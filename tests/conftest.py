"""Shared pytest fixtures for Smart Meal Finder core unit tests.

Provides deterministic sample datasets, frozen MenuItem instances, Merchant wrappers,
synthetic edge-case fixtures (zero price, greedy failure counterexamples, extreme budgets),
and temporary JSON file factories.
"""

import json
from pathlib import Path
from typing import Any, Callable, Dict, List
import pytest

from core.loader import Category, MenuItem, Merchant


@pytest.fixture
def sample_menu_items() -> List[MenuItem]:
    """Provides a deterministic set of validated MenuItem objects across categories and canteens."""
    return [
        MenuItem(
            id="dallas_food_01",
            name="Nasi Ayam Penyet Sambal Bawang",
            category=Category.FOOD,
            price=16000,
            satisfaction_score=89.0,
            dietary_tags=frozenset({"halal", "spicy"}),
            merchant_id="m_dallas_01",
            merchant_name="Ayam Penyet Mas Brow",
            canteen_name="Kantin Dallas",
            faculty="RIK UI",
            calories=580,
            description="Ayam penyet pedas nikmat",
            is_available=True,
        ),
        MenuItem(
            id="dallas_food_02",
            name="Nasi Tempe Orek & Telur Dadar",
            category=Category.FOOD,
            price=11000,
            satisfaction_score=81.0,
            dietary_tags=frozenset({"halal", "vegetarian"}),
            merchant_id="m_dallas_01",
            merchant_name="Ayam Penyet Mas Brow",
            canteen_name="Kantin Dallas",
            faculty="RIK UI",
            calories=440,
            description="Paket sarapan hemat",
            is_available=True,
        ),
        MenuItem(
            id="dallas_bev_01",
            name="Es Teh Manis Jumbo",
            category=Category.BEVERAGE,
            price=3000,
            satisfaction_score=78.0,
            dietary_tags=frozenset({"halal", "vegetarian"}),
            merchant_id="m_dallas_01",
            merchant_name="Ayam Penyet Mas Brow",
            canteen_name="Kantin Dallas",
            faculty="RIK UI",
            calories=120,
            description="Es teh manis segar",
            is_available=True,
        ),
        MenuItem(
            id="dallas_snack_01",
            name="Tahu Goreng Krispi",
            category=Category.SNACK,
            price=4000,
            satisfaction_score=75.0,
            dietary_tags=frozenset({"halal", "vegetarian"}),
            merchant_id="m_dallas_01",
            merchant_name="Ayam Penyet Mas Brow",
            canteen_name="Kantin Dallas",
            faculty="RIK UI",
            calories=210,
            description="Tahu pong renyah",
            is_available=True,
        ),
        MenuItem(
            id="takor_food_01",
            name="Nasi Telur Pontianak Takor",
            category=Category.FOOD,
            price=12000,
            satisfaction_score=85.0,
            dietary_tags=frozenset({"halal"}),
            merchant_id="m_takor_01",
            merchant_name="Bento Ekonomis Takor",
            canteen_name="Kantin Takor",
            faculty="FEB UI",
            calories=500,
            description="Nasi telur kecap gurih",
            is_available=True,
        ),
        MenuItem(
            id="takor_bev_01",
            name="Es Jeruk Peras Takor",
            category=Category.BEVERAGE,
            price=4000,
            satisfaction_score=82.0,
            dietary_tags=frozenset({"halal", "vegetarian"}),
            merchant_id="m_takor_01",
            merchant_name="Bento Ekonomis Takor",
            canteen_name="Kantin Takor",
            faculty="FEB UI",
            calories=110,
            description="Jeruk peras murni dingin",
            is_available=True,
        ),
        MenuItem(
            id="dallas_sold_out_01",
            name="Nasi Bebek Madura (Habis)",
            category=Category.FOOD,
            price=20000,
            satisfaction_score=92.0,
            dietary_tags=frozenset({"halal", "spicy"}),
            merchant_id="m_dallas_01",
            merchant_name="Ayam Penyet Mas Brow",
            canteen_name="Kantin Dallas",
            faculty="RIK UI",
            calories=700,
            description="Bebek bumbu hitam",
            is_available=False,
        ),
    ]


@pytest.fixture
def sample_merchants(sample_menu_items: List[MenuItem]) -> List[Merchant]:
    """Provides a list of Merchant objects with nested menu items."""
    dallas_items = [it for it in sample_menu_items if it.canteen_name == "Kantin Dallas"]
    takor_items = [it for it in sample_menu_items if it.canteen_name == "Kantin Takor"]
    return [
        Merchant(
            id="m_dallas_01",
            name="Ayam Penyet Mas Brow",
            canteen_id="dallas",
            canteen_name="Kantin Dallas",
            faculty="RIK UI",
            rating=4.7,
            items=dallas_items,
            description="Spesialis ayam penyet RIK",
        ),
        Merchant(
            id="m_takor_01",
            name="Bento Ekonomis Takor",
            canteen_id="takor",
            canteen_name="Kantin Takor",
            faculty="FEB UI",
            rating=4.5,
            items=takor_items,
            description="Menu bento hemat FEB",
        ),
    ]


