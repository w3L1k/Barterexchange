from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.http import require_POST

from .forms import (
    ComplaintForm,
    ExchangeAcceptForm,
    ExchangeRequestForm,
    ExchangeReviewForm,
    ListingForm,
    LoginForm,
    ProfileForm,
    RegisterForm,
)
from .models import Complaint, DemoProfile, ExchangeRequest, Favorite, Listing, ListingImage, Notification, Review
from .services import find_matches, group_matches


def get_current_profile(request):
    if not request.user.is_authenticated:
        return None
    profile, _created = DemoProfile.objects.get_or_create(
        user=request.user,
        defaults={
            'name': request.user.get_username(),
            'city': 'Москва',
            'bio': 'Новый пользователь BarterExchange.',
        },
    )
    return profile


def common_context(request):
    profile = get_current_profile(request)
    return {
        'current_profile': profile,
        'unread_notifications_count': (
            Notification.objects.filter(profile=profile, is_read=False).count() if profile else 0
        ),
    }


def notify(profile, text, url=''):
    Notification.objects.create(profile=profile, text=text, url=url)


def sync_legacy_desired_category(listing, form):
    desired_categories = list(form.cleaned_data['desired_categories'])
    if desired_categories:
        listing.desired_category = desired_categories[0]


def listing_has_active_exchange(listing):
    active_statuses = [ExchangeRequest.Status.PENDING, ExchangeRequest.Status.ACCEPTED]
    return ExchangeRequest.objects.filter(
        Q(offered_listing=listing) | Q(requested_listing=listing),
        status__in=active_statuses,
    ).exists()


def get_review_target(exchange, profile):
    if exchange.initiator == profile:
        return exchange.receiver
    if exchange.receiver == profile:
        return exchange.initiator
    return None


def add_review_state(exchanges, profile):
    for exchange in exchanges:
        target = get_review_target(exchange, profile)
        exchange.review_target = target
        exchange.can_review = bool(
            target
            and exchange.status == ExchangeRequest.Status.COMPLETED
            and not Review.objects.filter(exchange=exchange, author=profile, target=target).exists()
        )
    return exchanges


def get_exchange_columns(profile):
    incoming = ExchangeRequest.objects.select_related(
        'initiator', 'receiver', 'offered_listing', 'requested_listing'
    ).filter(receiver=profile, status=ExchangeRequest.Status.PENDING)
    outgoing = ExchangeRequest.objects.select_related(
        'initiator', 'receiver', 'offered_listing', 'requested_listing'
    ).filter(initiator=profile, status=ExchangeRequest.Status.PENDING)
    in_progress = ExchangeRequest.objects.select_related(
        'initiator', 'receiver', 'offered_listing', 'requested_listing'
    ).filter(
        Q(initiator=profile) | Q(receiver=profile),
        status=ExchangeRequest.Status.ACCEPTED,
    )
    completed = ExchangeRequest.objects.select_related(
        'initiator', 'receiver', 'offered_listing', 'requested_listing'
    ).filter(
        Q(initiator=profile) | Q(receiver=profile),
        status=ExchangeRequest.Status.COMPLETED,
    )
    return incoming, outgoing, in_progress, add_review_state(completed, profile)


def login_view(request):
    if request.user.is_authenticated:
        return redirect('catalog')
    form = LoginForm(request, data=request.POST or None)
    if request.method == 'POST' and form.is_valid():
        login(request, form.get_user())
        messages.success(request, 'Вы вошли в аккаунт.')
        return redirect(request.GET.get('next') or 'catalog')
    if request.method == 'POST':
        messages.error(request, 'Неверный логин или пароль.')
    demo_users = ['artem', 'maria', 'ilya', 'sofia', 'nikita', 'elena', 'daniil', 'alina']
    return render(request, 'exchange/login.html', {'form': form, 'demo_users': demo_users})


@require_POST
def demo_login_view(request):
    if request.user.is_authenticated:
        return redirect('catalog')
    username = request.POST.get('username')
    allowed_users = {'artem', 'maria', 'ilya', 'sofia', 'nikita', 'elena', 'daniil', 'alina'}
    if username not in allowed_users:
        messages.error(request, 'Такого демо-аккаунта нет.')
        return redirect('login')
    user = authenticate(request, username=username, password='demo12345')
    if not user:
        messages.error(request, 'Демо-аккаунты не найдены. Запустите seed_demo.')
        return redirect('login')
    login(request, user)
    messages.success(request, f'Вы вошли как {username}.')
    return redirect('catalog')


