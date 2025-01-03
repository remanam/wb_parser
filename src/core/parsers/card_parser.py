import requests

from src.core.consts import get_card_link_from_card_id, get_category_endpoint_by_page


class Card:
    def __init__(self, card_link: str, card_name: str, root_id: int, card_id: int, quantity: int, product_type: str,
                 reviews_count: int, product_rating: int, category_id: int):
        self.card_link = card_link
        self.card_name = card_name
        self.id = card_id
        self.root_id = root_id
        self.quantity = quantity
        self.product_type = product_type
        self.reviews_count = reviews_count
        self.product_rating = product_rating
        self.category_id = category_id


class WBCardParser:
    def __init__(self):
        self.session = requests.Session()

    def parse_cards_from_category(self, category: dict, from_page: int, to_page: int) -> list[dict] | None:
        products = []
        for index in range(1, to_page - from_page + 2):
            url = get_category_endpoint_by_page(page=index, category_id=category["id"], shard=category["shard"])

            response = self.session.get(url=url)
            try:
                assert response.status_code == 200
            except:
                print(response.status_code)
                print(response.request.url)
                return
            portion_products = response.json()["data"]["products"]

            for item in portion_products:
                products.append(item)

        result = []

        for product in products:
            card_id = product["id"]

            card_link = get_card_link_from_card_id(card_id=card_id)

            item = Card(
                card_link=card_link,
                card_name=product["brand"] + " " + product["name"],
                card_id=card_id,
                root_id=product["root"],
                quantity=product["totalQuantity"],
                reviews_count=product["nmFeedbacks"],
                product_rating=product["nmReviewRating"],
                product_type=product["entity"],
                category_id=category["id"]).__dict__

            result.append(item)

        # today = datetime.today().strftime("%Y-%m-%d")

        # filename = f'./results/result_of_{today}.xlsx'
        #
        # # Создаем DataFrame из списка объектов Cards
        # df = pandas.DataFrame(result)
        #
        # # Записываем DataFrame в CSV
        # df.to_excel(filename, index=False, engine='openpyxl')
        #
        # # Задаем цвет для заголовков
        # yellow_fill = PatternFill(start_color="FFFF00", end_color="FFFF00", fill_type="solid")  # Желтый цвет
        # change_color_of_columns(filename=filename, color=yellow_fill)

        return result

