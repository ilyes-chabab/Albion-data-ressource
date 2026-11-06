from datetime import datetime

# Colonnes obligatoires provenant de l'API Albion Online Data Project
REQUIRED_COLUMNS = [
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

# Colonnes contenant des prix
PRICE_COLUMNS = [
    "sell_price_min",
    "sell_price_max",
    "buy_price_min",
    "buy_price_max",
]


def validate_record(record):
    """
    Vérifie qu'un enregistrement contient les colonnes obligatoires
    et que les valeurs respectent les types attendus.
    """

    # Vérification du format de l'enregistrement
    if not isinstance(record, dict):
        return False

    # Vérification de la présence des colonnes
    if not all(column in record for column in REQUIRED_COLUMNS):
        return False

    # Vérification des identifiants
    if not isinstance(record["item_id"], str):
        return False

    if not isinstance(record["city"], str):
        return False

    # Vérification de la qualité
    if not isinstance(record["quality"], int):
        return False

    # Vérification des prix
    for column in PRICE_COLUMNS:
        if not isinstance(record[column], (int, float)):
            return False

    # Vérification des dates
    for column in REQUIRED_COLUMNS:
        if column.endswith("_date"):

            # La date sentinelle représente une date indisponible
            if record[column] == "0001-01-01T00:00:00":
                continue

            try:
                datetime.fromisoformat(record[column])
            except (ValueError, TypeError):
                return False

    return True