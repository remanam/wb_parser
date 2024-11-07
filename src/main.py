from collections import OrderedDict
from typing import TypeVar

import requests
from sqlalchemy import create_engine, Connection, insert, select, update, or_, and_, not_
from sqlalchemy.orm import sessionmaker, Session

from consts import CATEGORIES_URL, CATEGORY_NAMES_WITH_SECOND_HIERARCHY
from src import db_models, config
from src.card_parser.main import WBCardParser
from src.db_models import CategoriesTable, Base, Cards
import os

from src.review_parser.main import WBReviewParser

os.system("cls")
# Определяем ANSI escape codes для цветов
RED = '\033[91m'
GREEN = '\033[92m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'  # Сброс цвета


def create_category_from_dict(item: dict, is_sub_caterogy: bool = False) -> CategoriesTable:
    category = CategoriesTable()

    category.id = item["id"]
    category.name = item["name"]
    category.url = item["url"]

    if item.get("shard") is not None:
        category.shard = item.get("shard")

    if is_sub_caterogy:
        if item.get("parent") is None:
            raise Exception("У подкатегории нет родителя")
        else:
            category.parent = item["parent"]

    return category


class CategoryParser:
    def __init__(self):
        self.session = requests.Session()

    def get_categories(self):
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
                                        print("Есть категории 4 уровня")

        return categories


def add_categories_to_db(wb_parser_db: Session, categories: list[dict]):
    # Получаем текущие записи.
    t = db_models.CategoriesTable
    result = wb_parser_db.execute(select(t.id)).fetchall()
    ids_to_check = [row[0] for row in result]

    categories_to_update = []
    categories_to_insert = []

    for category in categories:
        if category.get("id") in ids_to_check:
            categories_to_update.append(category)
        else:
            categories_to_insert.append(category)

    if len(categories_to_insert) != 0:
        wb_parser_db.bulk_insert_mappings(mapper=db_models.CategoriesTable.__mapper__, mappings=categories_to_insert)

    wb_parser_db.bulk_update_mappings(mapper=db_models.CategoriesTable.__mapper__, mappings=categories_to_update)

    wb_parser_db.commit()


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
    categories = CategoryParser().get_categories()
    #
    engine = create_engine(config.WB_PARSER_DB_URL)
    session = sessionmaker(bind=engine)()

    insert_or_update_to_db(wb_parser_db=session, db_model=CategoriesTable, items_to_add=categories)

    # categories = session.execute(select(CategoriesTable) \
    #     .where(
    #     or_(CategoriesTable.name == "Цветы",
    #         and_(
    #             CategoriesTable.parent != None,
    #             not_(CategoriesTable.name.in_(CATEGORY_NAMES_WITH_SECOND_HIERARCHY))))
    # )).scalars().all()
    # categories = session.query(db_models.CategoriesTable).filter(and_(CategoriesTable.parent != None,
    #                                                                   CategoriesTable.childs == None,
    #                                                                   CategoriesTable.name != "Цифровые товары",
    #                                                                   CategoriesTable.name != "Путешествия",
    #                                                                   CategoriesTable.name != "Цифровые аудиокниги",
    #                                                                   CategoriesTable.name != "Цифровые книги",
    #                                                                   CategoriesTable.id != 131389)).all()
    # category_ids = [category.id for category in categories]
    # ---------------------------------
    # Парсим карточки товаров, передавая в них category_id (Чтобы умели указывать категорию
    # У карточек есть root_id, он нужен, чтобы парсить отзывы
    # parser = WBCardParser()
    #
    # for category in categories:
    #     cards = parser.parse_category(from_page=1, to_page=1, category=category)
    #
    #     insert_or_update_to_db(wb_parser_db=session, db_model=db_models.Cards, items_to_add=cards)
    #
    #     print(BLUE + "Сбор карточек - страница " + RESET + GREEN + "TODO" + RESET)
    #     print("Категория " + GREEN + "id = " + str(
    #         category.id) + "; Название = " + category.name + RESET + " ---------------- Готово")
    #     print("------------------")

    # ----------------------------------------
    # Парсим отзывы, отзывы храним привязанно к карточкам, карточки привязаны к категориям.
    # Это итоговый результат парсера.
    review_parser = WBReviewParser()

    card_for_review_parsing = session.execute(select(Cards).where(Cards.reviews_count >= 500)).fetchone()[0]

    reviews = review_parser.parse_reviews(card=card_for_review_parsing)
    insert_or_update_to_db(wb_parser_db=session, db_model=db_models.Review, items_to_add=reviews)
    i = 0


