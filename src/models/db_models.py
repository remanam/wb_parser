# Определяем базовый класс для моделей
from sqlalchemy import Column, String, Integer, Numeric, Date, JSON, ForeignKey, Boolean
from sqlalchemy.orm import Mapped, declarative_base

Base = declarative_base()


# Определяем модель для таблицы users
class Cards(Base):
    __tablename__ = 'cards'

    id: Mapped[int] = Column(Integer, primary_key=True)
    card_name: Mapped[str] = Column(String, nullable=False)
    root_id: Mapped[int] = Column(Integer, nullable=False)
    category_id: Mapped[int] = Column(Integer, ForeignKey("Category.id"), nullable=True)  # Внешний ключ
    card_link: Mapped[str] = Column(String, nullable=False)
    quantity: Mapped[int] = Column(Integer, nullable=False)
    reviews_count: Mapped[int] = Column(Integer, nullable=False)
    product_rating: Mapped[float] = Column(Numeric, nullable=False)
    product_type: Mapped[str] = Column(String, nullable=False)


class CategoriesTable(Base):
    __tablename__ = 'categories'

    id: Mapped[int] = Column(Integer, primary_key=True)
    name: Mapped[str] = Column(String, nullable=False)
    parent: Mapped[int] = Column(Integer, nullable=True)
    url: Mapped[str] = Column(String, nullable=False)
    shard: Mapped[str] = Column(String, nullable=True) # Путь до URL
    childs: Mapped[dict] = Column(JSON, nullable=True, default= None)


class Review(Base):
    __tablename__ = "reviews"
    id: Mapped[str] = Column(String, primary_key=True)
    card_id: Mapped[int] = Column(Integer, ForeignKey("cards.id"), nullable=False)  # Внешний ключ
    root_id: Mapped[int] = Column(Integer, nullable=False)
    text: Mapped[str] = Column(String, nullable=False)
    pros: Mapped[str] = Column(String, nullable=False)
    cons: Mapped[str] = Column(String, nullable=False)
    votes: Mapped[dict] = Column(JSON, nullable=True)
    rating: Mapped[float] = Column(Numeric, nullable=False)
    answer: Mapped[dict] = Column(JSON, nullable=True)
    created_at: Mapped[str] = Column(Date, nullable=False)
    updated_at: Mapped[str] = Column(Date, nullable=False)
