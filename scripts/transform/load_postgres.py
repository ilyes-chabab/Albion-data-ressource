
import os
from pathlib import Path

import pandas as pd
import psycopg2
from psycopg2.extras import execute_values
from dotenv import load_dotenv


# Chargement des variables du fichier .env
load_dotenv()


# Fichier Parquet à importer
PARQUET_FILE = Path("data/processed/market_prices.parquet")

# Configuration PostgreSQL
DB_CONFIG = {
    "host": "localhost",
    "port": 5432,
    "database": "albion_db",
    "user": "albion_user",
    "password": os.getenv("POSTGRES_PASSWORD"),
}

# Nombre de lignes insérées par lot
BATCH_SIZE = 2000

# Colonnes provenant du Parquet
COLUMNS = [
    "item_id",
    "city",
    "quality",
    "sell_price_min",
    "sell_price_min_date",
    "sell_price_max",
    "sell_price_max_date",
    "buy_price_min",
    "buy_price_min_date",
    "buy_price_max",
    "buy_price_max_date",
]


def load_data():

    # Vérification du fichier Parquet
    if not PARQUET_FILE.exists():
        raise FileNotFoundError(
            f"Fichier Parquet introuvable : {PARQUET_FILE}"
        )

    # Vérification du mot de passe
    if not DB_CONFIG["password"]:
        raise ValueError(
            "La variable POSTGRES_PASSWORD est absente du fichier .env."
        )

    print("Lecture du fichier Parquet...")

    df = pd.read_parquet(PARQUET_FILE)

    print(f"{len(df)} lignes trouvées.")

    # Remplacement des valeurs NaN par None pour PostgreSQL
    df = df.astype(object).where(pd.notna(df), None)

    # Conversion du DataFrame en liste de tuples
    records = [
        tuple(row[column] for column in COLUMNS)
        for _, row in df.iterrows()
    ]

    connection = None

    try:
        print("Connexion à PostgreSQL...")

        connection = psycopg2.connect(**DB_CONFIG)

        with connection:
            with connection.cursor() as cursor:

                insert_query = """
                    INSERT INTO market_prices (
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
                    )
                    VALUES %s
                    ON CONFLICT ON CONSTRAINT uq_market_prices_observation
                    DO NOTHING;
                """

                inserted = 0

                for start in range(0, len(records), BATCH_SIZE):

                    batch = records[start:start + BATCH_SIZE]

                    execute_values(
                        cursor,
                        insert_query,
                        batch,
                        page_size=BATCH_SIZE
                    )

                    inserted += cursor.rowcount

                    processed = min(
                        start + BATCH_SIZE,
                        len(records)
                    )

                    print(
                        f"{processed} / {len(records)} lignes traitées..."
                    )

        print("\nChargement terminé.")
        print(f"Lignes présentes dans le Parquet : {len(records)}")
        print(f"Nouvelles lignes insérées        : {inserted}")
        print(
            f"Lignes déjà présentes ignorées  : "
            f"{len(records) - inserted}"
        )

    except Exception:
        if connection:
            connection.rollback()
        raise

    finally:
        if connection:
            connection.close()


if __name__ == "__main__":
    load_data()
