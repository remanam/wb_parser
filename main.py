import pandas
from openpyxl.styles import PatternFill
from datetime import datetime

import requests

from consts import CATALOG_BASE_URL, BLUZKI_I_RUBASHKI_ROUTE, get_card_link_from_card_id, get_category_endpoint_by_page
from results.utils import change_color_of_columns

fields = ['card_id', 'product_rating', 'reviews_count', 'product_type']


class Review:
    def __init__(self, card_link: str, card_name: str, card_id: int, quantity: int, product_type: str,
                 reviews_count: int, product_rating: int):
        self.card_link = card_link
        self.card_name = card_name
        self.card_id = card_id
        self.quantity = quantity
        self.product_type = product_type
        self.reviews_count = reviews_count
        self.product_rating = product_rating


class WBReviewParser:
    def __init__(self):
        self.session = requests.Session()

    def parse_rubashki_bluzki_reviews(self, from_page: int, to_page: int):
        products = []
        for index in range(1, to_page - from_page + 2):
            url = get_category_endpoint_by_page(page=index)

            response = self.session.get(url=url)
            assert response.status_code == 200
            portion_products = response.json()["data"]["products"]

            for item in portion_products:
                products.append(item)

        result = []

        for product in products:
            card_id = product["id"]

            card_link = get_card_link_from_card_id(card_id=card_id)

            item = Review(
                card_link=card_link,
                card_name=product["brand"] + " " + product["name"],
                card_id=card_id,
                quantity=product["totalQuantity"],
                reviews_count=product["nmFeedbacks"],
                product_rating=product["nmReviewRating"],
                product_type=product["entity"]).__dict__

            result.append(item)

        today = datetime.today().strftime("%Y-%m-%d")

        filename = f'./results/result_of_{today}.xlsx'

        # Создаем DataFrame из списка объектов Review
        df = pandas.DataFrame(result)

        # Записываем DataFrame в CSV
        df.to_excel(filename, index=False, engine='openpyxl')

        # Задаем цвет для заголовков
        yellow_fill = PatternFill(start_color="FFFF00", end_color="FFFF00", fill_type="solid")  # Желтый цвет
        change_color_of_columns(filename=filename, color=yellow_fill)

        return result


if __name__ == "__main__":
    parser = WBReviewParser()
    parser.parse_rubashki_bluzki_reviews(from_page=1, to_page=2)
    i = 0
