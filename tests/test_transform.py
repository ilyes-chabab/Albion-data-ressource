
import json
from datetime import datetime

import pyarrow.parquet as pq

import scripts.transform.transform_prices as transformer


def create_record():
    """Crée un enregistrement valide pour les tests."""

    return {
        "item_id": "T4_BAG",
        "city": "Bridgewatch",
        "quality": 1,
        "sell_price_min": 1000,
        "sell_price_min_date": "2026-11-06T10:00:00",
        "sell_price_max": 1200,
        "sell_price_max_date": "2026-11-06T10:00:00",
        "buy_price_min": 900,
        "buy_price_min_date": "2026-11-06T10:00:00",
        "buy_price_max": 950,
        "buy_price_max_date": "2026-11-06T10:00:00",
    }


def test_convert_date():
    result = transformer.convert_date("2026-11-06T10:00:00")

    assert result == datetime(2026, 11, 6, 10, 0, 0)


def test_convert_sentinel_date():
    result = transformer.convert_date("0001-01-01T00:00:00")

    assert result is None


def test_transform_record():
    record = create_record()

    result = transformer.transform_record(record)

    assert result["item_id"] == "T4_BAG"
    assert result["city"] == "Bridgewatch"
    assert result["quality"] == 1
    assert result["sell_price_min"] == 1000
    assert result["sell_price_min_date"] == datetime(2026, 11, 6, 10, 0, 0)


def test_deduplication_key():
    record1 = transformer.transform_record(create_record())
    record2 = transformer.transform_record(create_record())

    assert (
        transformer.get_deduplication_key(record1)
        == transformer.get_deduplication_key(record2)
    )


def test_different_prices_have_different_keys():
    record1 = transformer.transform_record(create_record())

    record2_data = create_record()
    record2_data["sell_price_min"] = 1500
    record2 = transformer.transform_record(record2_data)

    assert (
        transformer.get_deduplication_key(record1)
        != transformer.get_deduplication_key(record2)
    )


def test_transform_file(tmp_path, monkeypatch):
    input_file = tmp_path / "market_prices.jsonl"
    output_file = tmp_path / "market_prices.parquet"

    record1 = create_record()
    record2 = create_record()  # Doublon exact

    record3 = create_record()
    record3["sell_price_min"] = 1500  # Enregistrement différent

    record4 = create_record()
    record4["quality"] = "incorrect"  # Enregistrement invalide

    records = [record1, record2, record3, record4]

    with open(input_file, "w", encoding="utf-8") as file:
        for record in records:
            file.write(json.dumps(record) + "\n")

    monkeypatch.setattr(transformer, "INPUT_FILE", input_file)
    monkeypatch.setattr(transformer, "OUTPUT_FILE", output_file)
    monkeypatch.setattr(transformer, "BATCH_SIZE", 2)

    transformer.transform_file()

    assert output_file.exists()

    table = pq.read_table(output_file)

    assert table.num_rows == 2
    assert table.column("sell_price_min").to_pylist() == [1000, 1500]
