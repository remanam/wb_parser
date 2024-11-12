from typing import TypeVar

import requests
import sqlalchemy.orm
from pydantic import BaseModel, ValidationError
from sqlalchemy import create_engine, select, and_
from sqlalchemy.orm import sessionmaker, Session

from src.core.consts import CATEGORIES_URL, BLUE, GREEN, RESET
from src import config
from src.models import db_models
from src.core.parsers.card_parser import WBCardParser
from src.models.db_models import CategoriesTable, Base, Cards

from src.core.parsers.review_parser import WBReviewParser
from fastapi import FastAPI, HTTPException

app = FastAPI()


@app.post("/parse_cards_from_category")
async def parse_cards_from_categories(categories: list[dict]) -> None:
    """
    Парсит товары и закидывает их в БД.

    Принимает номера страниц, с которых надо парсить и список категорий.
    Пока поставлю ограничение, что больше 10-ти категорий нельзя.
    """
    if len(categories) > 10:
        raise HTTPException(status_code=400, detail="Нельзя выделять больше 10-ти категорий.")

    card_parser = WBCardParser()

    for category in categories:
        cards = card_parser.parse_cards_from_category(from_page=1, to_page=40, category=category)

        insert_or_update_to_db(wb_parser_db=session, db_model=db_models.Cards, items_to_add=cards)

        print(BLUE + "Сбор карточек - страница " + RESET + GREEN + "TODO" + RESET)
        print("Категория " + GREEN + "id = " + str(
            category["id"]) + "; Название = " + category["name"] + RESET + " ---------------- Готово")
        print("------------------")


class Category(BaseModel):
    id: int
    name: str
    shard: str | None
    parent: int | None
    childs: list | None
    url: str | None

@app.get("/category", summary="Create an item")
async def get_categories() -> list[dict]:
    engine = create_engine(config.WB_PARSER_DB_URL)
    session = sessionmaker(bind=engine)()

    categories = session.query(db_models.CategoriesTable).filter(and_(CategoriesTable.parent != None,
                                                                                   CategoriesTable.childs == None,
                                                                                   CategoriesTable.name != "Цифровые товары",
                                                                                   CategoriesTable.name != "Путешествия",
                                                                                   CategoriesTable.name != "Цифровые аудиокниги",
                                                                                   CategoriesTable.name != "Цифровые книги",
                                                                                   CategoriesTable.id != 131389)).all()
    result = []
    for category in categories:
        try:
            item = Category(**category.__dict__).__dict__
        except ValidationError as e:
            print("Ошибка валидации:", e.json())

        result.append(item)

    return result


class CategoryParser:
    def __init__(self):
        self.session = requests.Session()

    def get_categories_from_url(self):
        try:
            response = self.session.get(url=CATEGORIES_URL)
            assert response.status_code == 200
            response = response.json()
        except:
            raise Exception("Не удалось получить категории")

        categories = []
        for item in response:

            # Добавляем корневую категорию
            categories.append(item)

            # Если есть ПОДКАТЕГОРИИ уровень 1
            if item.get("childs") is not None:
                childs_level1 = item.get("childs")

                # Добавляем подкатегории также
                for child1 in childs_level1:
                    categories.append(child1)

                    # Если есть ПОДКАТЕГОРИИ уровень 2
                    if child1.get("childs") is not None:
                        childs_level2 = child1.get("childs")

                        # Добавляем подкатегории также
                        for child2 in childs_level2:
                            categories.append(child2)

                            # Если есть ПОДКАТЕГОРИИ уровень 3
                            if child2.get("childs") is not None:
                                childs_level3 = child2.get("childs")

                                for child3 in childs_level3:
                                    categories.append(child3)

                                    # Если есть ПОДКАТЕГОРИИ уровень 4
                                    if child3.get("childs") is not None:
                                        childs_level4 = child3.get("childs")

                                        for child4 in childs_level4:
                                            categories.append(child4)

        return categories


