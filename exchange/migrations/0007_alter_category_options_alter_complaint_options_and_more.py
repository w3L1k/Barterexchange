
import django.core.validators
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('exchange', '0006_complaint'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='category',
            options={'ordering': ['name'], 'verbose_name': 'Категория', 'verbose_name_plural': 'Категории'},
        ),
        migrations.AlterModelOptions(
            name='complaint',
            options={'ordering': ['-created_at'], 'verbose_name': 'Жалоба', 'verbose_name_plural': 'Жалобы'},
        ),
        migrations.AlterModelOptions(
            name='demoprofile',
            options={'ordering': ['name'], 'verbose_name': 'Профиль', 'verbose_name_plural': 'Профили'},
        ),
        migrations.AlterModelOptions(
            name='exchangerequest',
            options={'ordering': ['-created_at'], 'verbose_name': 'Предложение обмена', 'verbose_name_plural': 'Предложения обмена'},
        ),
        migrations.AlterModelOptions(
            name='listing',
            options={'ordering': ['-created_at'], 'verbose_name': 'Объявление', 'verbose_name_plural': 'Объявления'},
        ),
        migrations.AlterModelOptions(
            name='listingimage',
            options={'verbose_name': 'Изображение объявления', 'verbose_name_plural': 'Изображения объявлений'},
        ),
        migrations.AlterModelOptions(
            name='notification',
            options={'ordering': ['-created_at'], 'verbose_name': 'Уведомление', 'verbose_name_plural': 'Уведомления'},
        ),
        migrations.AlterModelOptions(
            name='review',
            options={'ordering': ['-created_at'], 'verbose_name': 'Отзыв', 'verbose_name_plural': 'Отзывы'},
        ),
        migrations.AlterField(
            model_name='category',
            name='name',
            field=models.CharField(max_length=80, unique=True, verbose_name='Название'),
        ),
        migrations.AlterField(
            model_name='category',
            name='slug',
            field=models.SlugField(max_length=90, unique=True, verbose_name='Слаг'),
        ),
        migrations.AlterField(
            model_name='complaint',
            name='comment',
            field=models.TextField(blank=True, verbose_name='Комментарий'),
        ),
        migrations.AlterField(
            model_name='complaint',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, verbose_name='Дата создания'),
        ),
        migrations.AlterField(
            model_name='complaint',
            name='listing',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='complaints', to='exchange.listing', verbose_name='Объявление'),
        ),
        migrations.AlterField(
            model_name='complaint',
            name='reason',
            field=models.CharField(choices=[('wrong_category', 'Неверная категория'), ('fraud', 'Подозрение на мошенничество'), ('forbidden', 'Запрещенный товар'), ('offensive', 'Оскорбительное содержание'), ('other', 'Другое')], max_length=40, verbose_name='Причина'),
        ),
        migrations.AlterField(
            model_name='complaint',
            name='reporter',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='complaints_created', to='exchange.demoprofile', verbose_name='Автор жалобы'),
        ),
        migrations.AlterField(
            model_name='complaint',
            name='resolution',
            field=models.TextField(blank=True, verbose_name='Результат рассмотрения'),
        ),
        migrations.AlterField(
            model_name='complaint',
            name='status',
            field=models.CharField(choices=[('new', 'Новая'), ('in_review', 'На рассмотрении'), ('resolved', 'Рассмотрена'), ('rejected', 'Отклонена')], default='new', max_length=20, verbose_name='Статус'),
        ),
        migrations.AlterField(
            model_name='complaint',
            name='target_profile',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='complaints_received', to='exchange.demoprofile', verbose_name='Профиль'),
        ),
        migrations.AlterField(
            model_name='complaint',
            name='updated_at',
            field=models.DateTimeField(auto_now=True, verbose_name='Дата обновления'),
        ),
        migrations.AlterField(
            model_name='demoprofile',
            name='bio',
            field=models.TextField(blank=True, verbose_name='Описание'),
        ),
        migrations.AlterField(
            model_name='demoprofile',
            name='city',
            field=models.CharField(max_length=80, verbose_name='Город'),
        ),
        migrations.AlterField(
            model_name='demoprofile',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, verbose_name='Дата создания'),
        ),
        migrations.AlterField(
            model_name='demoprofile',
            name='name',
            field=models.CharField(max_length=120, verbose_name='Имя'),
        ),
        migrations.AlterField(
            model_name='demoprofile',
            name='rating',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=3, verbose_name='Рейтинг'),
        ),
        migrations.AlterField(
            model_name='demoprofile',
            name='user',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='demo_profile', to=settings.AUTH_USER_MODEL, verbose_name='Пользователь'),
        ),
        migrations.AlterField(
            model_name='exchangerequest',
            name='comment',
            field=models.TextField(blank=True, verbose_name='Комментарий'),
        ),
        migrations.AlterField(
            model_name='exchangerequest',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, verbose_name='Дата создания'),
        ),
        migrations.AlterField(
            model_name='exchangerequest',
            name='initiator',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='outgoing_requests', to='exchange.demoprofile', verbose_name='Инициатор'),
        ),
        migrations.AlterField(
            model_name='exchangerequest',
            name='offered_listing',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='offered_in_requests', to='exchange.listing', verbose_name='Предлагаемое объявление'),
        ),
        migrations.AlterField(
            model_name='exchangerequest',
            name='receiver',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='incoming_requests', to='exchange.demoprofile', verbose_name='Получатель'),
        ),
        migrations.AlterField(
            model_name='exchangerequest',
            name='requested_listing',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='requested_in_requests', to='exchange.listing', verbose_name='Запрошенное объявление'),
        ),
        migrations.AlterField(
            model_name='exchangerequest',
            name='status',
            field=models.CharField(choices=[('pending', 'Ожидает ответа'), ('accepted', 'Принята'), ('rejected', 'Отклонена'), ('cancelled', 'Отменена'), ('completed', 'Завершена')], default='pending', max_length=20, verbose_name='Статус'),
        ),
        migrations.AlterField(
            model_name='exchangerequest',
            name='updated_at',
            field=models.DateTimeField(auto_now=True, verbose_name='Дата обновления'),
        ),
        migrations.AlterField(
            model_name='listing',
            name='acceptable_city',
            field=models.CharField(blank=True, max_length=80, verbose_name='Подходящий город'),
        ),
        migrations.AlterField(
            model_name='listing',
            name='category',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='listings', to='exchange.category', verbose_name='Категория'),
        ),
        migrations.AlterField(
            model_name='listing',
            name='city',
            field=models.CharField(max_length=80, verbose_name='Город'),
        ),
        migrations.AlterField(
            model_name='listing',
            name='condition',
            field=models.CharField(choices=[('new', 'Новое'), ('excellent', 'Отличное'), ('good', 'Хорошее'), ('fair', 'Нормальное')], default='good', max_length=20, verbose_name='Состояние'),
        ),
        migrations.AlterField(
            model_name='listing',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, verbose_name='Дата создания'),
        ),
        migrations.AlterField(
            model_name='listing',
            name='description',
            field=models.TextField(verbose_name='Описание'),
        ),
        migrations.AlterField(
            model_name='listing',
            name='desired_category',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='desired_by_listings', to='exchange.category', verbose_name='Желаемая категория'),
        ),
        migrations.AlterField(
            model_name='listing',
            name='desired_keywords',
            field=models.CharField(help_text='Что пользователь хочет получить: слова через запятую или короткая фраза', max_length=220, verbose_name='Что хочет получить'),
        ),
        migrations.AlterField(
            model_name='listing',
            name='exchange_terms',
            field=models.TextField(blank=True, verbose_name='Условия обмена'),
        ),
        migrations.AlterField(
            model_name='listing',
            name='external_image_url',
            field=models.URLField(blank=True, verbose_name='Внешняя ссылка на изображение'),
        ),
        migrations.AlterField(
            model_name='listing',
            name='owner',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='listings', to='exchange.demoprofile', verbose_name='Владелец'),
        ),
        migrations.AlterField(
            model_name='listing',
            name='status',
            field=models.CharField(choices=[('active', 'Активно'), ('in_deal', 'В обмене'), ('archived', 'В архиве'), ('blocked', 'Заблокировано')], default='active', max_length=20, verbose_name='Статус'),
        ),
        migrations.AlterField(
            model_name='listing',
            name='title',
            field=models.CharField(max_length=160, verbose_name='Название'),
        ),
        migrations.AlterField(
            model_name='listing',
            name='updated_at',
            field=models.DateTimeField(auto_now=True, verbose_name='Дата обновления'),
        ),
        migrations.AlterField(
            model_name='listingimage',
            name='alt_text',
            field=models.CharField(blank=True, max_length=160, verbose_name='Описание изображения'),
        ),
        migrations.AlterField(
            model_name='listingimage',
            name='image',
            field=models.ImageField(upload_to='listings/', verbose_name='Изображение'),
        ),
        migrations.AlterField(
            model_name='listingimage',
            name='listing',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='images', to='exchange.listing', verbose_name='Объявление'),
        ),
        migrations.AlterField(
            model_name='notification',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, verbose_name='Дата создания'),
        ),
        migrations.AlterField(
            model_name='notification',
            name='is_read',
            field=models.BooleanField(default=False, verbose_name='Прочитано'),
        ),
        migrations.AlterField(
            model_name='notification',
            name='profile',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='notifications', to='exchange.demoprofile', verbose_name='Профиль'),
        ),
        migrations.AlterField(
            model_name='notification',
            name='text',
            field=models.CharField(max_length=255, verbose_name='Текст уведомления'),
        ),
        migrations.AlterField(
            model_name='notification',
            name='url',
            field=models.CharField(blank=True, max_length=255, verbose_name='Ссылка'),
        ),
        migrations.AlterField(
            model_name='review',
            name='author',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='reviews_written', to='exchange.demoprofile', verbose_name='Автор'),
        ),
        migrations.AlterField(
            model_name='review',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, verbose_name='Дата создания'),
        ),
        migrations.AlterField(
            model_name='review',
            name='exchange',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='reviews', to='exchange.exchangerequest', verbose_name='Обмен'),
        ),
        migrations.AlterField(
            model_name='review',
            name='score',
            field=models.PositiveSmallIntegerField(validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(5)], verbose_name='Оценка'),
        ),
        migrations.AlterField(
            model_name='review',
            name='target',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='reviews_received', to='exchange.demoprofile', verbose_name='Получатель отзыва'),
        ),
        migrations.AlterField(
            model_name='review',
            name='text',
            field=models.TextField(blank=True, verbose_name='Текст отзыва'),
        ),
    ]
