
from pathlib import Path

from huggingface_hub import HfApi


# Configuration du dépôt Hugging Face
REPO_ID = "Sayli84/albion-online-market-prices"
REPO_TYPE = "dataset"

# Fichier Parquet à publier
PARQUET_FILE = Path("data/processed/market_prices.parquet")

# Chemin du fichier dans le dépôt Hugging Face
PATH_IN_REPO = "data/market_prices.parquet"


def publish_dataset():
    """Publie le fichier Parquet sur Hugging Face."""

    # Vérification du fichier
    if not PARQUET_FILE.exists():
        raise FileNotFoundError(
            f"Fichier Parquet introuvable : {PARQUET_FILE}"
        )

    # Initialisation de l'API Hugging Face
    api = HfApi()

    # Vérification de l'existence et de la visibilité du dépôt
    repo_info = api.repo_info(
        repo_id=REPO_ID,
        repo_type=REPO_TYPE
    )

    if not repo_info.private:
        raise ValueError(
            "Le dépôt Hugging Face doit rester privé."
        )

    print(f"Publication de {PARQUET_FILE}...")

    # Envoi du fichier
    api.upload_file(
        path_or_fileobj=str(PARQUET_FILE),
        path_in_repo=PATH_IN_REPO,
        repo_id=REPO_ID,
        repo_type=REPO_TYPE,
        commit_message="Ajout du dataset Albion Online au format Parquet"
    )

    print("Publication terminée.")
    print(f"Dépôt : https://huggingface.co/datasets/{REPO_ID}")


if __name__ == "__main__":
    publish_dataset()
