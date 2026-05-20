from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.urls import reverse


class DemoProfile(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='demo_profile',
        null=True,
        blank=True,
        verbose_name='Пользователь',
    )
    name = models.CharField('Имя', max_length=120)
    city = models.CharField('Город', max_length=80)
    bio = models.TextField('Описание', blank=True)
    rating = models.DecimalField('Рейтинг', max_digits=3, decimal_places=2, default=0)
    created_at = models.DateTimeField('Дата создания', auto_now_add=True)

    class Meta:
        ordering = ['name']
        verbose_name = 'Профиль'
        verbose_name_plural = 'Профили'

    def __str__(self):
        return self.name


class Category(models.Model):
    name = models.CharField('Название', max_length=80, unique=True)
    slug = models.SlugField('Слаг', max_length=90, unique=True)

    class Meta:
        ordering = ['name']
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'

    def __str__(self):
        return self.name


class Listing(models.Model):
    class Condition(models.TextChoices):
        NEW = 'new', 'Новое'
        LIKE_NEW = 'excellent', 'Как новое'
        GOOD = 'good', 'Хорошее'
        USED = 'fair', 'Есть следы использования'
        NEEDS_REPAIR = 'needs_repair', 'Требует ремонта'

    class Status(models.TextChoices):
        ACTIVE = 'active', 'Активно'
        IN_DEAL = 'in_deal', 'В обмене'
        ARCHIVED = 'archived', 'В архиве'
        BLOCKED = 'blocked', 'Заблокировано'

    owner = models.ForeignKey(DemoProfile, on_delete=models.CASCADE, related_name='listings', verbose_name='Владелец')
    title = models.CharField('Название', max_length=160)
    description = models.TextField('Описание')
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name='listings', verbose_name='Категория')
    condition = models.CharField('Состояние', max_length=20, choices=Condition.choices, default=Condition.GOOD)
    city = models.CharField('Город', max_length=80)
    exchange_terms = models.TextField('Условия обмена', blank=True)
    external_image_url = models.URLField('Внешняя ссылка на изображение', blank=True)
    desired_category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name='desired_by_listings',
        verbose_name='Желаемая категория',
    )
    desired_categories = models.ManyToManyField(
        Category,
        related_name='desired_by_multiple_listings',
        verbose_name='Желаемые категории',
        blank=True,
    )
    desired_keywords = models.CharField(
        'Что хочет получить',
        max_length=220,
        help_text='Что пользователь хочет получить: слова через запятую или короткая фраза',
    )
    acceptable_city = models.CharField('Подходящий город', max_length=80, blank=True)
    status = models.CharField('Статус', max_length=20, choices=Status.choices, default=Status.ACTIVE)
    created_at = models.DateTimeField('Дата создания', auto_now_add=True)
    updated_at = models.DateTimeField('Дата обновления', auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Объявление'
        verbose_name_plural = 'Объявления'

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('listing_detail', args=[self.pk])

    @property
    def primary_image_url(self):
        image = self.images.first()
        if image and image.image:
            return image.image.url
        return self.external_image_url

    @property
    def desired_categories_display(self):
        categories = list(self.desired_categories.all())
        if categories:
            return ', '.join(category.name for category in categories)
        return self.desired_category.name


class Favorite(models.Model):
    profile = models.ForeignKey(DemoProfile, on_delete=models.CASCADE, related_name='favorites', verbose_name='Профиль')
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name='favorited_by', verbose_name='Объявление')
    created_at = models.DateTimeField('Дата добавления', auto_now_add=True)

    class Meta:
        unique_together = [('profile', 'listing')]
        ordering = ['-created_at']
        verbose_name = 'Избранное объявление'
        verbose_name_plural = 'Избранные объявления'

    def __str__(self):
        return f'{self.profile} сохранил {self.listing}'


class ListingImage(models.Model):
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name='images', verbose_name='Объявление')
    image = models.ImageField('Изображение', upload_to='listings/')
    alt_text = models.CharField('Описание изображения', max_length=160, blank=True)

    class Meta:
        verbose_name = 'Изображение объявления'
        verbose_name_plural = 'Изображения объявлений'

    def __str__(self):
        return self.alt_text or self.listing.title


