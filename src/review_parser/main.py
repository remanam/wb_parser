import requests
from sqlalchemy import create_engine, insert

from consts import get_review_endpoint_by_card_id, headers
from src import db_models, config


class Review:
    def __init__(self, id: str, card_id: int, pros: str, cons: str, created_at: str, updated_at: str, votes: dict,
                 rating: float, text: str, answer: dict):
        self.id = id
        self.card_id = card_id
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

    def parse_reviews(self, card_ids: list):
        """Сюда передается id карточки wildberies. Дальше парсим список отзывов."""

        result = []

        for card_id in card_ids:

            url = get_review_endpoint_by_card_id(card_id=card_id)


            response = self.session.get(url=url, headers=headers, proxies= {
                'https': 'http://YmHUU8:yC8usUDyHmuX@dproxy.site:14780',
            })
            assert response.status_code == 200
            reviews = response.json()["feedbacks"]

            for review in reviews:
                item = Review(id=review["id"],
                              card_id=card_id,
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


if __name__ == "__main__":
    parser = WBReviewParser()
    reviews = parser.parse_reviews(card_ids=[256577870])

    # Создание движка SQLAlchemy
    t = db_models.Review
    wb_parser_db = create_engine(config.WB_PARSER_DB_URL).connect()

    from src import db_models
    target_metadata = db_models.Base.metadata

    wb_parser_db.execute(insert(t).values(reviews))
    wb_parser_db.commit()
    i = 0
