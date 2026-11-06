
CREATE TABLE IF NOT EXISTS market_prices (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    item_id VARCHAR(100) NOT NULL,
    city VARCHAR(50) NOT NULL,
    quality INTEGER NOT NULL,

    sell_price_min DOUBLE PRECISION,
    sell_price_min_date TIMESTAMP,

    sell_price_max DOUBLE PRECISION,
    sell_price_max_date TIMESTAMP,

    buy_price_min DOUBLE PRECISION,
    buy_price_min_date TIMESTAMP,

    buy_price_max DOUBLE PRECISION,
    buy_price_max_date TIMESTAMP,

    collected_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);



ALTER TABLE market_prices
ADD CONSTRAINT uq_market_prices_observation
UNIQUE NULLS NOT DISTINCT (
    item_id,
    city,
    quality,
    sell_price_min,
    sell_price_min_date,
    sell_price_max,
    sell_price_max_date,
    buy_price_min,
    buy_price_min_date,
    buy_price_max,
    buy_price_max_date
);
