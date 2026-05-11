from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User

from .models import Category, Complaint, DemoProfile, ExchangeRequest, Listing, ListingImage, Notification, Review
from .services import find_matches


class MatchingTests(TestCase):
    def setUp(self):
        self.tech = Category.objects.create(name='Техника', slug='tech')
        self.books = Category.objects.create(name='Книги', slug='books')
        self.games = Category.objects.create(name='Игры', slug='games')
        self.alex_user = User.objects.create_user(username='alex', password='demo12345')
        self.maria_user = User.objects.create_user(username='maria', password='demo12345')
        self.ivan_user = User.objects.create_user(username='ivan', password='demo12345')
        self.alex = DemoProfile.objects.create(user=self.alex_user, name='Алексей', city='Москва')
        self.maria = DemoProfile.objects.create(user=self.maria_user, name='Мария', city='Москва')
        self.ivan = DemoProfile.objects.create(user=self.ivan_user, name='Иван', city='Казань')

    def create_listing(self, owner, title, category, desired_category, keywords, city='Москва'):
        return Listing.objects.create(
            owner=owner,
            title=title,
            description=f'{title} в хорошем состоянии',
            category=category,
            condition=Listing.Condition.GOOD,
            city=city,
            desired_category=desired_category,
            desired_keywords=keywords,
            acceptable_city=city,
        )

    def test_find_matches_orders_by_category_and_city(self):
        source = self.create_listing(self.alex, 'Механическая клавиатура', self.tech, self.books, 'фантастика книги')
        category_and_city = self.create_listing(self.maria, 'Книги фантастика', self.books, self.tech, 'клавиатура техника')
        category_other_city = self.create_listing(self.ivan, 'Учебники Python', self.books, self.tech, 'клавиатура', city='Казань')
        city_other_category = self.create_listing(self.ivan, 'Настольная игра', self.games, self.books, 'книги')

        matches = find_matches(source)

        self.assertEqual([match.listing for match in matches], [category_and_city, category_other_city, city_other_category])
        self.assertEqual([match.priority for match in matches], [1, 2, 3])


