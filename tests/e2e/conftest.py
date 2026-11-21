"""Shared pytest fixtures and test data generators for E2E tests.

Provides realistic sample datasets for Universitas Indonesia campus canteens
(Dallas, Takor, Kansas, Pusgiwa, Texas, Fasilkom), corrupt dataset factories
for boundary testing, and Flask test client fixtures.
"""

import json
from pathlib import Path
from typing import Any, Dict, List
import pytest


# Comprehensive mock dataset representing the 6 UI canteens
SAMPLE_MERCHANTS_DICT: Dict[str, Any] = {
    "canteens": [
        {"id": "dallas", "name": "Dallas", "faculty": "Fisip"},
        {"id": "takor", "name": "Takor", "faculty": "FEB"},
        {"id": "kansas", "name": "Kansas", "faculty": "FIB"},
        {"id": "pusgiwa", "name": "Pusgiwa", "faculty": "UI Pusat"},
        {"id": "texas", "name": "Texas", "faculty": "FT"},
        {"id": "fasilkom", "name": "Fasilkom", "faculty": "Fasilkom"},
    ],
    "merchants": [
        {
            "id": "m_dallas_1",
            "name": "Ayam Geprek Mas Brow Dallas",
            "canteen_id": "dallas",
            "canteen_name": "Dallas",
            "faculty": "Fisip",
            "rating": 4.7,
            "description": "Ayam geprek pedas gurih khas anak Fisip",
            "items": [
                {
                    "id": "item_dallas_01",
                    "name": "Paket Nasi Ayam Geprek Level 2",
                    "category": "food",
                    "price": 15000,
                    "satisfaction_score": 8.8,
                    "dietary_tags": ["halal", "pedas"],
                    "calories": 650,
                    "description": "Nasi putih hangat dengan ayam geprek sambal bawang",
                    "is_available": True,
                },
                {
                    "id": "item_dallas_02",
                    "name": "Es Teh Manis Jumbo",
                    "category": "beverage",
                    "price": 3000,
                    "satisfaction_score": 7.5,
                    "dietary_tags": ["halal", "vegetarian"],
                    "calories": 120,
                    "description": "Es teh manis segar ukuran jumbo",
                    "is_available": True,
                },
                {
                    "id": "item_dallas_03",
                    "name": "Tempe Mendoan (3 pcs)",
                    "category": "snack",
                    "price": 5000,
                    "satisfaction_score": 8.0,
                    "dietary_tags": ["halal", "vegetarian"],
                    "calories": 250,
                    "description": "Tempe mendoan hangat dengan kecap rawit",
                    "is_available": True,
                },
                {
                    "id": "item_dallas_04",
                    "name": "Nasi Telur Dadar Krispi (Sold Out)",
                    "category": "food",
                    "price": 10000,
                    "satisfaction_score": 7.8,
                    "dietary_tags": ["halal"],
                    "calories": 450,
                    "description": "Nasi telur dadar krispi murah meriah",
                    "is_available": False,
                },
            ],
        },
        {
            "id": "m_takor_1",
            "name": "Bento Ekonomis Takor",
            "canteen_id": "takor",
            "canteen_name": "Takor",
            "faculty": "FEB",
            "rating": 4.5,
            "description": "Menu hemat lezat favorit anak ekonomi",
            "items": [
                {
                    "id": "item_takor_01",
                    "name": "Nasi Telur Bento Pontianak",
                    "category": "food",
                    "price": 12000,
                    "satisfaction_score": 8.5,
                    "dietary_tags": ["halal"],
                    "calories": 500,
                    "description": "Nasi dengan telur mata sapi disiram kecap bumbu",
                    "is_available": True,
                },
                {
                    "id": "item_takor_02",
                    "name": "Es Jeruk Peras Takor",
                    "category": "beverage",
                    "price": 4000,
                    "satisfaction_score": 8.0,
                    "dietary_tags": ["halal", "vegetarian"],
                    "calories": 110,
                    "description": "Jeruk peras asli dengan es",
                    "is_available": True,
                },
            ],
        },
        {
            "id": "m_kansas_1",
            "name": "Soto Betawi Sastra Kansas",
            "canteen_id": "kansas",
            "canteen_name": "Kansas",
            "faculty": "FIB",
            "rating": 4.6,
            "description": "Soto Betawi santan gurih legendaris FIB",
            "items": [
                {
                    "id": "item_kansas_01",
                    "name": "Soto Ayam Santan + Nasi",
                    "category": "food",
                    "price": 18000,
                    "satisfaction_score": 9.0,
                    "dietary_tags": ["halal"],
                    "calories": 580,
                    "description": "Soto ayam dengan kuah santan kaya rempah",
                    "is_available": True,
                },
                {
                    "id": "item_kansas_02",
                    "name": "Air Mineral Dingin 600ml",
                    "category": "beverage",
                    "price": 3000,
                    "satisfaction_score": 6.5,
                    "dietary_tags": ["halal", "vegetarian"],
                    "calories": 0,
                    "description": "Air mineral kemasan botol dingin",
                    "is_available": True,
                },
            ],
        },
        {
            "id": "m_pusgiwa_1",
            "name": "Warung Nasi Padang Pusgiwa",
            "canteen_id": "pusgiwa",
            "canteen_name": "Pusgiwa",
            "faculty": "UI Pusat",
            "rating": 4.8,
            "description": "Nasi Padang porsi kuli harga mahasiswa",
            "items": [
                {
                    "id": "item_pusgiwa_01",
                    "name": "Nasi Rendang Sapi Porsi Lengkap",
                    "category": "food",
                    "price": 22000,
                    "satisfaction_score": 9.5,
                    "dietary_tags": ["halal", "pedas"],
                    "calories": 750,
                    "description": "Nasi rendang daging sapi empuk sayur nangka dan sambal hijau",
                    "is_available": True,
                },
                {
                    "id": "item_pusgiwa_02",
                    "name": "Teh Manis Dingin",
                    "category": "beverage",
                    "price": 2500,
                    "satisfaction_score": 7.0,
                    "dietary_tags": ["halal", "vegetarian"],
                    "calories": 90,
                    "description": "Teh manis segar penyegar dahaga",
                    "is_available": True,
                },
            ],
        },
        {
            "id": "m_texas_1",
            "name": "Bebek & Ayam Penyet Texas Teknik",
            "canteen_id": "texas",
            "canteen_name": "Texas",
            "faculty": "FT",
            "rating": 4.7,
            "description": "Sambal ijo pedas nampol anak Teknik",
            "items": [
                {
                    "id": "item_texas_01",
                    "name": "Nasi Ayam Penyet Sambal Ijo",
                    "category": "food",
                    "price": 16000,
                    "satisfaction_score": 8.9,
                    "dietary_tags": ["halal", "pedas"],
                    "calories": 620,
                    "description": "Ayam goreng penyet sambal ijo khas FT",
                    "is_available": True,
                },
                {
                    "id": "item_texas_02",
                    "name": "Teh Botol Sosro Dingin",
                    "category": "beverage",
                    "price": 4000,
                    "satisfaction_score": 7.6,
                    "dietary_tags": ["halal", "vegetarian"],
                    "calories": 130,
                    "description": "Teh botol sosro dingin kaca",
                    "is_available": True,
                },
            ],
        },
        {
            "id": "m_fasilkom_1",
            "name": "Kantin Fasilkom Bistro",
            "canteen_id": "fasilkom",
            "canteen_name": "Fasilkom",
            "faculty": "Fasilkom",
            "rating": 4.9,
            "description": "Menu sehat higienis programmer Fasilkom",
            "items": [
                {
                    "id": "item_fasilkom_01",
                    "name": "Tahu Tempe Bakar Madu Organik",
                    "category": "food",
                    "price": 14000,
                    "satisfaction_score": 8.7,
                    "dietary_tags": ["halal", "vegetarian"],
                    "calories": 410,
                    "description": "Tahu tempe bakar sehat saus madu gurih",
                    "is_available": True,
                },
                {
                    "id": "item_fasilkom_02",
                    "name": "Jus Alpukat Kocok Madu",
                    "category": "beverage",
                    "price": 9000,
                    "satisfaction_score": 9.2,
                    "dietary_tags": ["halal", "vegetarian"],
                    "calories": 280,
                    "description": "Jus alpukat murni dengan topping madu",
                    "is_available": True,
                },
                {
                    "id": "item_fasilkom_03",
                    "name": "Kripik Jamur Crispy",
                    "category": "snack",
                    "price": 6000,
                    "satisfaction_score": 8.2,
                    "dietary_tags": ["halal", "vegetarian"],
                    "calories": 180,
                    "description": "Jamur tiram crispy gurih renyah",
                    "is_available": True,
                },
            ],
        },
    ],
}


