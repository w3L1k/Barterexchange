from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.models import User

from .models import Complaint, DemoProfile, ExchangeRequest, Listing, Review


SCORE_CHOICES = [(value, '★' * value) for value in range(1, 6)]


class RegisterForm(UserCreationForm):
    name = forms.CharField(label='Имя', max_length=120)
    city = forms.CharField(label='Город', max_length=80)

    class Meta:
        model = User
        fields = ['username', 'name', 'city', 'password1', 'password2']
        labels = {
            'username': 'Логин',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].help_text = ''
        self.fields['password1'].label = 'Пароль'
        self.fields['password2'].label = 'Повторите пароль'
        self.fields['password1'].help_text = 'Минимум 8 символов. Не используйте слишком простой пароль.'
        self.fields['password2'].help_text = ''

    def save(self, commit=True):
        user = super().save(commit=commit)
        if commit:
            DemoProfile.objects.create(
                user=user,
                name=self.cleaned_data['name'],
                city=self.cleaned_data['city'],
                bio='Новый пользователь BarterExchange.',
            )
        return user


class LoginForm(AuthenticationForm):
    username = forms.CharField(label='Логин')
    password = forms.CharField(label='Пароль', widget=forms.PasswordInput)


class ProfileForm(forms.ModelForm):
    class Meta:
        model = DemoProfile
        fields = ['name', 'city', 'bio']
        labels = {
            'name': 'Имя',
            'city': 'Город',
            'bio': 'Описание профиля',
        }
        widgets = {
            'bio': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Расскажите, чем интересуетесь и что обычно ищете для обмена'}),
        }


class ListingForm(forms.ModelForm):
    photo = forms.ImageField(
        label='Фото товара',
        required=False,
        help_text='Можно загрузить фото для нового объявления.',
    )

    class Meta:
        model = Listing
        fields = [
            'title',
            'description',
            'category',
            'condition',
            'city',
            'exchange_terms',
            'desired_categories',
            'desired_keywords',
            'acceptable_city',
        ]
        labels = {
            'title': 'Название',
            'description': 'Описание',
            'category': 'Категория',
            'condition': 'Состояние',
            'city': 'Город',
            'exchange_terms': 'Условия обмена',
            'desired_categories': 'Какие категории рассматриваете взамен',
            'desired_keywords': 'Что хотите получить',
            'acceptable_city': 'Подходящий город',
        }
        help_texts = {
            'desired_keywords': 'Например: наушники, фантастика, гантели.',
            'acceptable_city': 'Оставьте город, где удобно провести обмен.',
        }
        widgets = {
            'title': forms.TextInput(attrs={'placeholder': 'Например: беспроводные наушники'}),
            'description': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Кратко опишите состояние и особенности товара'}),
            'city': forms.TextInput(attrs={'placeholder': 'Москва'}),
            'exchange_terms': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Без доплаты, самовывоз, встреча в городе и т.д.'}),
            'desired_keywords': forms.TextInput(attrs={'placeholder': 'Что хотите получить взамен'}),
            'acceptable_city': forms.TextInput(attrs={'placeholder': 'Москва'}),
            'desired_categories': forms.CheckboxSelectMultiple(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['category'].empty_label = 'Выберите категорию'
        self.fields['desired_categories'].required = True
        if self.instance and self.instance.pk and not self.instance.desired_categories.exists():
            self.initial['desired_categories'] = [self.instance.desired_category_id]


class ExchangeRequestForm(forms.ModelForm):
    class Meta:
        model = ExchangeRequest
        fields = ['offered_listing', 'initiator_contact']
        labels = {
            'initiator_contact': 'Ваш способ связи',
        }
        widgets = {
            'initiator_contact': forms.TextInput(attrs={'placeholder': 'Телефон, email или другой удобный контакт'}),
        }

    def __init__(self, *args, profile=None, requested_listing=None, **kwargs):
        super().__init__(*args, **kwargs)
        queryset = Listing.objects.filter(owner=profile, status=Listing.Status.ACTIVE)
        if requested_listing:
            queryset = queryset.exclude(pk=requested_listing.pk)
        self.fields['offered_listing'].queryset = queryset
        self.fields['offered_listing'].label = 'Что вы предлагаете'
        self.fields['initiator_contact'].required = True


class ExchangeAcceptForm(forms.ModelForm):
    class Meta:
        model = ExchangeRequest
        fields = ['receiver_contact']
        labels = {
            'receiver_contact': 'Ваш способ связи',
        }
        widgets = {
            'receiver_contact': forms.TextInput(attrs={'placeholder': 'Телефон, email или другой удобный контакт'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['receiver_contact'].required = True


class ProfileReviewForm(forms.ModelForm):
    exchange = forms.ModelChoiceField(label='Завершенный обмен', queryset=ExchangeRequest.objects.none())

    class Meta:
        model = Review
        fields = ['exchange', 'score', 'text']
        labels = {
            'score': 'Оценка',
            'text': 'Отзыв',
        }
        widgets = {
            'text': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Опишите, как прошел обмен'}),
        }

    def __init__(self, *args, author=None, target=None, **kwargs):
        super().__init__(*args, **kwargs)
        queryset = ExchangeRequest.objects.none()
        if author and target:
            reviewed_ids = Review.objects.filter(author=author, target=target).values_list('exchange_id', flat=True)
            queryset = ExchangeRequest.objects.filter(
                status=ExchangeRequest.Status.COMPLETED,
            ).filter(
                initiator__in=[author, target],
                receiver__in=[author, target],
            ).exclude(pk__in=reviewed_ids)
        self.fields['exchange'].queryset = queryset
        self.fields['score'].min_value = 1
        self.fields['score'].max_value = 5


class ExchangeReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['score', 'text']
        labels = {
            'score': 'Оценка',
            'text': 'Отзыв',
        }
        widgets = {
            'score': forms.RadioSelect(attrs={'class': 'star-rating'}, choices=SCORE_CHOICES),
            'text': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Напишите, как прошел обмен'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['score'].min_value = 1
        self.fields['score'].max_value = 5


class ComplaintForm(forms.ModelForm):
    LISTING_REASON_CHOICES = [
        (Complaint.Reason.WRONG_CATEGORY, 'Неверная категория'),
        (Complaint.Reason.WRONG_DESCRIPTION, 'Описание не соответствует товару'),
        (Complaint.Reason.FORBIDDEN, 'Запрещенный товар'),
        (Complaint.Reason.FRAUD, 'Подозрение на мошенничество'),
        (Complaint.Reason.OTHER, 'Другое'),
    ]
    PROFILE_REASON_CHOICES = [
        (Complaint.Reason.OFFENSIVE, 'Оскорбительное поведение'),
        (Complaint.Reason.FRAUD, 'Подозрение на мошенничество'),
        (Complaint.Reason.FAKE_PROFILE, 'Недостоверный профиль'),
        (Complaint.Reason.SPAM, 'Спам или навязчивые сообщения'),
        (Complaint.Reason.OTHER, 'Другое'),
    ]

    class Meta:
        model = Complaint
        fields = ['reason', 'comment']
        labels = {
            'reason': 'Причина жалобы',
            'comment': 'Комментарий',
        }
        widgets = {
            'comment': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Коротко опишите, что именно нужно проверить'}),
        }

    def __init__(self, *args, target_type='listing', **kwargs):
        super().__init__(*args, **kwargs)
        if target_type == 'profile':
            self.fields['reason'].choices = [('', 'Выберите причину')] + self.PROFILE_REASON_CHOICES
        else:
            self.fields['reason'].choices = [('', 'Выберите причину')] + self.LISTING_REASON_CHOICES