def register_view(request):
    if request.user.is_authenticated:
        return redirect('catalog')
    form = RegisterForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.save()
        login(request, user)
        messages.success(request, 'Аккаунт создан. Теперь можно добавлять объявления.')
        return redirect('catalog')
    return render(request, 'exchange/register.html', {'form': form})


@require_POST
def logout_view(request):
    logout(request)
    messages.success(request, 'Вы вышли из аккаунта.')
    return redirect('login')


def catalog(request):
    profile = get_current_profile(request)
    listings = (
        Listing.objects.select_related('owner', 'category', 'desired_category')
        .prefetch_related('images', 'desired_categories')
        .filter(status=Listing.Status.ACTIVE)
    )
    if profile:
        listings = listings.exclude(owner=profile)
    query = request.GET.get('q', '').strip()
    category = request.GET.get('category', '').strip()
    city = request.GET.get('city', '').strip()
    condition = request.GET.get('condition', '').strip()
    sort = request.GET.get('sort', '-created_at')

    if query:
        normalized_query = query.casefold()
        matching_ids = [
            listing.pk
            for listing in listings
            if normalized_query in listing.title.casefold()
        ]
        listings = listings.filter(pk__in=matching_ids)
    if category:
        listings = listings.filter(category__slug=category)
    if city:
        listings = listings.filter(city__iexact=city)
    if condition:
        listings = listings.filter(condition=condition)

    sort_map = {
        '-created_at': '-created_at',
        'title': 'title',
    }
    listings = listings.order_by(sort_map.get(sort, '-created_at'))

    context = common_context(request)
    context.update(
        {
            'listings': listings,
            'categories': Listing._meta.get_field('category').remote_field.model.objects.all(),
            'cities': Listing.objects.order_by('city').values_list('city', flat=True).distinct(),
            'conditions': Listing.Condition.choices,
            'filters': {'q': query, 'category': category, 'city': city, 'condition': condition, 'sort': sort},
        }
    )
    return render(request, 'exchange/catalog.html', context)


@login_required
def profile_detail(request, pk=None):
    current_profile = get_current_profile(request)
    profile = current_profile if pk is None else get_object_or_404(DemoProfile, pk=pk)
    listings = (
        Listing.objects.select_related('category', 'desired_category')
        .prefetch_related('images', 'desired_categories')
        .filter(owner=profile)
    )
    reviews = Review.objects.select_related(
        'author',
        'exchange',
        'exchange__offered_listing',
        'exchange__requested_listing',
    ).filter(target=profile)
    average_score = None
    if reviews:
        average_score = round(sum(review.score for review in reviews) / len(reviews), 1)
    incoming = outgoing = in_progress = completed = None
    if current_profile == profile:
        incoming, outgoing, in_progress, completed = get_exchange_columns(current_profile)

    context = common_context(request)
    context.update(
        {
            'profile': profile,
            'listings': listings,
            'reviews': reviews,
            'average_score': average_score,
            'review_count': reviews.count(),
            'is_own_profile': current_profile == profile,
            'incoming': incoming,
            'outgoing': outgoing,
            'in_progress': in_progress,
            'completed': completed,
        }
    )
    return render(request, 'exchange/profile_detail.html', context)


def listing_detail(request, pk):
    listing = get_object_or_404(
        Listing.objects.select_related('owner', 'category', 'desired_category').prefetch_related(
            'images', 'desired_categories'
        ),
        pk=pk,
    )
    context = common_context(request)
    current_profile = context['current_profile']
    if listing.status != Listing.Status.ACTIVE and listing.owner != current_profile:
        raise Http404
    matches = find_matches(listing, limit=12) if listing.status == Listing.Status.ACTIVE else []
    context.update(
        {
            'listing': listing,
            'match_groups': group_matches(matches),
            'is_favorite': (
                Favorite.objects.filter(profile=current_profile, listing=listing).exists()
                if current_profile and current_profile != listing.owner
                else False
            ),
            'has_active_exchange': listing_has_active_exchange(listing),
        }
    )
    return render(request, 'exchange/listing_detail.html', context)


def listing_matches(request, pk):
    listing = get_object_or_404(
        Listing.objects.select_related('owner', 'category', 'desired_category').prefetch_related(
            'images', 'desired_categories'
        ),
        pk=pk,
    )
    context = common_context(request)
    context.update({'listing': listing, 'match_groups': group_matches(find_matches(listing, limit=48))})
    return render(request, 'exchange/listing_matches.html', context)