@pytest.fixture(scope="session")
def sample_merchants_data() -> Dict[str, Any]:
    """Returns the comprehensive sample merchants dictionary."""
    return SAMPLE_MERCHANTS_DICT


@pytest.fixture
def temp_merchants_file(tmp_path: Path, sample_merchants_data: Dict[str, Any]) -> str:
    """Writes valid merchant data into a temporary JSON file and returns path."""
    json_path = tmp_path / "merchants.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(sample_merchants_data, f, indent=2)
    return str(json_path)


@pytest.fixture
def corrupt_dataset_factory(tmp_path: Path):
    """Factory creating various corrupt or anomaly datasets for boundary testing."""
    def _create(anomaly_type: str) -> str:
        file_path = tmp_path / f"corrupt_{anomaly_type}.json"
        
        if anomaly_type == "nonexistent":
            return str(tmp_path / "does_not_exist_999.json")
            
        elif anomaly_type == "empty_json":
            file_path.write_text("{}", encoding="utf-8")
            
        elif anomaly_type == "empty_merchants":
            file_path.write_text(json.dumps({"merchants": []}), encoding="utf-8")
            
        elif anomaly_type == "missing_keys":
            # Missing critical 'price' and 'id'
            data = {
                "merchants": [
                    {
                        "name": "Incomplete Merchant",
                        "items": [{"name": "Item without price"}]
                    }
                ]
            }
            file_path.write_text(json.dumps(data), encoding="utf-8")
            
        elif anomaly_type == "negative_price":
            data = {
                "merchants": [
                    {
                        "id": "m1",
                        "name": "Negative Price Merchant",
                        "canteen_name": "Dallas",
                        "faculty": "Fisip",
                        "rating": 4.0,
                        "items": [
                            {
                                "id": "neg_01",
                                "name": "Minus Price Dish",
                                "category": "food",
                                "price": -5000,
                                "satisfaction_score": 7.0,
                                "is_available": True
                            }
                        ]
                    }
                ]
            }
            file_path.write_text(json.dumps(data), encoding="utf-8")
            
        elif anomaly_type == "malformed_syntax":
            file_path.write_text('{"merchants": [ { "id": "unclosed', encoding="utf-8")
            
        elif anomaly_type == "invalid_category":
            data = {
                "merchants": [
                    {
                        "id": "m1",
                        "name": "Invalid Category Merchant",
                        "canteen_name": "Takor",
                        "faculty": "FEB",
                        "rating": 4.0,
                        "items": [
                            {
                                "id": "inv_01",
                                "name": "Alien Dish",
                                "category": "dessert_not_in_schema",
                                "price": 10000,
                                "satisfaction_score": 8.0,
                                "is_available": True
                            }
                        ]
                    }
                ]
            }
            file_path.write_text(json.dumps(data), encoding="utf-8")
            
        else:
            raise ValueError(f"Unknown anomaly type: {anomaly_type}")
            
        return str(file_path)

    return _create