@pytest.fixture
def temp_json_file(tmp_path: Path) -> Callable[[Any, str], str]:
    """Factory fixture to serialize arbitrary data to a temporary JSON file and return path."""
    def _create(data: Any, filename: str = "test_merchants.json") -> str:
        filepath = tmp_path / filename
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        return str(filepath)
    return _create


@pytest.fixture
def sample_merchants_raw_dict() -> Dict[str, Any]:
    """Returns a raw valid merchant dictionary structure for file loading tests."""
    return {
        "merchants": [
            {
                "id": "m_test_01",
                "name": "Warung Test UI",
                "canteen_id": "test_canteen",
                "canteen_name": "Kantin Test",
                "faculty": "Fasilkom UI",
                "rating": 4.8,
                "description": "Warung untuk pengujian unit test",
                "items": [
                    {
                        "id": "test_food_01",
                        "name": "Nasi Goreng Test",
                        "category": "food",
                        "price": 15000,
                        "satisfaction_score": 88.0,
                        "dietary_tags": ["halal"],
                        "calories": 550,
                        "description": "Nasi goreng lezat",
                        "is_available": True,
                    },
                    {
                        "id": "test_bev_01",
                        "name": "Es Teh Test",
                        "category": "beverage",
                        "price": 3000,
                        "satisfaction_score": 75.0,
                        "dietary_tags": ["halal", "vegetarian"],
                        "calories": 100,
                        "description": "Es teh manis",
                        "is_available": True,
                    },
                ],
            }
        ]
    }


@pytest.fixture
def knapsack_greedy_failure_items() -> List[MenuItem]:
    """Items engineered where greedy algorithm fails but DP knapsack finds optimal subset.

    Item G: Price 6,000, Sat 60.0 (Ratio = 0.0100)
    Item A: Price 5,000, Sat 48.0 (Ratio = 0.0096)
    Item B: Price 5,000, Sat 48.0 (Ratio = 0.0096)
    Budget = 10,000.
    Greedy picks Item G (Sat 60.0). Remaining 4,000 cannot pick A or B. Total Sat = 60.0.
    Optimal DP picks Item A + Item B (Cost 10,000, Sat 96.0). Total Sat = 96.0.
    """
    return [
        MenuItem(
            id="item_greedy",
            name="Item Greedy Bait",
            category=Category.FOOD,
            price=6000,
            satisfaction_score=60.0,
            dietary_tags=frozenset({"halal"}),
            merchant_id="m1",
            merchant_name="M",
            canteen_name="Dallas",
            faculty="RIK",
        ),
        MenuItem(
            id="item_opt_a",
            name="Item Optimal A",
            category=Category.FOOD,
            price=5000,
            satisfaction_score=48.0,
            dietary_tags=frozenset({"halal"}),
            merchant_id="m1",
            merchant_name="M",
            canteen_name="Dallas",
            faculty="RIK",
        ),
        MenuItem(
            id="item_opt_b",
            name="Item Optimal B",
            category=Category.FOOD,
            price=5000,
            satisfaction_score=48.0,
            dietary_tags=frozenset({"halal"}),
            merchant_id="m1",
            merchant_name="M",
            canteen_name="Dallas",
            faculty="RIK",
        ),
    ]


@pytest.fixture
def synthetic_edge_case_items() -> Dict[str, MenuItem]:
    """Provides individual edge-case MenuItem fixtures."""
    return {
        "zero_price": MenuItem(
            id="free_water",
            name="Air Putih Gratis",
            category=Category.BEVERAGE,
            price=0,
            satisfaction_score=30.0,
            dietary_tags=frozenset({"halal", "vegetarian"}),
            merchant_id="m1",
            merchant_name="M",
            canteen_name="Dallas",
            faculty="RIK",
        ),
        "expensive": MenuItem(
            id="sultan_steak",
            name="Wagyu Steak Sultan",
            category=Category.FOOD,
            price=150000,
            satisfaction_score=99.0,
            dietary_tags=frozenset({"halal"}),
            merchant_id="m1",
            merchant_name="M",
            canteen_name="Dallas",
            faculty="RIK",
        ),
        "snack_cheap": MenuItem(
            id="kerupuk",
            name="Kerupuk Putih",
            category=Category.SNACK,
            price=1000,
            satisfaction_score=50.0,
            dietary_tags=frozenset({"halal", "vegetarian"}),
            merchant_id="m1",
            merchant_name="M",
            canteen_name="Dallas",
            faculty="RIK",
        ),
    }