@login_required
def listing_create(request):
    profile = get_current_profile(request)
    if not profile:
        messages.error(request, 'Сначала войдите или зарегистрируйтесь.')
        return redirect('login')
    if request.method == 'POST':
        form = ListingForm(request.POST, request.FILES)
        if form.is_valid():
            listing = form.save(commit=False)
            listing.owner = profile
            sync_legacy_desired_category(listing, form)
            listing.save()
            form.save_m2m()
            photo = form.cleaned_data.get('photo')
            if photo:
                ListingImage.objects.create(listing=listing, image=photo, alt_text=listing.title)
            messages.success(request, 'Объявление создано.')
            return redirect(listing)
    else:
        form = ListingForm(initial={'city': profile.city, 'acceptable_city': profile.city})
    context = common_context(request)
    context.update({'form': form})
    return render(request, 'exchange/listing_form.html', context)


@login_required
def profile_edit(request):
    profile = get_current_profile(request)
    form = ProfileForm(request.POST or None, instance=profile)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Профиль обновлен.')
        return redirect('my_profile')
    context = common_context(request)
    context.update({'form': form})
    return render(request, 'exchange/profile_form.html', context)


@login_required
def listing_edit(request, pk):
    profile = get_current_profile(request)
    listing = get_object_or_404(Listing, pk=pk, owner=profile)
    if listing_has_active_exchange(listing):
        messages.error(request, 'Нельзя редактировать объявление, пока по нему есть ожидающий или принятый обмен.')
        return redirect(listing)
    if request.method == 'POST':
        form = ListingForm(request.POST, request.FILES, instance=listing)
        if form.is_valid():
            listing = form.save(commit=False)
            sync_legacy_desired_category(listing, form)
            listing.save()
            form.save_m2m()
            photo = form.cleaned_data.get('photo')
            if photo:
                listing.images.all().delete()
                listing.external_image_url = ''
                listing.save(update_fields=['external_image_url'])
                ListingImage.objects.create(listing=listing, image=photo, alt_text=listing.title)
            messages.success(request, 'Объявление обновлено.')
            return redirect(listing)
    else:
        form = ListingForm(instance=listing)
    context = common_context(request)
    context.update({'form': form, 'listing': listing})
    return render(request, 'exchange/listing_form.html', context)


@login_required
def favorites(request):
    profile = get_current_profile(request)
    items = (
        Favorite.objects.select_related('listing', 'listing__owner', 'listing__category', 'listing__desired_category')
        .prefetch_related('listing__images', 'listing__desired_categories')
        .filter(profile=profile)
    )
    context = common_context(request)
    context.update({'favorites': items})
    return render(request, 'exchange/favorites.html', context)


@require_POST
@login_required
def favorite_toggle(request, pk):
    profile = get_current_profile(request)
    listing = get_object_or_404(Listing, pk=pk, status=Listing.Status.ACTIVE)
    next_url = request.POST.get('next') or listing.get_absolute_url()
    if listing.owner == profile:
        messages.error(request, 'Нельзя добавить свое объявление в избранное.')
        return redirect(next_url)
    favorite = Favorite.objects.filter(profile=profile, listing=listing).first()
    if favorite:
        favorite.delete()
        messages.success(request, 'Объявление удалено из избранного.')
    else:
        Favorite.objects.create(profile=profile, listing=listing)
        messages.success(request, 'Объявление добавлено в избранное.')
    return redirect(next_url)


@require_POST
@login_required
def listing_archive(request, pk):
    profile = get_current_profile(request)
    listing = get_object_or_404(Listing, pk=pk, owner=profile)
    if listing_has_active_exchange(listing):
        messages.error(request, 'Нельзя архивировать объявление, пока по нему есть ожидающий или принятый обмен.')
        return redirect(listing)
    listing.status = Listing.Status.ARCHIVED
    listing.save(update_fields=['status', 'updated_at'])
    messages.success(request, 'Объявление перенесено в архив.')
    return redirect('my_profile')


@require_POST
@login_required
def listing_delete(request, pk):
    profile = get_current_profile(request)
    listing = get_object_or_404(Listing, pk=pk, owner=profile)
    if listing_has_active_exchange(listing):
        messages.error(request, 'Нельзя удалить объявление, пока по нему есть ожидающий или принятый обмен.')
        return redirect(listing)
    listing.delete()
    messages.success(request, 'Объявление удалено.')
    return redirect('my_profile')


