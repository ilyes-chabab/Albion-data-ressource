
import json
from pathlib import Path
from datetime import datetime

import pyarrow as pa
import pyarrow.parquet as pq

from scripts.transform.validation import validate_record


# Fichiers source et destination
INPUT_FILE = Path("data/raw/market_prices.jsonl")
OUTPUT_FILE = Path("data/processed/market_prices.parquet")

# Nombre de lignes traitées à chaque lot
BATCH_SIZE = 5000

# Les 11 champs de l'API utilisés pour identifier un doublon
DEDUPLICATION_COLUMNS = [
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

# Schéma du fichier Parquet
SCHEMA = pa.schema([
    ("item_id", pa.string()),
    ("city", pa.string()),
    ("quality", pa.int64()),
    ("sell_price_min", pa.float64()),
    ("sell_price_min_date", pa.timestamp("s")),
    ("sell_price_max", pa.float64()),
    ("sell_price_max_date", pa.timestamp("s")),
    ("buy_price_min", pa.float64()),
    ("buy_price_min_date", pa.timestamp("s")),
    ("buy_price_max", pa.float64()),
    ("buy_price_max_date", pa.timestamp("s")),
])


def convert_date(value):
    """Convertit une date ISO en datetime."""
    if value == "0001-01-01T00:00:00" or value is None:
        return None

    return datetime.fromisoformat(value)


def transform_record(record):
    """Transforme un enregistrement avant son stockage."""

    return {
        "item_id": record["item_id"],
        "city": record["city"],
        "quality": record["quality"],
        "sell_price_min": record["sell_price_min"],
        "sell_price_min_date": convert_date(record["sell_price_min_date"]),
        "sell_price_max": record["sell_price_max"],
        "sell_price_max_date": convert_date(record["sell_price_max_date"]),
        "buy_price_min": record["buy_price_min"],
        "buy_price_min_date": convert_date(record["buy_price_min_date"]),
        "buy_price_max": record["buy_price_max"],
        "buy_price_max_date": convert_date(record["buy_price_max_date"]),
    }


def get_deduplication_key(record):
    """
    Construit une clé à partir des 11 champs.
    Deux lignes ne sont considérées comme doublons
    que si les 11 valeurs sont identiques.
    """

    return tuple(record[column] for column in DEDUPLICATION_COLUMNS)


def transform_file():

    if not INPUT_FILE.exists():
        print(f"Fichier source introuvable : {INPUT_FILE}")
        return

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

    # Supprime l'ancien fichier Parquet s'il existe
    if OUTPUT_FILE.exists():
        OUTPUT_FILE.unlink()

    total_read = 0
    total_valid = 0
    total_invalid = 0
    total_duplicates = 0
    total_written = 0

    # Stocke les clés des lignes déjà rencontrées
    seen_keys = set()

    batch = []
    writer = None

    with open(INPUT_FILE, "r", encoding="utf-8") as file:

        for line in file:
            total_read += 1

            try:
                record = json.loads(line)

                if not validate_record(record):
                    total_invalid += 1
                    continue

                total_valid += 1

                transformed_record = transform_record(record)

                # Vérification des doublons sur les 11 champs
                key = get_deduplication_key(transformed_record)

                if key in seen_keys:
                    total_duplicates += 1
                    continue

                seen_keys.add(key)
                batch.append(transformed_record)

                # Écriture du lot lorsqu'il atteint sa taille maximale
                if len(batch) >= BATCH_SIZE:

                    table = pa.Table.from_pylist(
                        batch,
                        schema=SCHEMA
                    )

                    if writer is None:
                        writer = pq.ParquetWriter(
                            OUTPUT_FILE,
                            SCHEMA
                        )

                    writer.write_table(table)

                    total_written += len(batch)
                    batch.clear()

                    print(
                        f"{total_read} lignes lues - "
                        f"{total_written} lignes écrites..."
                    )

            except (json.JSONDecodeError, ValueError, TypeError, KeyError):
                total_invalid += 1

    # Écriture du dernier lot
    if batch:
        table = pa.Table.from_pylist(
            batch,
            schema=SCHEMA
        )

        if writer is None:
            writer = pq.ParquetWriter(
                OUTPUT_FILE,
                SCHEMA
            )

        writer.write_table(table)
        total_written += len(batch)

    if writer is not None:
        writer.close()

    print("\nTransformation terminée.")
    print(f"Lignes lues              : {total_read}")
    print(f"Lignes valides           : {total_valid}")
    print(f"Lignes invalides         : {total_invalid}")
    print(f"Doublons supprimés       : {total_duplicates}")
    print(f"Lignes finales           : {total_written}")
    print(f"Fichier Parquet          : {OUTPUT_FILE}")


if __name__ == "__main__":
    transform_file()
