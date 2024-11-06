import random
import time

import requests
from sqlalchemy import create_engine, insert

from consts import get_review_endpoint_by_card_id, HEADERS
from src import db_models, config
from src.db_models import Cards


class Review:
    def __init__(self, id: str, card_id: int, root_id: int, pros: str, cons: str, created_at: str, updated_at: str, votes: dict,
                 rating: float, text: str, answer: dict):
        self.id = id
        self.card_id = card_id
        self.root_id = root_id
        self.text = text
        self.pros = pros
        self.cons = cons
        self.created_at = created_at
        self.updated_at = updated_at
        self.votes = votes
        self.rating = rating
        self.answer = answer


class WBReviewParser:
    def __init__(self):
        self.session = requests.Session()

    def parse_reviews(self, card: Cards):
        """card: экземпляр класса Cards. Сразу можем доставать поля таблицы оттуда."""

        result = []

        reviews = self.get_reviews(root_id=card.root_id)

        for review in reviews:
            item = Review(id=review["id"],
                          root_id=card.root_id,
                          card_id=card.id,
                          pros=review["pros"],
                          cons=review["cons"],
                          created_at=review["createdDate"],
                          updated_at=review["updatedDate"],
                          rating=review["productValuation"],
                          votes=review.get("votes", None),
                          text=review.get("text", None),
                          answer=review.get("anwser", None)
                          ).__dict__
            result.append(item)

        return result

    def get_reviews(self, root_id: int) -> dict:

        try:
            response = self.http_get(url=f"https://feedbacks1.wb.ru/feedbacks/v1/{root_id}")
            if response.status_code == 200:
                if not response.json()["feedbacks"]:
                    raise Exception("Server 1 is not suitable")
                return response.json()
        except:
            response = self.http_get(url=f"https://feedbacks2.wb.ru/feedbacks/v1/{root_id}")
            if response.status_code == 200:
                if not response.json()["feedbacks"]:
                    raise Exception("Server 2 is not suitable")
                return response.json()["feedbacks"]

    def http_get(self, url: str) -> requests.Response:
        time.sleep(random.randint(1, 2))

        headers = HEADERS
        headers["Referer"] = f"https://www.wildberries.ru/catalog/233261/feedbacks?imtId=179151289"

        response = self.session.get(
            url=url,
            headers=headers,
            proxies={
                'https': 'http://SEF8UZ:aVab4MYAAPbu@dproxy.site:15091',
            }
        )
        return response


if __name__ == "__main__":

    parser = WBReviewParser()
    reviews = parser.parse_reviews(card=[213323171])

