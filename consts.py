import random

WB_FRONT_BASE_URL = "https://wildberries.ru/"


def get_card_link_from_card_id(card_id: int) -> str:
    return WB_FRONT_BASE_URL + f"catalog/{card_id}/detail.aspx"


CATALOG_BASE_URL = "https://catalog.wb.ru/"

REVIEW_BASE_URL = "https://feedbacks2.wb.ru/"

BLUZKI_I_RUBASHKI_ROUTE = "catalog/bl_shirts/v2/catalog?ab_testing=false&appType=1&cat=8126&curr=rub&dest=12358062&sort=popular&spp=30"


def get_category_endpoint_by_page(page: int) -> str:
    return CATALOG_BASE_URL + f"catalog/bl_shirts/v2/catalog?ab_testing=false&appType=1&cat=8126&curr=rub&dest=12358062&sort=popular&spp=30&page={page}"


def get_review_endpoint_by_card_id(card_id: int) -> str:
    return REVIEW_BASE_URL + f"feedbacks/v2/{card_id}"


userAgentStrings = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.2227.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.3497.92 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36',
]

headers = {
    "User-Agent": random.choice(userAgentStrings),
    "Accept": "*/*",
}
