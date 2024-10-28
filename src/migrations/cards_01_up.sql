-- Создание таблицы cards
CREATE TABLE cards (
    id SERIAL PRIMARY KEY,  -- Автоинкрементируемый первичный ключ
    card_name VARCHAR(255) NOT NULL,  -- Строка для названия карты, не может быть пустой
    card_link VARCHAR(255) NOT NULL,   -- Строка для ссылки на карту, не может быть пустой
    quantity INTEGER NOT NULL,           -- Целое число для количества, не может быть пустым
    reviews_count INTEGER NOT NULL,      -- Целое число для количества отзывов, не может быть пустым
    reviews_id INTEGER, -- айдишник на таблицу с отзывами по этой карточке товара
    product_rating FLOAT NOT NULL,       -- Не целое число для рейтинга продукта, не может быть пустым
    product_type VARCHAR(255) NOT NULL   -- Строка для категории товара, не может быть пустой
);