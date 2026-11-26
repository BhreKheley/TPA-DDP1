import json
from datetime import datetime

import pytest

from app import create_app
from core.budget import WIB


def merchant(mid, name, canteen, items, updated_at="2026-11-20", **extra):
    return {"id": mid, "name": name, "canteen": canteen, "updated_at": updated_at, "items": items, **extra}


def item(iid, name, category, price):
    return {"id": iid, "name": name, "category": category, "price": price}


SAMPLE = [
    merchant("m1", "Warung Murah", "Kantin A", [
        item("a1", "Nasi", "food", 4000), item("a2", "Tempe", "snack", 2000), item("a3", "Es Teh", "beverage", 3000),
        item("a4", "Ayam", "snack", 9000),
    ]),
    merchant("m2", "Bakso", "Kantin B", [item("b1", "Bakso", "food", 15000)], updated_at="2026-09-01"),
    merchant("m3", "Warung Murah", "Kantin B", [item("c1", "Mie", "food", 8000)],
             opens="22:00", closes="02:00"),  # nama sama di kantin berbeda, buka lewat tengah malam
]


@pytest.fixture
def data_file(tmp_path):
    path = tmp_path / "merchants.json"
    path.write_text(json.dumps(SAMPLE), encoding="utf-8")
    return path


@pytest.fixture
def client(data_file):
    app = create_app({"TESTING": True, "DATA_PATH": data_file,
                      "NOW": datetime(2026, 11, 25, 12, 0, tzinfo=WIB)})
    return app.test_client()