@login_required
def listing_complaint(request, pk):
    profile = get_current_profile(request)
    listing = get_object_or_404(
        Listing.objects.select_related('owner', 'category'),
        pk=pk,
        status=Listing.Status.ACTIVE,
    )
    if listing.owner == profile:
        messages.error(request, 'Нельзя пожаловаться на свое объявление.')
        return redirect(listing)

    complaint_instance = Complaint(reporter=profile, listing=listing, target_profile=listing.owner)
    form = ComplaintForm(request.POST or None, instance=complaint_instance, target_type='listing')
    if request.method == 'POST' and form.is_valid():
        complaint = form.save(commit=False)
        complaint.save()
        messages.success(request, 'Жалоба отправлена. Модератор проверит объявление.')
        return redirect(listing)

    context = common_context(request)
    context.update(
        {
            'form': form,
            'target_title': listing.title,
            'target_subtitle': f'Объявление · {listing.owner.name}',
            'cancel_url': listing.get_absolute_url(),
        }
    )
    return render(request, 'exchange/complaint_form.html', context)


@login_required
def profile_complaint(request, pk):
    profile = get_current_profile(request)
    target_profile = get_object_or_404(DemoProfile, pk=pk)
    if target_profile == profile:
        messages.error(request, 'Нельзя пожаловаться на свой профиль.')
        return redirect('my_profile')

    complaint_instance = Complaint(reporter=profile, target_profile=target_profile)
    form = ComplaintForm(request.POST or None, instance=complaint_instance, target_type='profile')
    if request.method == 'POST' and form.is_valid():
        complaint = form.save(commit=False)
        complaint.save()
        messages.success(request, 'Жалоба отправлена. Модератор проверит профиль.')
        return redirect('profile_detail', pk=target_profile.pk)

    context = common_context(request)
    context.update(
        {
            'form': form,
            'target_title': target_profile.name,
            'target_subtitle': f'Профиль · {target_profile.city}',
            'cancel_url': reverse('profile_detail', args=[target_profile.pk]),
        }
    )
    return render(request, 'exchange/complaint_form.html', context)


@login_required
def exchange_create(request, pk):
    requested_listing = get_object_or_404(Listing, pk=pk, status=Listing.Status.ACTIVE)
    profile = get_current_profile(request)
    if requested_listing.owner == profile:
        messages.error(request, 'Нельзя предложить обмен самому себе.')
        return redirect(requested_listing)
    if ExchangeRequest.objects.filter(
        requested_listing=requested_listing,
        status=ExchangeRequest.Status.ACCEPTED,
    ).exists():
        messages.error(request, 'По этому объявлению уже есть принятый обмен.')
        return redirect(requested_listing)

    own_listings = Listing.objects.filter(owner=profile, status=Listing.Status.ACTIVE).exclude(pk=requested_listing.pk)
    if not own_listings.exists():
        context = common_context(request)
        context.update({'requested_listing': requested_listing})
        return render(request, 'exchange/exchange_no_listings.html', context)

    if request.method == 'POST':
        form = ExchangeRequestForm(request.POST, profile=profile, requested_listing=requested_listing)
        if form.is_valid():
            exchange = form.save(commit=False)
            exchange.initiator = profile
            exchange.receiver = requested_listing.owner
            exchange.requested_listing = requested_listing
            if exchange.offered_listing.owner != profile:
                messages.error(request, 'Можно предложить только свое объявление.')
                return redirect(requested_listing)
            exchange.save()
            notify(
                exchange.receiver,
                f'{profile.name} предлагает обмен на «{requested_listing.title}».',
                '/profile/',
            )
            messages.success(request, 'Предложение обмена отправлено.')
            return redirect('my_profile')
    else:
        form = ExchangeRequestForm(profile=profile, requested_listing=requested_listing)

    context = common_context(request)
    context.update({'form': form, 'requested_listing': requested_listing})
    return render(request, 'exchange/exchange_form.html', context)


@login_required
def exchange_dashboard(request):
    profile = get_current_profile(request)
    incoming, outgoing, in_progress, completed = get_exchange_columns(profile)
    context = common_context(request)
    context.update({'incoming': incoming, 'outgoing': outgoing, 'in_progress': in_progress, 'completed': completed})
    return render(request, 'exchange/exchange_dashboard.html', context)


