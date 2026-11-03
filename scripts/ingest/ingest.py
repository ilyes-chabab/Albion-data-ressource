import json 
from pathlib import Path
import asyncio
import aiohttp


BASE_URL = "https://europe.albion-online-data.com/api/v2/stats/prices"
ITEMS_DIR = Path("data\\raw\\items_categories")
OUTPUT_FILE = Path("data\\raw\\market_prices.jsonl")

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

async def fetch_url(session, url):

    async with session.get(url) as response:

        response.raise_for_status()

        data = await response.json()

        return data
    
async def main():

    urls = create_urls(create_batches(identifiers_item))
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

    async with aiohttp.ClientSession() as session:

        with OUTPUT_FILE.open("w", encoding="utf-8") as file:

            for url in urls:

                data = await fetch_url(session, url)

                for item in data:
                    file.write(json.dumps(item, ensure_ascii=False) + "\n")

                print(f"{len(data)} résultats enregistrés")

    print(f"Fichier JSONL créé : {OUTPUT_FILE}")


if __name__ == "__main__":
    asyncio.run(main())

