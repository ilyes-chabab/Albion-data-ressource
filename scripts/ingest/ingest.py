import json
from pathlib import Path
import asyncio
import aiohttp

BASE_URL = "https://europe.albion-online-data.com/api/v2/stats/prices"
ITEMS_DIR = Path("data\\raw\\items_categories")
OUTPUT_FILE = Path("data\\raw\\market_prices.jsonl")
CHECKPOINT_FILE = Path("data\\raw\\checkpoint.json")

MAX_RETRIES = 5
BASE_DELAY = 1


def get_item_identifiers():
    identifiers = []

    for file_path in ITEMS_DIR.glob("*.json"):
        with file_path.open("r", encoding="utf-8") as file:
            content = json.load(file)

        for item in content["data"]:
            identifier = item.get("identifier")

            if identifier:
                identifiers.append(identifier)

    return identifiers


identifiers_item = get_item_identifiers()


def create_batches(identifiers, batch_size=20):
    batches = []

    for i in range(0, len(identifiers), batch_size):
        batch = identifiers[i:i + batch_size]
        batches.append(batch)

    return batches


def create_urls(batches):
    urls = []

    for batch in batches:
        items = ",".join(batch)
        url = f"{BASE_URL}/{items}.json"
        urls.append(url)

    return urls


def load_checkpoint():
    if CHECKPOINT_FILE.exists():
        with CHECKPOINT_FILE.open("r", encoding="utf-8") as file:
            return json.load(file)

    return []


def save_checkpoint(completed_batches):
    with CHECKPOINT_FILE.open("w", encoding="utf-8") as file:
        json.dump(completed_batches, file)


semaphore = asyncio.Semaphore(5)


async def fetch_url(session, url):
    async with semaphore:
        for attempt in range(MAX_RETRIES):
            try:
                async with session.get(url, timeout=30) as response:
                    if response.status == 429:
                        raise aiohttp.ClientResponseError(
                            response.request_info,
                            response.history,
                            status=response.status
                        )

                    response.raise_for_status()
                    data = await response.json()

                    return data

            except (aiohttp.ClientError, asyncio.TimeoutError) as error:
                if attempt == MAX_RETRIES - 1:
                    print(f"Échec définitif : {url}")
                    raise

                delay = BASE_DELAY * (2 ** attempt)

                print(
                    f"Erreur : {error} | "
                    f"Nouvelle tentative dans {delay} secondes..."
                )

                await asyncio.sleep(delay)


async def main():
    batches = create_batches(identifiers_item)
    urls = create_urls(batches)

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

    completed_batches = load_checkpoint()

    async with aiohttp.ClientSession() as session:
        with OUTPUT_FILE.open("a", encoding="utf-8") as file:
            for batch_index, url in enumerate(urls):

                if batch_index in completed_batches:
                    continue

                data = await fetch_url(session, url)

                for item in data:
                    file.write(json.dumps(item, ensure_ascii=False) + "\n")

                file.flush()

                completed_batches.append(batch_index)
                save_checkpoint(completed_batches)

                print(
                    f"Lot {batch_index + 1}/{len(urls)} terminé "
                    f"- {len(data)} résultats enregistrés"
                )
    if len(completed_batches) == len(urls):
        CHECKPOINT_FILE.unlink(missing_ok=True)
        print("Collecte terminée. Checkpoint supprimé.")


if __name__ == "__main__":
    asyncio.run(main())