# Создаем обобщенный тип для моделей
ModelType = TypeVar('ModelType', bound=Base)
def insert_or_update_to_db(wb_parser_db: Session, db_model: ModelType, items_to_add: list[dict]) -> None:
    """
    :param wb_parser_db: Сессия sqlAlchemy, там есть нужные методы.
    :param db_model:  Передаем сюда одну из наших моделей sqlAlchemy
    :param items_to_add: Данные передаем в виде списка словарей
    """
    # Получаем текущие записи.
    result = wb_parser_db.execute(select(db_model.id)).fetchall()
    ids_to_check = [row[0] for row in result]

    items_to_update = []
    items_to_insert = []

    # Если айдишник есть, то мы запись обновляем, если нет создадим новую
    for item in items_to_add:
        if item.get("id") in ids_to_check:
            items_to_update.append(item)
        else:
            items_to_insert.append(item)

    # Убираем дубликаты, чтоб не наткнуться на ошибку при insert в БД.
    items_to_insert = remove_duplicates_by_id(input_list=items_to_insert)

    # Если в базе нет, то добавляем
    if len(items_to_insert) != 0:
        try:
            wb_parser_db.bulk_insert_mappings(mapper=db_model.__mapper__, mappings=items_to_insert)
            wb_parser_db.commit()
        except:
            print("То, что хотели вставить " + str(items_to_insert))
            print("То, что хотели обновить " + str(items_to_update))
            print("То, что передали для добавления " + str(items_to_add))
            raise Exception("Не удалось выполнить INSERT")

    # Обновляем
    try:
        wb_parser_db.bulk_update_mappings(mapper=db_model.__mapper__, mappings=items_to_update)
        wb_parser_db.commit()
    except:
        print("Не удалось выполнить ОБНОВЛЕНИЕ")
        print("То, что хотели вставить " + str(items_to_insert))
        print("То, что хотели обновить " + str(items_to_update))
        print("То, что передали для добавления " + str(items_to_add))
        raise Exception("Не удалось выполнить UPDATE")


def remove_duplicates_by_id(input_list):
    """Кусок кода с интернета. Возрващает список БЕЗ дубликатов.

    Это нужно на случай, когда карточки товара где-то могут повториться ( по id).
    Таких случаев должно быть мало, но иногда натыкаюсь.
    """
    unique_dict = {item["id"]: item for item in input_list}.values()
    return list(unique_dict)


if __name__ == "__main__":
    # -------------------------------
    # Парсим и закидываем в базу категории товаров
    # Category = CategoryParser().get_categories_from_url()

    engine = create_engine(config.WB_PARSER_DB_URL)
    session = sessionmaker(bind=engine)()

    # insert_or_update_to_db(wb_parser_db=session, db_model=CategoriesTable, items_to_add=Category)

    categories = session.query(db_models.CategoriesTable).filter(and_(CategoriesTable.parent != None,
                                                                      CategoriesTable.childs == None,
                                                                      CategoriesTable.name != "Цифровые товары",
                                                                      CategoriesTable.name != "Путешествия",
                                                                      CategoriesTable.name != "Цифровые аудиокниги",
                                                                      CategoriesTable.name != "Цифровые книги",
                                                                      CategoriesTable.id != 131389,
                                                                      CategoriesTable.parent.in_([306]))).all()
    # category_ids = [category.id for category in Category]
    # ---------------------------------
    # Парсим карточки товаров, передавая в них category_id (Чтобы умели указывать категорию
    # У карточек есть root_id, он нужен, чтобы парсить отзывы
    card_parser = WBCardParser()

    for category in categories:
        cards = card_parser.parse_cards_from_category(from_page=1, to_page=10, category=category.__dict__)

        insert_or_update_to_db(wb_parser_db=session, db_model=db_models.Cards, items_to_add=cards)

        print(BLUE + "Сбор карточек - страница " + RESET + GREEN + "TODO" + RESET)
        print("Категория " + GREEN + "id = " + str(
            category.id) + "; Название = " + category.name + RESET + " ---------------- Готово")
        print("------------------")

    # ----------------------------------------
    # Парсим отзывы, отзывы храним привязанно к карточкам, карточки привязаны к категориям.
    # Это итоговый результат парсера.
    review_parser = WBReviewParser()

    cards = session.execute(select(Cards).where(Cards.reviews_count >= 2000)).fetchall()
    for i in range(len(cards)):
        try:
            reviews = review_parser.parse_reviews(card=cards[i][0])
            insert_or_update_to_db(wb_parser_db=session, db_model=db_models.Review, items_to_add=reviews)

        except:
            print(f"Для карточки {cards[i][0].id} отзывы НЕ добавлены")
    i = 0
