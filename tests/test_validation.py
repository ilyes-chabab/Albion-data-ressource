
import pytest

from scripts.transform.validation import validate_record


@pytest.fixture
def valid_record():
    return {
        "item_id": "T4_MAIN_SWORD",
        "city": "Martlock",
        "quality": 1,
        "sell_price_min": 1000,
        "sell_price_min_date": "2026-11-06T10:00:00",
        "sell_price_max": 1200,
        "sell_price_max_date": "2026-11-06T10:00:00",
        "buy_price_min": 800,
        "buy_price_min_date": "2026-11-06T10:00:00",
        "buy_price_max": 900,
        "buy_price_max_date": "2026-11-06T10:00:00",
    }


def test_valid_record(valid_record):
    assert validate_record(valid_record) is True


def test_record_not_dictionary():
    assert validate_record("invalid") is False


def test_missing_column(valid_record):
    del valid_record["item_id"]

    assert validate_record(valid_record) is False


def test_invalid_item_id(valid_record):
    valid_record["item_id"] = 123

    assert validate_record(valid_record) is False


def test_invalid_quality(valid_record):
    valid_record["quality"] = "1"

    assert validate_record(valid_record) is False


def test_invalid_price(valid_record):
    valid_record["sell_price_min"] = "1000"

    assert validate_record(valid_record) is False


def test_invalid_date(valid_record):
    valid_record["sell_price_min_date"] = "date_invalide"

    assert validate_record(valid_record) is False


def test_sentinel_date_is_accepted(valid_record):
    valid_record["sell_price_min_date"] = "0001-01-01T00:00:00"

    assert validate_record(valid_record) is True
