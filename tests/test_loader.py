import json

import pytest

from core.loader import load_merchants
from core.models import DataError
from tests.conftest import SAMPLE, item, merchant


def write(tmp_path, data):
    path = tmp_path / "d.json"
    path.write_text(json.dumps(data), encoding="utf-8")
    return path


def test_loads_sample(data_file):
    merchants = load_merchants(data_file)
    assert [m.id for m in merchants] == ["m1", "m2", "m3"]
    assert merchants[0].items[0].price == 4000


def test_real_dataset_is_valid():
    assert len(load_merchants("data/merchants.json")) >= 1


@pytest.mark.parametrize("change, expected", [
    (lambda m: m.pop("updated_at"), "updated_at"),
    (lambda m: m.update(canteen=""), "canteen"),
    (lambda m: m.update(items=[]), "minimal satu menu"),
    (lambda m: m["items"][0].update(price="4000"), "bilangan bulat"),
    (lambda m: m["items"][0].update(price=-1), "lebih dari 0"),
    (lambda m: m["items"][0].update(category="soup"), "category"),
    (lambda m: m.update(opens="07:00"), "opens"),
    (lambda m: m.update(opens="07:00", closes="07:00"), "opens"),
    (lambda m: m.update(opens="tujuh", closes="08:00"), "JJ:MM"),
])
def test_rejects_bad_data(tmp_path, change, expected):
    bad = json.loads(json.dumps(SAMPLE))
    change(bad[0])
    with pytest.raises(DataError, match=expected):
        load_merchants(write(tmp_path, bad))


def test_rejects_duplicate_item_ids(tmp_path):
    dup = [merchant("x", "X", "K", [item("i", "a", "food", 1000), item("i", "b", "food", 2000)])]
    with pytest.raises(DataError, match="dobel"):
        load_merchants(write(tmp_path, dup))


def test_missing_and_broken_files(tmp_path):
    with pytest.raises(DataError, match="tidak ditemukan"):
        load_merchants(tmp_path / "nope.json")
    broken = tmp_path / "b.json"
    broken.write_text("{oops", encoding="utf-8")
    with pytest.raises(DataError, match="tidak valid"):
        load_merchants(broken)
    with pytest.raises(DataError, match="tidak kosong"):
        load_merchants(write(tmp_path, []))