class ExchangeRequest(models.Model):
    class Status(models.TextChoices):
        PENDING = 'pending', 'Ожидает ответа'
        ACCEPTED = 'accepted', 'Принята'
        REJECTED = 'rejected', 'Отклонена'
        CANCELLED = 'cancelled', 'Отменена'
        COMPLETED = 'completed', 'Завершена'

    initiator = models.ForeignKey(DemoProfile, on_delete=models.CASCADE, related_name='outgoing_requests', verbose_name='Инициатор')
    receiver = models.ForeignKey(DemoProfile, on_delete=models.CASCADE, related_name='incoming_requests', verbose_name='Получатель')
    offered_listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name='offered_in_requests', verbose_name='Предлагаемое объявление')
    requested_listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name='requested_in_requests', verbose_name='Запрошенное объявление')
    comment = models.TextField('Комментарий', blank=True)
    initiator_contact = models.CharField('Способ связи инициатора', max_length=220, blank=True)
    receiver_contact = models.CharField('Способ связи получателя', max_length=220, blank=True)
    status = models.CharField('Статус', max_length=20, choices=Status.choices, default=Status.PENDING)
    created_at = models.DateTimeField('Дата создания', auto_now_add=True)
    updated_at = models.DateTimeField('Дата обновления', auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Предложение обмена'
        verbose_name_plural = 'Предложения обмена'

    def __str__(self):
        return f'{self.offered_listing} -> {self.requested_listing}'


class Review(models.Model):
    exchange = models.ForeignKey(ExchangeRequest, on_delete=models.CASCADE, related_name='reviews', verbose_name='Обмен')
    author = models.ForeignKey(DemoProfile, on_delete=models.CASCADE, related_name='reviews_written', verbose_name='Автор')
    target = models.ForeignKey(DemoProfile, on_delete=models.CASCADE, related_name='reviews_received', verbose_name='Получатель отзыва')
    score = models.PositiveSmallIntegerField('Оценка', validators=[MinValueValidator(1), MaxValueValidator(5)])
    text = models.TextField('Текст отзыва', blank=True)
    created_at = models.DateTimeField('Дата создания', auto_now_add=True)

    class Meta:
        unique_together = [('exchange', 'author', 'target')]
        ordering = ['-created_at']
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'

    def __str__(self):
        return f'{self.author} -> {self.target}: {self.score}'


class Notification(models.Model):
    profile = models.ForeignKey(DemoProfile, on_delete=models.CASCADE, related_name='notifications', verbose_name='Профиль')
    text = models.CharField('Текст уведомления', max_length=255)
    url = models.CharField('Ссылка', max_length=255, blank=True)
    is_read = models.BooleanField('Прочитано', default=False)
    created_at = models.DateTimeField('Дата создания', auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Уведомление'
        verbose_name_plural = 'Уведомления'

    def __str__(self):
        return self.text


class Complaint(models.Model):
    class Reason(models.TextChoices):
        WRONG_CATEGORY = 'wrong_category', 'Неверная категория'
        WRONG_DESCRIPTION = 'wrong_description', 'Описание не соответствует товару'
        FRAUD = 'fraud', 'Подозрение на мошенничество'
        FORBIDDEN = 'forbidden', 'Запрещенный товар'
        OFFENSIVE = 'offensive', 'Оскорбительное содержание'
        FAKE_PROFILE = 'fake_profile', 'Недостоверный профиль'
        SPAM = 'spam', 'Спам или навязчивые сообщения'
        OTHER = 'other', 'Другое'

    class Status(models.TextChoices):
        NEW = 'new', 'Новая'
        IN_REVIEW = 'in_review', 'На рассмотрении'
        RESOLVED = 'resolved', 'Рассмотрена'
        REJECTED = 'rejected', 'Отклонена'

    reporter = models.ForeignKey(DemoProfile, on_delete=models.CASCADE, related_name='complaints_created', verbose_name='Автор жалобы')
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name='complaints', null=True, blank=True, verbose_name='Объявление')
    target_profile = models.ForeignKey(
        DemoProfile,
        on_delete=models.CASCADE,
        related_name='complaints_received',
        null=True,
        blank=True,
        verbose_name='Профиль',
    )
    reason = models.CharField('Причина', max_length=40, choices=Reason.choices)
    comment = models.TextField('Комментарий', blank=True)
    status = models.CharField('Статус', max_length=20, choices=Status.choices, default=Status.NEW)
    resolution = models.TextField('Результат рассмотрения', blank=True)
    created_at = models.DateTimeField('Дата создания', auto_now_add=True)
    updated_at = models.DateTimeField('Дата обновления', auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Жалоба'
        verbose_name_plural = 'Жалобы'

    def __str__(self):
        target = self.listing or self.target_profile
        return f'{self.reporter} пожаловался на {target}'

    def clean(self):
        if not self.listing and not self.target_profile:
            raise ValidationError('У жалобы должен быть товар или профиль.')
