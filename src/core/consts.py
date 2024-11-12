import os
import random

WB_FRONT_BASE_URL = "https://wildberries.ru/"

os.system("cls")
# Определяем ANSI escape codes для цветов
RED = '\033[91m'
GREEN = '\033[92m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'  # Сброс цвета

def get_card_link_from_card_id(card_id: int) -> str:
    return WB_FRONT_BASE_URL + f"catalog/{card_id}/detail.aspx"


REVIEW_BASE_URL = "https://feedbacks2.wb.ru/"


CATALOG_BASE_URL = "https://catalog.wb.ru/"
BLUZKI_I_RUBASHKI_ROUTE = "catalog/bl_shirts/v2/catalog?ab_testing=false&appType=1&cat=8126&curr=rub&dest=12358062&sort=popular&spp=30"


# Названия категорий, где нужно два раза нырнуть, прежде чем появятся карточки. И Путешествия тоже скипаем
CATEGORY_NAMES_WITH_SECOND_HIERARCHY = ["Дом", "Аксессуары", "Мебель", "Бытовая техника", "Зоотовары",
                                        "Спорт", "Автотовары", "Книги", "Для ремонта", "Сад и дача",
                                        "Цифровые товары", "Путешествия", "Акции", "Распродажа 11.11",
                                        "Сертификаты Wildberries", "Шторы", "Белье", "Большие размеры",
                                        "Будущие мамы", "Для высоких", "Одежда для дома", "Офис",
                                        "Пляжная мода", "Религиозная", "Свадьба", "Спецодежда и СИЗы",
                                        "Подарки женщинам", "Женская", "Для девочек", "Для мальчиков",
                                        "Для новорожденных", "Прогулки и путешествия", "Товары для малыша",
                                        "Подарки детям", "Подарки мужчинам", "Ванная", "Кухня", "Кружки",
                                        "Кухонный текстиль", "Магниты", "Волосы", "Инструменты для парикмахеров"]

CATEGORIES_URL = "https://static-basket-01.wbbasket.ru/vol0/data/main-menu-ru-ru-v3.json"

def get_category_endpoint_by_page(page: int, category_id, shard: str) -> str:
    return CATALOG_BASE_URL + (f"catalog/{shard}/v2/catalog?ab_testing=false&appType=1&cat={category_id}&curr=rub&dest"
                               f"=12358062&sort=popular&spp=30&page={page}")


def get_review_endpoint_by_card_id(card_id: int) -> str:
    return REVIEW_BASE_URL + f"feedbacks/v2/{card_id}"


userAgentStrings = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.2227.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.3497.92 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36',
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36",
]

HEADERS = {
        "Accept": "*/*",
        "Accept-Language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7",
        "Connection": "keep-alive",
        "Origin": "https://www.wildberries.ru",
        "Referer": "https://www.wildberries.ru/catalog/197396720/feedbacks?imtId=179151289",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "cross-site",
        "User-Agent": random.choice(userAgentStrings),
        "sec-ch-ua": 'Google Chrome";v="111", "Not(A:Brand";v="8", "Chromium";v="111"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": "Windows",
        "cache-control": "no-cache",
}
