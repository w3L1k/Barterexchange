from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from django.utils.text import slugify

from exchange.models import Category, DemoProfile, ExchangeRequest, Favorite, Listing, Notification, Review


class Command(BaseCommand):
    help = 'Create demo profiles, categories and listings for BarterExchange.'

    def handle(self, *args, **options):
        Review.objects.all().delete()
        Favorite.objects.all().delete()
        Notification.objects.all().delete()
        ExchangeRequest.objects.all().delete()
        Listing.objects.all().delete()
        DemoProfile.objects.all().delete()
        Category.objects.all().delete()
        User.objects.filter(is_superuser=False).delete()

        categories = {}
        for name in ['Техника', 'Книги', 'Одежда', 'Спорт', 'Дом', 'Хобби', 'Игры', 'Музыка', 'Другое']:
            categories[name] = Category.objects.create(name=name, slug=slugify(name, allow_unicode=True))

        profiles = [
            ('artem', 'Артем', 'Москва', 'Любит технику, книги и настольные игры.', 4.8),
            ('maria', 'Мария', 'Москва', 'Обменивает вещи для дома и учебы.', 4.6),
            ('ilya', 'Илья', 'Санкт-Петербург', 'Ищет спортивный инвентарь и музыкальные вещи.', 4.7),
            ('sofia', 'София', 'Казань', 'Собирает книги, винил и предметы для творчества.', 4.9),
            ('nikita', 'Никита', 'Нижний Новгород', 'Часто меняет гаджеты и игровые аксессуары.', 4.5),
            ('elena', 'Елена', 'Екатеринбург', 'Ищет полезные вещи для дома и хобби.', 4.4),
            ('daniil', 'Даниил', 'Москва', 'Интересуется спортом, играми и электроникой.', 4.3),
            ('alina', 'Алина', 'Санкт-Петербург', 'Обменивает одежду, книги и декор.', 4.8),
        ]
        profile_objs = []
        for username, name, city, bio, rating in profiles:
            user = User.objects.create_user(username=username, password='demo12345')
            profile_objs.append(DemoProfile.objects.create(user=user, name=name, city=city, bio=bio, rating=rating))
        profiles_by_city = {}
        for profile in profile_objs:
            profiles_by_city.setdefault(profile.city, []).append(profile)

        samples = [
            ('Беспроводные наушники Sony', 'Техника', 'Хорошее', 620, 'Книги', 'фантастика книги роман', 'Москва'),
            ('Kindle Paperwhite', 'Техника', 'Отличное', 700, 'Книги', 'бумажные книги классика', 'Москва'),
            ('Механическая клавиатура', 'Техника', 'Хорошее', 550, 'Игры', 'геймпад настольная игра', 'Москва'),
            ('Фитнес-браслет Mi Band', 'Техника', 'Нормальное', 240, 'Спорт', 'гантели коврик фитнес', 'Казань'),
            ('Пауэрбанк 20000 mAh', 'Техника', 'Хорошее', 360, 'Дом', 'настольная лампа органайзер', 'Санкт-Петербург'),
            ('Роутер TP-Link', 'Техника', 'Хорошее', 300, 'Музыка', 'винил колонка наушники', 'Екатеринбург'),
            ('Смарт-колонка', 'Техника', 'Отличное', 520, 'Дом', 'увлажнитель декор светильник', 'Москва'),
            ('Геймпад Xbox', 'Игры', 'Хорошее', 430, 'Техника', 'клавиатура мышь наушники', 'Нижний Новгород'),
            ('Настольная игра Каркассон', 'Игры', 'Отличное', 380, 'Книги', 'фэнтези фантастика', 'Москва'),
            ('Настольная игра Кодовые имена', 'Игры', 'Хорошее', 300, 'Хобби', 'скетчбук краски кисти', 'Санкт-Петербург'),
            ('Коллекция игр для PS4', 'Игры', 'Хорошее', 750, 'Техника', 'планшет наушники колонка', 'Казань'),
            ('Шахматы деревянные', 'Игры', 'Отличное', 260, 'Книги', 'история биография', 'Москва'),
            ('Книги Терри Пратчетта', 'Книги', 'Хорошее', 420, 'Игры', 'настольная игра стратегия', 'Москва'),
            ('Учебники по Python', 'Книги', 'Хорошее', 350, 'Техника', 'клавиатура мышь монитор', 'Санкт-Петербург'),
            ('Романы Стругацких', 'Книги', 'Нормальное', 300, 'Музыка', 'винил пластинки', 'Казань'),
            ('Атлас по истории искусства', 'Книги', 'Отличное', 480, 'Хобби', 'акварель скетчбук', 'Екатеринбург'),
            ('Книги по дизайну интерфейсов', 'Книги', 'Хорошее', 460, 'Техника', 'планшет стилус', 'Москва'),
            ('Подборка бизнес-книг', 'Книги', 'Хорошее', 400, 'Спорт', 'турник эспандер', 'Нижний Новгород'),
            ('Куртка демисезонная', 'Одежда', 'Хорошее', 500, 'Техника', 'наушники колонка', 'Москва'),
            ('Кроссовки беговые', 'Одежда', 'Хорошее', 450, 'Спорт', 'гантели коврик', 'Санкт-Петербург'),
            ('Рюкзак городской', 'Одежда', 'Отличное', 380, 'Книги', 'python программирование', 'Москва'),
            ('Пальто шерстяное', 'Одежда', 'Хорошее', 650, 'Дом', 'светильник зеркало', 'Казань'),
            ('Худи оверсайз', 'Одежда', 'Отличное', 280, 'Игры', 'настольная игра', 'Екатеринбург'),
            ('Велосипедный шлем', 'Спорт', 'Хорошее', 320, 'Техника', 'фитнес браслет', 'Москва'),
            ('Набор гантелей', 'Спорт', 'Хорошее', 480, 'Одежда', 'кроссовки худи', 'Москва'),
            ('Коврик для йоги', 'Спорт', 'Отличное', 220, 'Дом', 'растение декор', 'Санкт-Петербург'),
            ('Роликовые коньки', 'Спорт', 'Нормальное', 520, 'Техника', 'наушники powerbank', 'Казань'),
            ('Туристический рюкзак', 'Спорт', 'Хорошее', 600, 'Музыка', 'гитара укулеле', 'Нижний Новгород'),
            ('Настольная лампа', 'Дом', 'Отличное', 240, 'Техника', 'пауэрбанк колонка', 'Москва'),
            ('Увлажнитель воздуха', 'Дом', 'Хорошее', 430, 'Техника', 'смарт колонка', 'Москва'),
            ('Комплект посуды', 'Дом', 'Хорошее', 360, 'Книги', 'кулинария дизайн', 'Санкт-Петербург'),
            ('Зеркало в раме', 'Дом', 'Отличное', 520, 'Одежда', 'пальто куртка', 'Казань'),
            ('Органайзер для рабочего стола', 'Дом', 'Новое', 180, 'Техника', 'мышь флешка', 'Екатеринбург'),
            ('Акварельные краски', 'Хобби', 'Отличное', 260, 'Книги', 'искусство дизайн', 'Москва'),
            ('Скетчбук и маркеры', 'Хобби', 'Новое', 300, 'Игры', 'кодовые имена каркассон', 'Санкт-Петербург'),
            ('Набор для вышивания', 'Хобби', 'Хорошее', 220, 'Дом', 'декор лампа', 'Казань'),
            ('Фотоаппарат пленочный', 'Хобби', 'Нормальное', 700, 'Техника', 'kindle планшет', 'Москва'),
            ('Конструктор LEGO', 'Игры', 'Хорошее', 580, 'Игры', 'ps4 геймпад', 'Нижний Новгород'),
            ('Укулеле', 'Музыка', 'Хорошее', 420, 'Спорт', 'рюкзак туристический', 'Москва'),
            ('Виниловые пластинки джаз', 'Музыка', 'Хорошее', 390, 'Книги', 'стругацкие фантастика', 'Казань'),
            ('MIDI-клавиатура', 'Музыка', 'Отличное', 760, 'Техника', 'планшет наушники', 'Санкт-Петербург'),
            ('Портативная колонка JBL', 'Техника', 'Хорошее', 520, 'Дом', 'увлажнитель лампа', 'Екатеринбург'),
            ('Гитара акустическая', 'Музыка', 'Нормальное', 680, 'Спорт', 'туристический рюкзак', 'Нижний Новгород'),
        ]

        condition_map = {
            'Новое': Listing.Condition.NEW,
            'Отличное': Listing.Condition.LIKE_NEW,
            'Хорошее': Listing.Condition.GOOD,
            'Нормальное': Listing.Condition.USED,
        }

        title_image_paths = [
            '/static/exchange/demo_images/stock/headphones.png',
            '/static/exchange/demo_images/stock/kindle.png',
            '/static/exchange/demo_images/stock/keyboard.png',
            '/static/exchange/demo_images/stock/fitness_band.png',
            '/static/exchange/demo_images/stock/powerbank.png',
            '/static/exchange/demo_images/stock/router.png',
            '/static/exchange/demo_images/stock/smart_speaker.png',
            '/static/exchange/demo_images/stock/gamepad.png',
            '/static/exchange/demo_images/stock/carcassonne.png',
            '/static/exchange/demo_images/stock/codenames.png',
            '/static/exchange/demo_images/stock/ps4_games.png',
            '/static/exchange/demo_images/stock/chess.png',
            '/static/exchange/demo_images/stock/pratchett.png',
            '/static/exchange/demo_images/stock/python_books.png',
            '/static/exchange/demo_images/stock/strugatsky.png',
            '/static/exchange/demo_images/stock/art_atlas.png',
            '/static/exchange/demo_images/stock/ui_books.png',
            '/static/exchange/demo_images/stock/business_books.png',
            '/static/exchange/demo_images/stock/jacket.png',
            '/static/exchange/demo_images/stock/sneakers.png',
            '/static/exchange/demo_images/stock/city_backpack.png',
            '/static/exchange/demo_images/stock/coat.png',
            '/static/exchange/demo_images/stock/hoodie.png',
            '/static/exchange/demo_images/stock/helmet.png',
            '/static/exchange/demo_images/stock/dumbbells.png',
            '/static/exchange/demo_images/stock/yoga_mat.png',
            '/static/exchange/demo_images/stock/roller_skates.png',
            '/static/exchange/demo_images/stock/hiking_backpack.png',
            '/static/exchange/demo_images/stock/desk_lamp.png',
            '/static/exchange/demo_images/stock/humidifier.png',
            '/static/exchange/demo_images/stock/dishes.png',
            '/static/exchange/demo_images/stock/mirror.png',
            '/static/exchange/demo_images/stock/organizer.png',
            '/static/exchange/demo_images/stock/watercolors.png',
            '/static/exchange/demo_images/stock/sketchbook.png',
            '/static/exchange/demo_images/stock/embroidery.png',
            '/static/exchange/demo_images/stock/film_camera.png',
            '/static/exchange/demo_images/stock/lego.png',
            '/static/exchange/demo_images/stock/ukulele.png',
            '/static/exchange/demo_images/stock/vinyl.png',
            '/static/exchange/demo_images/stock/midi_keyboard.png',
            '/static/exchange/demo_images/stock/jbl_speaker.png',
            '/static/exchange/demo_images/stock/guitar.png',
        ]

        descriptions = {
            'Беспроводные наушники Sony': 'Полноразмерные наушники с шумоподавлением, держат заряд несколько дней. Есть небольшие следы использования на амбушюрах.',
            'Kindle Paperwhite': 'Электронная книга с подсветкой, экран без трещин, корпус в аккуратном состоянии. Подойдет для чтения в дороге.',
            'Механическая клавиатура': 'Клавиатура с четким ходом клавиш, все кнопки работают. Подойдет для работы, учебы или игр.',
            'Фитнес-браслет Mi Band': 'Браслет считает шаги, пульс и уведомления. Ремешок немного потертый, но устройство работает стабильно.',
            'Пауэрбанк 20000 mAh': 'Емкий пауэрбанк для телефона и небольших гаджетов. Заряжает несколько устройств, корпус без серьезных повреждений.',
            'Роутер TP-Link': 'Домашний Wi-Fi роутер для квартиры, настройки сброшены. В комплекте блок питания.',
            'Смарт-колонка': 'Колонка с голосовым помощником и хорошим звуком для комнаты. Подключение к Wi-Fi работает без проблем.',
            'Геймпад Xbox': 'Беспроводной геймпад, стики не залипают, кнопки нажимаются ровно. Есть потертости на корпусе.',
            'Настольная игра Каркассон': 'Полный комплект настольной игры, карточки и фигурки на месте. Коробка немного помята.',
            'Настольная игра Кодовые имена': 'Игра для компании, карточки в хорошем состоянии. Отличный вариант для вечеров с друзьями.',
            'Коллекция игр для PS4': 'Несколько дисков для PlayStation 4 в коробках. Диски читаются, часть коробок с потертостями.',
            'Шахматы деревянные': 'Деревянные шахматы со складной доской. Все фигуры на месте, доска закрывается плотно.',
            'Книги Терри Пратчетта': 'Подборка книг Терри Пратчетта в мягких обложках. Страницы чистые, без заметок.',
            'Учебники по Python': 'Учебные книги по Python для начинающих и продолжающих. Подойдут для учебы и практики.',
            'Романы Стругацких': 'Несколько романов Стругацких, книги читались аккуратно. Есть небольшие следы хранения.',
            'Атлас по истории искусства': 'Большой иллюстрированный атлас с репродукциями и описаниями. Тяжелая книга в хорошем состоянии.',
            'Книги по дизайну интерфейсов': 'Книги про UX, интерфейсы и визуальную структуру приложений. Подойдут дизайнеру или разработчику.',
            'Подборка бизнес-книг': 'Несколько книг по менеджменту, привычкам и предпринимательству. Без выделений маркером.',
            'Куртка демисезонная': 'Куртка на прохладную погоду, молния работает, ткань без дыр. Размер примерно M.',
            'Кроссовки беговые': 'Легкие кроссовки для пробежек и прогулок. Подошва не стерта, есть следы носки.',
            'Рюкзак городской': 'Городской рюкзак с отделением для ноутбука. Молнии целые, внутри чистый.',
            'Пальто шерстяное': 'Теплое пальто классического кроя. Носилось аккуратно, без заметных дефектов.',
            'Худи оверсайз': 'Свободное худи без принта, ткань плотная. Подойдет для повседневной носки.',
            'Велосипедный шлем': 'Шлем для велосипеда или самоката, регулировка размера работает. Серьезных ударов не было.',
            'Набор гантелей': 'Пара разборных гантелей для домашних тренировок. Вес можно менять под разные упражнения.',
            'Коврик для йоги': 'Мягкий коврик для йоги и растяжки, не скользит на полу. После использования очищен.',
            'Роликовые коньки': 'Ролики для прогулочного катания, застежки держат крепко. Колеса требуют небольшой чистки.',
            'Туристический рюкзак': 'Большой рюкзак для походов с несколькими отделениями. Лямки целые, ткань плотная.',
            'Настольная лампа': 'Лампа для рабочего стола с регулируемым наклоном. Светит ярко, выключатель исправен.',
            'Увлажнитель воздуха': 'Компактный увлажнитель для комнаты, резервуар без трещин. Работает тихо.',
            'Комплект посуды': 'Набор тарелок и чашек для кухни. Без сколов, подойдет для дома или дачи.',
            'Зеркало в раме': 'Зеркало в декоративной раме, стекло без трещин. Можно повесить в прихожей или комнате.',
            'Органайзер для рабочего стола': 'Органайзер для канцелярии, кабелей и мелких вещей. Помогает держать стол в порядке.',
            'Акварельные краски': 'Набор акварели с насыщенными цветами. Часть цветов почти не использовалась.',
            'Скетчбук и маркеры': 'Скетчбук с плотной бумагой и набор маркеров. Подойдет для набросков и учебы.',
            'Набор для вышивания': 'Набор с канвой, нитками и схемой. Упаковка открыта, но детали сохранены.',
            'Фотоаппарат пленочный': 'Пленочный фотоаппарат для любительской съемки. Требует пленку и батарейку.',
            'Конструктор LEGO': 'Набор LEGO с деталями для сборки. Большая часть деталей на месте, инструкция сохранена.',
            'Укулеле': 'Небольшая укулеле с мягким звучанием. Струны стоят, корпус без трещин.',
            'Виниловые пластинки джаз': 'Несколько джазовых пластинок для проигрывателя. Конверты с потертостями, пластинки без глубоких царапин.',
            'MIDI-клавиатура': 'Компактная MIDI-клавиатура для записи музыки и работы в DAW. Подключается по USB.',
            'Портативная колонка JBL': 'Портативная колонка с мощным звуком для комнаты или прогулок. Заряд держит нормально.',
            'Гитара акустическая': 'Акустическая гитара для обучения и домашних занятий. Есть следы использования, звучит ровно.',
        }

        city_counts = {city: 0 for city in profiles_by_city}
        created_listings = []
        extra_desired = {
            'Техника': ['Книги', 'Игры'],
            'Книги': ['Техника', 'Хобби'],
            'Одежда': ['Спорт', 'Техника'],
            'Спорт': ['Одежда', 'Музыка'],
            'Дом': ['Техника', 'Одежда'],
            'Хобби': ['Книги', 'Игры'],
            'Игры': ['Книги', 'Техника'],
            'Музыка': ['Спорт', 'Книги'],
        }
        for index, item in enumerate(samples):
            title, category, condition, _old_value, desired_category, keywords, city = item
            city_profiles = profiles_by_city[city]
            owner = city_profiles[city_counts[city] % len(city_profiles)]
            city_counts[city] += 1
            listing = Listing.objects.create(
                owner=owner,
                title=title,
                description=descriptions[title],
                category=categories[category],
                condition=condition_map[condition],
                city=city,
                exchange_terms='Рассмотрю обмен по интересу и потребности, без привязки к цене товара.',
                external_image_url=title_image_paths[index],
                desired_category=categories[desired_category],
                desired_keywords=keywords,
                acceptable_city=city,
            )
            desired_names = [desired_category]
            for extra_name in extra_desired.get(category, []):
                if extra_name not in desired_names:
                    desired_names.append(extra_name)
                if len(desired_names) == 2:
                    break
            listing.desired_categories.set(categories[name] for name in desired_names)
            created_listings.append(listing)

        profiles_by_username = {profile.user.username: profile for profile in profile_objs}
        listings_by_owner = {profile: [] for profile in profile_objs}
        for listing in created_listings:
            listings_by_owner[listing.owner].append(listing)

        used_listing_ids = set()

        def take_listing(username, offset=0):
            owner_listings = listings_by_owner[profiles_by_username[username]]
            listing = owner_listings[offset % len(owner_listings)]
            used_listing_ids.add(listing.pk)
            return listing

        exchange_specs = [
            ('artem', 'maria', 0, 0, ExchangeRequest.Status.PENDING, 'Готов встретиться в центре Москвы на этой неделе.'),
            ('maria', 'ilya', 0, 0, ExchangeRequest.Status.PENDING, 'Могу передать товар через пункт выдачи или при встрече.'),
            ('ilya', 'sofia', 0, 0, ExchangeRequest.Status.ACCEPTED, 'Условия подходят, договорились о встрече после выходных.'),
            ('sofia', 'nikita', 0, 0, ExchangeRequest.Status.ACCEPTED, 'Обмен без доплаты, состояние товаров устраивает обе стороны.'),
            ('nikita', 'elena', 0, 0, ExchangeRequest.Status.REJECTED, 'Владелец выбрал другое предложение, но обмен остался в истории.'),
            ('elena', 'daniil', 0, 0, ExchangeRequest.Status.CANCELLED, 'Планы поменялись, стороны решили отменить обмен без претензий.'),
            ('maria', 'sofia', 1, 1, ExchangeRequest.Status.REJECTED, 'Предложение не подошло по желаемой категории.'),
            ('ilya', 'alina', 1, 1, ExchangeRequest.Status.CANCELLED, 'Стороны не смогли подобрать удобное время встречи.'),
            ('nikita', 'maria', 1, 2, ExchangeRequest.Status.PENDING, 'Предложение актуально, жду ответа владельца.'),
            ('artem', 'maria', 2, 3, ExchangeRequest.Status.COMPLETED, 'Встретились в удобном месте, обмен прошел без доплаты.'),
            ('maria', 'ilya', 3, 2, ExchangeRequest.Status.COMPLETED, 'Товар соответствовал описанию, быстро согласовали время встречи.'),
            ('ilya', 'sofia', 2, 2, ExchangeRequest.Status.COMPLETED, 'Оба товара проверили на месте, обмен завершили сразу.'),
            ('sofia', 'nikita', 3, 2, ExchangeRequest.Status.COMPLETED, 'Стороны заранее уточнили состояние товаров и остались довольны.'),
            ('nikita', 'elena', 2, 2, ExchangeRequest.Status.COMPLETED, 'Обмен прошел аккуратно, без доплат и спорных условий.'),
            ('elena', 'daniil', 2, 2, ExchangeRequest.Status.COMPLETED, 'Быстро согласовали время, товары передали при личной встрече.'),
            ('daniil', 'alina', 2, 2, ExchangeRequest.Status.COMPLETED, 'Вещи соответствовали описанию, обмен завершили в тот же день.'),
            ('alina', 'artem', 2, 2, ExchangeRequest.Status.COMPLETED, 'Условия были понятными, участники обмена остались на связи.'),
        ]

        completed_review_texts = [
            (
                'Все прошло спокойно: товар был в заявленном состоянии, договоренности соблюдены.',
                'Приятный обмен, быстро договорились и без лишних уточнений завершили встречу.',
            ),
            (
                'Пользователь был на связи и заранее предупредил о времени встречи.',
                'Товар полностью совпал с описанием, обменом остался доволен.',
            ),
            (
                'Хороший опыт обмена: аккуратная вещь и понятные условия.',
                'Встреча прошла без задержек, второй участник был вежлив и подготовлен.',
            ),
        ]
        completed_index = 0

        for initiator_username, receiver_username, offered_offset, requested_offset, status, comment in exchange_specs:
            offered_listing = take_listing(initiator_username, offered_offset)
            requested_listing = take_listing(receiver_username, requested_offset)
            exchange = ExchangeRequest.objects.create(
                initiator=offered_listing.owner,
                receiver=requested_listing.owner,
                offered_listing=offered_listing,
                requested_listing=requested_listing,
                initiator_contact=f'{initiator_username}@barter.local',
                receiver_contact=(
                    f'{receiver_username}@barter.local'
                    if status in [ExchangeRequest.Status.ACCEPTED, ExchangeRequest.Status.COMPLETED]
                    else ''
                ),
                comment='',
                status=status,
            )
            if status == ExchangeRequest.Status.ACCEPTED:
                Listing.objects.filter(pk__in=[offered_listing.pk, requested_listing.pk]).update(status=Listing.Status.IN_DEAL)
            elif status == ExchangeRequest.Status.COMPLETED:
                Listing.objects.filter(pk__in=[offered_listing.pk, requested_listing.pk]).update(status=Listing.Status.ARCHIVED)
                author_text, receiver_text = completed_review_texts[completed_index % len(completed_review_texts)]
                completed_index += 1
                Review.objects.create(
                    exchange=exchange,
                    author=requested_listing.owner,
                    target=offered_listing.owner,
                    score=5,
                    text=author_text,
                )
                Review.objects.create(
                    exchange=exchange,
                    author=offered_listing.owner,
                    target=requested_listing.owner,
                    score=4,
                    text=receiver_text,
                )

        for profile in profile_objs:
            saved = 0
            for listing in created_listings:
                listing.refresh_from_db()
                if listing.owner != profile and listing.status == Listing.Status.ACTIVE:
                    Favorite.objects.get_or_create(profile=profile, listing=listing)
                    saved += 1
                if saved == 2:
                    break

        for owner, owner_listings in listings_by_owner.items():
            active_count = 0
            for listing in owner_listings:
                listing.refresh_from_db()
                if listing.status != Listing.Status.ACTIVE:
                    continue
                if active_count < 3:
                    active_count += 1
                else:
                    listing.status = Listing.Status.ARCHIVED
                    listing.save(update_fields=['status'])

        self.stdout.write(self.style.SUCCESS(f'Создано профилей: {len(profile_objs)}, объявлений: {len(samples)}'))
        self.stdout.write(self.style.SUCCESS(f'Создано обменов: {len(exchange_specs)}, отзывов: {Review.objects.count()}'))
        self.stdout.write(self.style.SUCCESS('Демо-пароль для всех аккаунтов: demo12345'))