class ExchangeFlowTests(TestCase):
    def setUp(self):
        self.tech = Category.objects.create(name='Техника', slug='tech')
        self.books = Category.objects.create(name='Книги', slug='books')
        self.alex_user = User.objects.create_user(username='alex', password='demo12345')
        self.maria_user = User.objects.create_user(username='maria', password='demo12345')
        self.ivan_user = User.objects.create_user(username='ivan', password='demo12345')
        self.alex = DemoProfile.objects.create(user=self.alex_user, name='Алексей', city='Москва')
        self.maria = DemoProfile.objects.create(user=self.maria_user, name='Мария', city='Москва')
        self.ivan = DemoProfile.objects.create(user=self.ivan_user, name='Иван', city='Москва')
        self.requested = self.listing(self.maria, 'Kindle', self.tech, self.books)
        self.offered_a = self.listing(self.alex, 'Книги фантастика', self.books, self.tech)
        self.offered_b = self.listing(self.ivan, 'Учебники Python', self.books, self.tech)

    def listing(self, owner, title, category, desired_category):
        return Listing.objects.create(
            owner=owner,
            title=title,
            description=title,
            category=category,
            condition=Listing.Condition.GOOD,
            city='Москва',
            desired_category=desired_category,
            desired_keywords='книги техника',
        )

    def test_accepting_exchange_rejects_other_pending_requests(self):
        accepted = ExchangeRequest.objects.create(
            initiator=self.alex,
            receiver=self.maria,
            offered_listing=self.offered_a,
            requested_listing=self.requested,
        )
        competing = ExchangeRequest.objects.create(
            initiator=self.ivan,
            receiver=self.maria,
            offered_listing=self.offered_b,
            requested_listing=self.requested,
        )
        self.client.force_login(self.maria_user)

        response = self.client.post(reverse('exchange_action', args=[accepted.pk, 'accept']))

        self.assertRedirects(response, reverse('my_profile'))
        accepted.refresh_from_db()
        competing.refresh_from_db()
        self.assertEqual(accepted.status, ExchangeRequest.Status.ACCEPTED)
        self.assertEqual(competing.status, ExchangeRequest.Status.REJECTED)

    def test_profile_shows_listings_and_completed_exchange_review_button(self):
        exchange = ExchangeRequest.objects.create(
            initiator=self.alex,
            receiver=self.maria,
            offered_listing=self.offered_a,
            requested_listing=self.requested,
            status=ExchangeRequest.Status.COMPLETED,
        )
        self.client.force_login(self.maria_user)

        response = self.client.get(reverse('profile_detail', args=[self.alex.pk]))

        self.assertContains(response, 'Книги фантастика')
        self.assertNotContains(response, 'Оставить отзыв')

        response = self.client.get(reverse('my_profile'))

        self.assertContains(response, 'Мои обмены')
        self.assertContains(response, 'Оставить отзыв')

        response = self.client.post(
            reverse('exchange_review', args=[exchange.pk]),
            {
                'score': 5,
                'text': 'Обмен прошел хорошо.',
            },
        )

        self.assertRedirects(response, reverse('my_profile'))
        self.assertTrue(Review.objects.filter(author=self.maria, target=self.alex, exchange=exchange).exists())

    def test_completing_exchange_redirects_to_review_form(self):
        exchange = ExchangeRequest.objects.create(
            initiator=self.alex,
            receiver=self.maria,
            offered_listing=self.offered_a,
            requested_listing=self.requested,
            status=ExchangeRequest.Status.ACCEPTED,
        )
        self.client.force_login(self.maria_user)

        response = self.client.post(reverse('exchange_action', args=[exchange.pk, 'complete']))

        self.assertRedirects(response, reverse('exchange_review', args=[exchange.pk]))

    def test_exchange_create_notifies_receiver(self):
        self.client.force_login(self.alex_user)

        response = self.client.post(
            reverse('exchange_create', args=[self.requested.pk]),
            {'offered_listing': self.offered_a.pk, 'comment': 'Предлагаю обмен'},
        )

        self.assertRedirects(response, reverse('my_profile'))
        self.assertTrue(Notification.objects.filter(profile=self.maria, text__contains='предлагает обмен').exists())

    def test_exchange_create_without_own_listings_prompts_to_create_listing(self):
        new_user = User.objects.create_user(username='newbie', password='demo12345')
        DemoProfile.objects.create(user=new_user, name='Новичок', city='Москва')
        self.client.force_login(new_user)

        response = self.client.get(reverse('exchange_create', args=[self.requested.pk]))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'exchange/exchange_no_listings.html')
        self.assertContains(response, 'Создать объявление')

    def test_accepted_exchange_moves_to_in_progress_column(self):
        exchange = ExchangeRequest.objects.create(
            initiator=self.alex,
            receiver=self.maria,
            offered_listing=self.offered_a,
            requested_listing=self.requested,
            status=ExchangeRequest.Status.ACCEPTED,
        )
        self.client.force_login(self.alex_user)

        response = self.client.get(reverse('my_profile'))

        self.assertContains(response, 'В процессе')
        self.assertContains(response, exchange.requested_listing.title)