@pytest.fixture
def corrupt_dataset_factory(tmp_path: Path) -> Callable[[str], str]:
    """Factory generating various invalid or malformed JSON dataset files for testing."""
    def _create(anomaly_type: str) -> str:
        filepath = tmp_path / f"corrupt_{anomaly_type}.json"
        if anomaly_type == "nonexistent":
            return str(tmp_path / "does_not_exist_9999.json")
        elif anomaly_type == "malformed_syntax":
            filepath.write_text('{"merchants": [{"id": "unclosed', encoding="utf-8")
        elif anomaly_type == "empty_json":
            filepath.write_text("{}", encoding="utf-8")
        elif anomaly_type == "empty_merchants":
            filepath.write_text(json.dumps({"merchants": []}), encoding="utf-8")
        elif anomaly_type == "top_level_string":
            filepath.write_text('"just a string"', encoding="utf-8")
        elif anomaly_type == "top_level_missing_merchants":
            filepath.write_text(json.dumps({"wrong_key": []}), encoding="utf-8")
        elif anomaly_type == "merchant_not_object":
            filepath.write_text(json.dumps({"merchants": ["not a dict"]}), encoding="utf-8")
        elif anomaly_type == "missing_merchant_name":
            filepath.write_text(json.dumps({"merchants": [{"id": "m1"}]}), encoding="utf-8")
        elif anomaly_type == "invalid_rating_type":
            filepath.write_text(json.dumps({
                "merchants": [{
                    "id": "m1", "name": "M", "canteen_name": "C", "faculty": "F",
                    "rating": "four_point_five", "items": []
                }]
            }), encoding="utf-8")
        elif anomaly_type == "rating_out_of_bounds":
            filepath.write_text(json.dumps({
                "merchants": [{
                    "id": "m1", "name": "M", "canteen_name": "C", "faculty": "F",
                    "rating": 5.8, "items": []
                }]
            }), encoding="utf-8")
        elif anomaly_type == "missing_item_price":
            filepath.write_text(json.dumps({
                "merchants": [{
                    "id": "m1", "name": "M", "canteen_name": "C", "faculty": "F",
                    "rating": 4.0, "items": [{"id": "i1", "name": "Nasi", "category": "food"}]
                }]
            }), encoding="utf-8")
        elif anomaly_type == "missing_keys":
            filepath.write_text(json.dumps({
                "merchants": [{
                    "name": "Incomplete Merchant",
                    "items": [{"name": "Item without price"}]
                }]
            }), encoding="utf-8")
        elif anomaly_type == "negative_price":
            filepath.write_text(json.dumps({
                "merchants": [{
                    "id": "m1", "name": "M", "canteen_name": "C", "faculty": "F",
                    "rating": 4.0, "items": [{
                        "id": "i1", "name": "Nasi", "category": "food", "price": -5000,
                        "satisfaction_score": 80.0
                    }]
                }]
            }), encoding="utf-8")
        elif anomaly_type == "negative_item_price":
            filepath.write_text(json.dumps({
                "merchants": [{
                    "id": "m1", "name": "M", "canteen_name": "C", "faculty": "F",
                    "rating": 4.0, "items": [{
                        "id": "i1", "name": "Nasi", "category": "food", "price": -5000,
                        "satisfaction_score": 80.0
                    }]
                }]
            }), encoding="utf-8")
        elif anomaly_type == "float_item_price":
            filepath.write_text(json.dumps({
                "merchants": [{
                    "id": "m1", "name": "M", "canteen_name": "C", "faculty": "F",
                    "rating": 4.0, "items": [{
                        "id": "i1", "name": "Nasi", "category": "food", "price": 12500.5,
                        "satisfaction_score": 80.0
                    }]
                }]
            }), encoding="utf-8")
        elif anomaly_type == "invalid_category":
            filepath.write_text(json.dumps({
                "merchants": [{
                    "id": "m1", "name": "M", "canteen_name": "C", "faculty": "F",
                    "rating": 4.0, "items": [{
                        "id": "i1", "name": "Nasi", "category": "dessert_not_valid",
                        "price": 10000, "satisfaction_score": 80.0
                    }]
                }]
            }), encoding="utf-8")
        elif anomaly_type == "satisfaction_out_of_bounds":
            filepath.write_text(json.dumps({
                "merchants": [{
                    "id": "m1", "name": "M", "canteen_name": "C", "faculty": "F",
                    "rating": 4.0, "items": [{
                        "id": "i1", "name": "Nasi", "category": "food",
                        "price": 10000, "satisfaction_score": 120.0
                    }]
                }]
            }), encoding="utf-8")
        elif anomaly_type == "invalid_dietary_tags":
            filepath.write_text(json.dumps({
                "merchants": [{
                    "id": "m1", "name": "M", "canteen_name": "C", "faculty": "F",
                    "rating": 4.0, "items": [{
                        "id": "i1", "name": "Nasi", "category": "food",
                        "price": 10000, "satisfaction_score": 80.0, "dietary_tags": 12345
                    }]
                }]
            }), encoding="utf-8")
        else:
            raise ValueError(f"Unknown anomaly type: {anomaly_type}")
        return str(filepath)
    return _create


@pytest.fixture
def app():
    """Shared application fixture for Flask web testing."""
    from app import create_app
    flask_app = create_app({"TESTING": True})
    return flask_app


@pytest.fixture
def client(app):
    """Shared Flask test client fixture."""
    return app.test_client()


@pytest.fixture
def runner(app):
    """Shared Flask test CLI runner fixture."""
    return app.test_cli_runner()