@login_required
def exchange_accept(request, pk):
    profile = get_current_profile(request)
    exchange = get_object_or_404(
        ExchangeRequest.objects.select_related('initiator', 'receiver', 'offered_listing', 'requested_listing'),
        pk=pk,
        receiver=profile,
        status=ExchangeRequest.Status.PENDING,
    )
    form = ExchangeAcceptForm(request.POST or None, instance=exchange)
    if request.method == 'POST' and form.is_valid():
        exchange = form.save(commit=False)
        exchange.status = ExchangeRequest.Status.ACCEPTED
        exchange.save(update_fields=['receiver_contact', 'status', 'updated_at'])
        ExchangeRequest.objects.filter(
            requested_listing=exchange.requested_listing,
            status=ExchangeRequest.Status.PENDING,
        ).exclude(pk=exchange.pk).update(status=ExchangeRequest.Status.REJECTED)
        notify(
            exchange.initiator,
            f'Ваш обмен «{exchange.offered_listing.title} → {exchange.requested_listing.title}» принят.',
            '/profile/',
        )
        messages.success(request, 'Обмен принят. Теперь у обеих сторон есть способы связи.')
        return redirect('my_profile')

    context = common_context(request)
    context.update({'form': form, 'exchange': exchange})
    return render(request, 'exchange/exchange_accept.html', context)


@login_required
def exchange_review(request, pk):
    profile = get_current_profile(request)
    exchange = get_object_or_404(
        ExchangeRequest.objects.select_related('initiator', 'receiver', 'offered_listing', 'requested_listing'),
        pk=pk,
        status=ExchangeRequest.Status.COMPLETED,
    )
    target = get_review_target(exchange, profile)
    if not target:
        messages.error(request, 'Этот обмен принадлежит другим профилям.')
        return redirect('my_profile')
    if Review.objects.filter(exchange=exchange, author=profile, target=target).exists():
        messages.info(request, 'Вы уже оставили отзыв по этому обмену.')
        return redirect('my_profile')

    form = ExchangeReviewForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        review = form.save(commit=False)
        review.exchange = exchange
        review.author = profile
        review.target = target
        review.save()
        notify(target, f'{profile.name} оставил отзыв после обмена.', '/profile/')
        messages.success(request, 'Отзыв добавлен.')
        return redirect('my_profile')

    context = common_context(request)
    context.update({'form': form, 'exchange': exchange, 'target': target, 'score_values': range(1, 6)})
    return render(request, 'exchange/exchange_review.html', context)


@require_POST
@login_required
def exchange_action(request, pk, action):
    profile = get_current_profile(request)
    exchange = get_object_or_404(ExchangeRequest, pk=pk)
    if profile not in [exchange.initiator, exchange.receiver]:
        messages.error(request, 'Это предложение обмена принадлежит другим профилям.')
        return redirect('exchange_dashboard')

    if action == 'accept' and profile == exchange.receiver and exchange.status == ExchangeRequest.Status.PENDING:
        return redirect('exchange_accept', pk=exchange.pk)
    elif action == 'reject' and profile == exchange.receiver and exchange.status == ExchangeRequest.Status.PENDING:
        exchange.status = ExchangeRequest.Status.REJECTED
        exchange.save(update_fields=['status', 'updated_at'])
        notify(exchange.initiator, f'Ваш обмен «{exchange.offered_listing.title} → {exchange.requested_listing.title}» отклонен.', '/profile/')
        messages.success(request, 'Предложение отклонено.')
    elif action == 'cancel' and exchange.status in [ExchangeRequest.Status.PENDING, ExchangeRequest.Status.ACCEPTED]:
        exchange.status = ExchangeRequest.Status.CANCELLED
        exchange.save(update_fields=['status', 'updated_at'])
        messages.success(request, 'Обмен отменен.')
    elif action == 'complete' and exchange.status == ExchangeRequest.Status.ACCEPTED:
        exchange.status = ExchangeRequest.Status.COMPLETED
        exchange.save(update_fields=['status', 'updated_at'])
        other = exchange.receiver if profile == exchange.initiator else exchange.initiator
        notify(other, f'Обмен «{exchange.offered_listing.title} → {exchange.requested_listing.title}» завершен и ожидает оценки.', '/profile/')
        messages.success(request, 'Обмен завершен.')
        return redirect('exchange_review', pk=exchange.pk)
    else:
        messages.error(request, 'Действие недоступно для текущего статуса.')
    return redirect('my_profile')


@login_required
def notifications(request):
    profile = get_current_profile(request)
    items = Notification.objects.filter(profile=profile)
    items.filter(is_read=False).update(is_read=True)
    context = common_context(request)
    context.update({'notifications': items})
    return render(request, 'exchange/notifications.html', context)
