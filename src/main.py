from typing import TypeVar

import requests
from sqlalchemy import create_engine, Connection, insert, select, update
from sqlalchemy.orm import sessionmaker, Session

from consts import CATEGORIES_URL
from src import db_models, config
from src.card_parser.main import WBCardParser
from src.db_models import CategoriesTable, Base


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

    # Нечего добавить - не добавляем
    if len(items_to_insert) != 0:
        wb_parser_db.bulk_insert_mappings(mapper=db_model.__mapper__, mappings=items_to_insert)
        wb_parser_db.commit()

    # Обновляем
    wb_parser_db.bulk_update_mappings(mapper=db_model.__mapper__, mappings=items_to_update)

    wb_parser_db.commit()


if __name__ == "__main__":
    # -------------------------------
    # Парсим и закидываем в базу категории товаров
    #categories = CategoryParser().get_categories()
    #
    engine = create_engine(config.WB_PARSER_DB_URL)
    session = sessionmaker(bind=engine)()

    #insert_or_update_to_db(wb_parser_db=session, db_model=CategoriesTable, items_to_add=categories)

    categories = session.query(db_models.CategoriesTable).filter(CategoriesTable.parent != None).all()
    category_ids = [category.id for category in categories]

    # ---------------------------------
    # Парсим карточки товаров, передавая в них category_id (Чтобы умели указывать категорию
    # У карточек есть root_id, он нужен, чтобы парсить отзывы
    parser = WBCardParser()

    for category in categories:
        cards = parser.parse_category(from_page=1, to_page=3, category=category)

        # TODO - здесь остановился
        insert_or_update_to_db(wb_parser_db=session, db_model=db_models.Card, items_to_add=cards)

    # ----------------------------------------
    # Парсим отзывы, отзывы храним привязанно к карточкам, карточки привязаны к категориям.
    # Это итоговый результат парсера.