@pytest.fixture
def standalone_menu_items():
    """Generates a standalone list of MenuItem-compatible objects or dicts for direct engine testing."""
    items = []
    for merchant in SAMPLE_MERCHANTS_DICT["merchants"]:
        for it in merchant["items"]:
            items.append({
                "id": it["id"],
                "name": it["name"],
                "category": it["category"],
                "price": it["price"],
                "satisfaction_score": it["satisfaction_score"],
                "dietary_tags": set(it.get("dietary_tags", [])),
                "merchant_id": merchant["id"],
                "merchant_name": merchant["name"],
                "canteen_name": merchant["canteen_name"],
                "faculty": merchant["faculty"],
                "calories": it.get("calories"),
                "description": it.get("description", ""),
                "is_available": it.get("is_available", True),
            })
    return items


@pytest.fixture
def app():
    """Flask application fixture with progressive fallback handling."""
    # Attempt 1: app factory
    try:
        from app import create_app
        flask_app = create_app({"TESTING": True})
        return flask_app
    except (ImportError, AttributeError):
        pass

    # Attempt 2: app package level instance
    try:
        from app import app as flask_app
        flask_app.config["TESTING"] = True
        return flask_app
    except (ImportError, AttributeError):
        pass

    # Attempt 3: app.routes level instance
    try:
        from app.routes import app as flask_app
        flask_app.config["TESTING"] = True
        return flask_app
    except (ImportError, AttributeError):
        pass

    # Attempt 4: run.py level instance
    try:
        from run import app as flask_app
        flask_app.config["TESTING"] = True
        return flask_app
    except (ImportError, AttributeError):
        pytest.skip("Flask application not yet implemented (scheduled for Milestone 4).")


@pytest.fixture
def client(app):
    """Flask test client fixture."""
    return app.test_client()
