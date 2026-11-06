
-- =====================================================
-- ANALYSES SQL - ALBION ONLINE
-- =====================================================


-- =====================================================
-- 1. Quels sont les prix moyens observés dans chaque ville ?
-- Notions : GROUP BY, COUNT, AVG, FILTER
-- =====================================================

SELECT
    city,
    COUNT(*) AS nombre_observations,

    COUNT(*) FILTER (
        WHERE sell_price_min > 0
    ) AS observations_avec_vente,

    ROUND(
        AVG(sell_price_min) FILTER (
            WHERE sell_price_min > 0
        )::numeric,
        2
    ) AS prix_moyen_vente,

    ROUND(
        AVG(buy_price_max) FILTER (
            WHERE buy_price_max > 0
        )::numeric,
        2
    ) AS prix_moyen_achat

FROM market_prices
GROUP BY city
ORDER BY prix_moyen_vente DESC;


-- =====================================================
-- 2. Quels objets sont disponibles à la vente
-- dans le plus de villes ?
-- Notions : GROUP BY, COUNT DISTINCT, HAVING, FILTER
-- =====================================================

SELECT
    item_id,
    quality,

    COUNT(DISTINCT city) FILTER (
        WHERE sell_price_min > 0
    ) AS nombre_villes_avec_vente,

    COUNT(DISTINCT city) FILTER (
        WHERE buy_price_max > 0
    ) AS nombre_villes_avec_achat

FROM market_prices
GROUP BY item_id, quality

HAVING COUNT(DISTINCT city) FILTER (
    WHERE sell_price_min > 0
) >= 2

ORDER BY
    nombre_villes_avec_vente DESC,
    item_id,
    quality

LIMIT 20;


-- =====================================================
-- 3. Dans quelles villes un objet coûte-t-il plus cher
-- que sa moyenne dans les différentes villes ?
-- Notions : CTE, DISTINCT ON, AVG, JOIN
-- =====================================================

WITH dernieres_observations AS (

    SELECT DISTINCT ON (item_id, quality, city)
        item_id,
        quality,
        city,
        sell_price_min,
        sell_price_min_date

    FROM market_prices

    WHERE sell_price_min > 0
      AND sell_price_min_date IS NOT NULL

    ORDER BY
        item_id,
        quality,
        city,
        sell_price_min_date DESC,
        id DESC
),

moyennes_objets AS (

    SELECT
        item_id,
        quality,
        AVG(sell_price_min) AS prix_moyen

    FROM dernieres_observations

    GROUP BY item_id, quality

    HAVING COUNT(DISTINCT city) >= 2
)

SELECT
    o.item_id,
    o.quality,
    o.city,
    o.sell_price_min,
    ROUND(m.prix_moyen::numeric, 2) AS prix_moyen

FROM dernieres_observations o

JOIN moyennes_objets m
    ON o.item_id = m.item_id
   AND o.quality = m.quality

WHERE o.sell_price_min > m.prix_moyen

ORDER BY
    o.item_id,
    o.sell_price_min DESC;


-- =====================================================
-- 4. Quels sont les 10 objets les plus chers
-- dans chaque ville ?
-- Notions : CTE, ROW_NUMBER, PARTITION BY
-- =====================================================

WITH dernieres_observations AS (

    SELECT DISTINCT ON (item_id, quality, city)
        item_id,
        quality,
        city,
        sell_price_min,
        sell_price_min_date

    FROM market_prices

    WHERE sell_price_min > 0
      AND sell_price_min_date IS NOT NULL

    ORDER BY
        item_id,
        quality,
        city,
        sell_price_min_date DESC,
        id DESC
),

classement AS (

    SELECT
        city,
        item_id,
        quality,
        sell_price_min,

        ROW_NUMBER() OVER (
            PARTITION BY city
            ORDER BY sell_price_min DESC, item_id, quality
        ) AS rang

    FROM dernieres_observations
)

SELECT
    city,
    item_id,
    quality,
    sell_price_min,
    rang

FROM classement

WHERE rang <= 10

ORDER BY city, rang;


-- =====================================================
-- 5. Quels sont les plus grands écarts de prix
-- entre deux villes pour un même objet ?
-- Notions : CTE, auto-jointure, ABS, LIMIT
-- =====================================================

WITH dernieres_observations AS (

    SELECT DISTINCT ON (item_id, quality, city)
        item_id,
        quality,
        city,
        sell_price_min,
        sell_price_min_date

    FROM market_prices

    WHERE sell_price_min > 0
      AND sell_price_min_date IS NOT NULL

    ORDER BY
        item_id,
        quality,
        city,
        sell_price_min_date DESC,
        id DESC
)

SELECT
    a.item_id,
    a.quality,

    a.city AS ville_1,
    b.city AS ville_2,

    a.sell_price_min AS prix_ville_1,
    b.sell_price_min AS prix_ville_2,

    b.sell_price_min - a.sell_price_min AS difference_prix

FROM dernieres_observations a

JOIN dernieres_observations b
    ON a.item_id = b.item_id
   AND a.quality = b.quality
   AND a.city < b.city

ORDER BY
    ABS(b.sell_price_min - a.sell_price_min) DESC

LIMIT 50;


-- =====================================================
-- 6. TEST DE PERFORMANCE D'UN INDEX
-- Objectif : accélérer la recherche de la dernière
-- observation de vente par objet, qualité et ville.
-- =====================================================


-- ETAPE 1 : supprimer l'index s'il existe déjà

DROP INDEX IF EXISTS idx_market_prices_latest_sell;


-- ETAPE 2 : actualiser les statistiques

ANALYZE market_prices;


-- ETAPE 3 : mesurer sans l'index

EXPLAIN (ANALYZE, BUFFERS)
SELECT DISTINCT ON (item_id, quality, city)
    item_id,
    quality,
    city,
    sell_price_min,
    sell_price_min_date

FROM market_prices

WHERE sell_price_min > 0
  AND sell_price_min_date IS NOT NULL

ORDER BY
    item_id,
    quality,
    city,
    sell_price_min_date DESC,
    id DESC;


-- ETAPE 4 : créer l'index

CREATE INDEX idx_market_prices_latest_sell
ON market_prices (
    item_id,
    quality,
    city,
    sell_price_min_date DESC,
    id DESC
)
WHERE sell_price_min > 0
  AND sell_price_min_date IS NOT NULL;


-- ETAPE 5 : actualiser les statistiques

ANALYZE market_prices;


-- ETAPE 6 : mesurer avec l'index

EXPLAIN (ANALYZE, BUFFERS)
SELECT DISTINCT ON (item_id, quality, city)
    item_id,
    quality,
    city,
    sell_price_min,
    sell_price_min_date

FROM market_prices

WHERE sell_price_min > 0
  AND sell_price_min_date IS NOT NULL

ORDER BY
    item_id,
    quality,
    city,
    sell_price_min_date DESC,
    id DESC;