class CatalogAndListingFormTests(TestCase):
    def setUp(self):
        self.tech = Category.objects.create(name='Техника', slug='tech')
        self.books = Category.objects.create(name='Книги', slug='books')
        self.user = User.objects.create_user(username='artem', password='demo12345')
        self.other_user = User.objects.create_user(username='maria', password='demo12345')
        self.profile = DemoProfile.objects.create(user=self.user, name='Артем', city='Москва')
        self.other_profile = DemoProfile.objects.create(user=self.other_user, name='Мария', city='Москва')
        Listing.objects.create(
            owner=self.other_profile,
            title='Беспроводные наушники',
            description='Наушники с шумоподавлением',
            category=self.tech,
            condition=Listing.Condition.GOOD,
            city='Москва',
            exchange_terms='Ищу книги или настольные игры',
            desired_category=self.books,
            desired_keywords='фантастика книги',
            acceptable_city='Москва',
        )

    def test_catalog_search_uses_title_only_case_insensitive(self):
        Listing.objects.create(
            owner=self.other_profile,
            title='Туристический рюкзак',
            description='Рюкзак для походов',
            category=self.tech,
            condition=Listing.Condition.GOOD,
            city='Москва',
            exchange_terms='Ищу гитару',
            desired_category=self.books,
            desired_keywords='гитара',
            acceptable_city='Москва',
        )

        self.client.force_login(self.user)
        response = self.client.get(reverse('catalog'), {'q': 'НАУШНИКИ'})

        self.assertContains(response, 'Беспроводные наушники')
        self.assertNotContains(response, 'Туристический рюкзак')

    def test_guest_can_open_catalog_and_listing(self):
        listing = Listing.objects.get(title='Беспроводные наушники')

        catalog_response = self.client.get(reverse('catalog'))
        detail_response = self.client.get(reverse('listing_detail', args=[listing.pk]))

        self.assertEqual(catalog_response.status_code, 200)
        self.assertEqual(detail_response.status_code, 200)
        self.assertContains(catalog_response, 'Предложить обмен')
        self.assertContains(detail_response, reverse('login'))

    def test_archived_listing_is_hidden_from_guest_and_other_user(self):
        listing = Listing.objects.get(title='Беспроводные наушники')
        listing.status = Listing.Status.ARCHIVED
        listing.save(update_fields=['status'])

        guest_response = self.client.get(reverse('listing_detail', args=[listing.pk]))
        self.client.force_login(self.user)
        user_response = self.client.get(reverse('listing_detail', args=[listing.pk]))
        self.client.force_login(self.other_user)
        owner_response = self.client.get(reverse('listing_detail', args=[listing.pk]))

        self.assertEqual(guest_response.status_code, 404)
        self.assertEqual(user_response.status_code, 404)
        self.assertEqual(owner_response.status_code, 200)

    def test_blocked_listing_is_hidden_from_guest_and_other_user(self):
        listing = Listing.objects.get(title='Беспроводные наушники')
        listing.status = Listing.Status.BLOCKED
        listing.save(update_fields=['status'])

        guest_response = self.client.get(reverse('listing_detail', args=[listing.pk]))
        self.client.force_login(self.user)
        user_response = self.client.get(reverse('listing_detail', args=[listing.pk]))
        self.client.force_login(self.other_user)
        owner_response = self.client.get(reverse('listing_detail', args=[listing.pk]))

        self.assertEqual(guest_response.status_code, 404)
        self.assertEqual(user_response.status_code, 404)
        self.assertEqual(owner_response.status_code, 200)

    def test_user_can_complain_about_listing_and_profile(self):
        listing = Listing.objects.get(title='Беспроводные наушники')
        self.client.force_login(self.user)

        listing_response = self.client.post(
            reverse('listing_complaint', args=[listing.pk]),
            {'reason': Complaint.Reason.FRAUD, 'comment': 'Проверьте объявление'},
        )
        profile_response = self.client.post(
            reverse('profile_complaint', args=[self.other_profile.pk]),
            {'reason': Complaint.Reason.OFFENSIVE, 'comment': 'Проверьте профиль'},
        )

        self.assertRedirects(listing_response, reverse('listing_detail', args=[listing.pk]))
        self.assertRedirects(profile_response, reverse('profile_detail', args=[self.other_profile.pk]))
        self.assertTrue(Complaint.objects.filter(reporter=self.profile, listing=listing).exists())
        self.assertTrue(Complaint.objects.filter(reporter=self.profile, target_profile=self.other_profile, listing__isnull=True).exists())

    def test_user_cannot_complain_about_own_listing_or_profile(self):
        listing = Listing.objects.create(
            owner=self.profile,
            title='Мой товар для жалобы',
            description='На свой товар жаловаться нельзя',
            category=self.tech,
            condition=Listing.Condition.GOOD,
            city='Москва',
            exchange_terms='',
            desired_category=self.books,
            desired_keywords='книги',
            acceptable_city='Москва',
        )
        self.client.force_login(self.user)

        listing_response = self.client.post(
            reverse('listing_complaint', args=[listing.pk]),
            {'reason': Complaint.Reason.OTHER, 'comment': 'Сам на себя'},
        )
        profile_response = self.client.post(
            reverse('profile_complaint', args=[self.profile.pk]),
            {'reason': Complaint.Reason.OTHER, 'comment': 'Сам на себя'},
        )

        self.assertRedirects(listing_response, reverse('listing_detail', args=[listing.pk]))
        self.assertRedirects(profile_response, reverse('my_profile'))
        self.assertFalse(Complaint.objects.filter(reporter=self.profile).exists())

    def test_catalog_hides_current_profile_listings(self):
        own_listing = Listing.objects.create(
            owner=self.profile,
            title='Мой товар',
            description='Не должен быть в каталоге',
            category=self.tech,
            condition=Listing.Condition.GOOD,
            city='Москва',
            exchange_terms='',
            desired_category=self.books,
            desired_keywords='книги',
            acceptable_city='Москва',
        )
        Listing.objects.create(
            owner=self.other_profile,
            title='Чужой товар',
            description='Должен быть в каталоге',
            category=self.tech,
            condition=Listing.Condition.GOOD,
            city='Москва',
            exchange_terms='',
            desired_category=self.books,
            desired_keywords='книги',
            acceptable_city='Москва',
        )

        self.client.force_login(self.user)
        response = self.client.get(reverse('catalog'))

        self.assertNotContains(response, own_listing.title)
        self.assertContains(response, 'Чужой товар')
        self.assertContains(response, 'Предложить обмен')

    def test_listing_create_accepts_uploaded_photo(self):
        self.client.force_login(self.user)
        image = SimpleUploadedFile(
            'photo.gif',
            b'GIF87a\x01\x00\x01\x00\x80\x01\x00\x00\x00\x00ccc,\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02D\x01\x00;',
            content_type='image/gif',
        )

        response = self.client.post(
            reverse('listing_create'),
            {
                'title': 'Настольная лампа',
                'description': 'Рабочая лампа для стола',
                'category': self.tech.pk,
                'condition': Listing.Condition.GOOD,
                'city': 'Москва',
                'exchange_terms': 'Обмен по договоренности',
                'desired_category': self.books.pk,
                'desired_keywords': 'книги',
                'acceptable_city': 'Москва',
                'photo': image,
            },
        )

        self.assertEqual(response.status_code, 302)
        listing = Listing.objects.get(title='Настольная лампа')
        self.assertTrue(ListingImage.objects.filter(listing=listing).exists())

    def test_owner_can_delete_listing_without_active_exchange(self):
        listing = Listing.objects.create(
            owner=self.profile,
            title='Удаляемый товар',
            description='Можно удалить',
            category=self.tech,
            condition=Listing.Condition.GOOD,
            city='Москва',
            exchange_terms='',
            desired_category=self.books,
            desired_keywords='книги',
            acceptable_city='Москва',
        )
        self.client.force_login(self.user)

        response = self.client.post(reverse('listing_delete', args=[listing.pk]))

        self.assertRedirects(response, reverse('my_profile'))
        self.assertFalse(Listing.objects.filter(pk=listing.pk).exists())

    def test_owner_cannot_edit_archive_or_delete_listing_with_active_exchange(self):
        listing = Listing.objects.create(
            owner=self.profile,
            title='Товар со сделкой',
            description='Нельзя менять',
            category=self.tech,
            condition=Listing.Condition.GOOD,
            city='Москва',
            exchange_terms='',
            desired_category=self.books,
            desired_keywords='книги',
            acceptable_city='Москва',
        )
        offered = Listing.objects.create(
            owner=self.other_profile,
            title='Предложенный товар',
            description='Активная сделка',
            category=self.books,
            condition=Listing.Condition.GOOD,
            city='Москва',
            exchange_terms='',
            desired_category=self.tech,
            desired_keywords='техника',
            acceptable_city='Москва',
        )
        ExchangeRequest.objects.create(
            initiator=self.other_profile,
            receiver=self.profile,
            offered_listing=offered,
            requested_listing=listing,
            status=ExchangeRequest.Status.PENDING,
        )
        self.client.force_login(self.user)

        edit_response = self.client.get(reverse('listing_edit', args=[listing.pk]))
        archive_response = self.client.post(reverse('listing_archive', args=[listing.pk]))
        delete_response = self.client.post(reverse('listing_delete', args=[listing.pk]))
        listing.refresh_from_db()

        self.assertRedirects(edit_response, reverse('listing_detail', args=[listing.pk]))
        self.assertRedirects(archive_response, reverse('listing_detail', args=[listing.pk]))
        self.assertRedirects(delete_response, reverse('listing_detail', args=[listing.pk]))
        self.assertEqual(listing.status, Listing.Status.ACTIVE)
        self.assertTrue(Listing.objects.filter(pk=listing.pk).exists())
