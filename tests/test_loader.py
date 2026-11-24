"""Unit test suite for core/loader.py (Data Loader & Schema Validation).

Tests:
1. Loading real survey data from data/merchants.json
2. Exception hierarchy and custom error raises
3. Schema constraints, data types, and value bounds
4. Strict mode vs Non-strict mode behaviors
5. MenuItem immutability and post-init normalizations
6. Helper functions: extract_all_items and filter_items
"""

from dataclasses import FrozenInstanceError
from pathlib import Path
from typing import Any, Callable, Dict, List
import pytest

from core.loader import (
    Category,
    DataFileNotFoundError,
    DataValidationError,
    JSONParseError,
    MealFinderDataError,
    MenuItem,
    Merchant,
    extract_all_items,
    filter_items,
    load_merchants,
)


class TestRealDatasetLoading:
    """Verifies that the actual project survey dataset in data/merchants.json loads and validates."""

    def test_load_real_merchants_success(self):
        dataset_path = Path("data/merchants.json")
        assert dataset_path.is_file(), "data/merchants.json must exist in repository root"
        merchants = load_merchants(dataset_path, strict=True)
        assert isinstance(merchants, list)
        assert len(merchants) >= 6, "Expected at least 6 merchants in real dataset"

    def test_real_merchants_canteen_coverage(self):
        merchants = load_merchants("data/merchants.json", strict=True)
        canteen_names = {m.canteen_name for m in merchants}
        expected_canteens = {"Dallas", "Takor", "Kansas", "Pusgiwa", "Kantek", "Balgebun"}
        for expected in expected_canteens:
            assert any(expected.lower() in c.lower() for c in canteen_names), f"Missing canteen {expected}"

    def test_real_merchants_all_categories_present(self):
        merchants = load_merchants("data/merchants.json", strict=True)
        all_items = extract_all_items(merchants, only_available=False)
        categories = {it.category for it in all_items}
        assert Category.FOOD in categories
        assert Category.BEVERAGE in categories
        assert Category.SNACK in categories

    def test_real_merchants_numeric_bounds(self):
        merchants = load_merchants("data/merchants.json", strict=True)
        for m in merchants:
            assert 0.0 <= m.rating <= 5.0
            for it in m.items:
                assert isinstance(it.price, int)
                assert it.price > 0
                assert 0.0 <= it.satisfaction_score <= 100.0


class TestExceptionHierarchy:
    """Verifies custom exception inheritance and file loading errors."""

    def test_exception_inheritance(self):
        assert issubclass(DataFileNotFoundError, MealFinderDataError)
        assert issubclass(DataFileNotFoundError, FileNotFoundError)
        assert issubclass(JSONParseError, MealFinderDataError)
        assert issubclass(DataValidationError, MealFinderDataError)

    def test_nonexistent_file_raises_data_file_not_found(self, corrupt_dataset_factory: Callable[[str], str]):
        bad_path = corrupt_dataset_factory("nonexistent")
        with pytest.raises(DataFileNotFoundError):
            load_merchants(bad_path)

    def test_malformed_json_raises_json_parse_error(self, corrupt_dataset_factory: Callable[[str], str]):
        bad_path = corrupt_dataset_factory("malformed_syntax")
        with pytest.raises(JSONParseError):
            load_merchants(bad_path)


class TestSchemaValidation:
    """Verifies schema validation on invalid, incomplete, or corrupted records."""

    def test_top_level_invalid_types(self, corrupt_dataset_factory: Callable[[str], str]):
        path = corrupt_dataset_factory("top_level_string")
        with pytest.raises(DataValidationError):
            load_merchants(path)

    def test_top_level_dict_missing_merchants_key(self, corrupt_dataset_factory: Callable[[str], str]):
        path = corrupt_dataset_factory("top_level_missing_merchants")
        with pytest.raises(DataValidationError):
            load_merchants(path)

    def test_merchant_not_object(self, corrupt_dataset_factory: Callable[[str], str]):
        path = corrupt_dataset_factory("merchant_not_object")
        with pytest.raises(DataValidationError):
            load_merchants(path)

    def test_merchant_missing_required_fields(self, corrupt_dataset_factory: Callable[[str], str]):
        path = corrupt_dataset_factory("missing_merchant_name")
        with pytest.raises(DataValidationError):
            load_merchants(path)

    def test_invalid_merchant_rating(self, corrupt_dataset_factory: Callable[[str], str]):
        path_type = corrupt_dataset_factory("invalid_rating_type")
        with pytest.raises(DataValidationError):
            load_merchants(path_type)

        path_bounds = corrupt_dataset_factory("rating_out_of_bounds")
        with pytest.raises(DataValidationError):
            load_merchants(path_bounds)

    def test_item_missing_required_fields(self, corrupt_dataset_factory: Callable[[str], str]):
        path = corrupt_dataset_factory("missing_item_price")
        with pytest.raises(DataValidationError):
            load_merchants(path)

    def test_item_negative_or_float_price(self, corrupt_dataset_factory: Callable[[str], str]):
        path_neg = corrupt_dataset_factory("negative_item_price")
        with pytest.raises(DataValidationError):
            load_merchants(path_neg)

        path_float = corrupt_dataset_factory("float_item_price")
        with pytest.raises(DataValidationError):
            load_merchants(path_float)

    def test_item_invalid_category(self, corrupt_dataset_factory: Callable[[str], str]):
        path = corrupt_dataset_factory("invalid_category")
        with pytest.raises(DataValidationError):
            load_merchants(path)

    def test_item_satisfaction_out_of_bounds(self, corrupt_dataset_factory: Callable[[str], str]):
        path = corrupt_dataset_factory("satisfaction_out_of_bounds")
        with pytest.raises(DataValidationError):
            load_merchants(path)

    def test_item_invalid_dietary_tags_type(self, corrupt_dataset_factory: Callable[[str], str]):
        path = corrupt_dataset_factory("invalid_dietary_tags")
        with pytest.raises(DataValidationError):
            load_merchants(path)


class TestStrictModeVsNonStrict:
    """Verifies strict parameter behavior when encountering empty collections."""

    def test_empty_merchants_strict_raises(self, temp_json_file: Callable[[Any, str], str]):
        path = temp_json_file({"merchants": []}, "empty_merchants.json")
        with pytest.raises(DataValidationError, match="Merchant list cannot be empty"):
            load_merchants(path, strict=True)

    def test_empty_merchants_non_strict_returns_empty_list(self, temp_json_file: Callable[[Any, str], str]):
        path = temp_json_file({"merchants": []}, "empty_merchants_nonstrict.json")
        result = load_merchants(path, strict=False)
        assert result == []

    def test_merchant_empty_items_strict_raises(self, temp_json_file: Callable[[Any, str], str]):
        data = {
            "merchants": [{
                "id": "m1", "name": "Empty Stall", "canteen_name": "Dallas",
                "faculty": "RIK", "rating": 4.0, "items": []
            }]
        }
        path = temp_json_file(data, "empty_items_strict.json")
        with pytest.raises(DataValidationError, match="must contain at least 1 menu item"):
            load_merchants(path, strict=True)

    def test_merchant_empty_items_non_strict_allowed(self, temp_json_file: Callable[[Any, str], str]):
        data = {
            "merchants": [{
                "id": "m1", "name": "Empty Stall", "canteen_name": "Dallas",
                "faculty": "RIK", "rating": 4.0, "items": []
            }]
        }
        path = temp_json_file(data, "empty_items_nonstrict.json")
        result = load_merchants(path, strict=False)
        assert len(result) == 1
        assert result[0].items == []


class TestMenuItemInvariants:
    """Verifies immutability and post-init normalizations of MenuItem."""

    def test_menu_item_is_frozen(self, sample_menu_items: List[MenuItem]):
        item = sample_menu_items[0]
        with pytest.raises((FrozenInstanceError, AttributeError)):
            item.price = 25000  # type: ignore

    def test_menu_item_normalizes_string_category(self):
        item = MenuItem(
            id="i1", name="Teh", category="beverage", price=3000, satisfaction_score=70.0,  # type: ignore
            dietary_tags=frozenset(), merchant_id="m", merchant_name="M", canteen_name="C", faculty="F"
        )
        assert item.category == Category.BEVERAGE

    def test_menu_item_normalizes_dietary_tags_to_frozenset(self):
        item = MenuItem(
            id="i2", name="Tahu", category=Category.FOOD, price=5000, satisfaction_score=75.0,
            dietary_tags=["HALAL", " Vegetarian "],  # type: ignore
            merchant_id="m", merchant_name="M", canteen_name="C", faculty="F"
        )
        assert isinstance(item.dietary_tags, frozenset)
        assert item.dietary_tags == frozenset({"halal", "vegetarian"})


class TestHelperFunctions:
    """Verifies extract_all_items and filter_items helper functions."""

    def test_extract_all_items_respects_only_available(self, sample_merchants: List[Merchant]):
        all_items = extract_all_items(sample_merchants, only_available=False)
        avail_items = extract_all_items(sample_merchants, only_available=True)
        assert len(all_items) == 7
        assert len(avail_items) == 6
        assert all(it.is_available for it in avail_items)

    def test_filter_items_by_max_price(self, sample_menu_items: List[MenuItem]):
        cheap_items = filter_items(sample_menu_items, max_price=4000)
        assert len(cheap_items) > 0
        assert all(it.price <= 4000 for it in cheap_items)

    def test_filter_items_by_canteen_substring_case_insensitive(self, sample_menu_items: List[MenuItem]):
        dallas_items = filter_items(sample_menu_items, canteen_name="dAlLaS")
        assert len(dallas_items) > 0
        assert all("dallas" in it.canteen_name.lower() for it in dallas_items)

    def test_filter_items_by_dietary_tags(self, sample_menu_items: List[MenuItem]):
        veg_items = filter_items(sample_menu_items, required_tags={"vegetarian"})
        assert len(veg_items) > 0
        assert all("vegetarian" in it.dietary_tags for it in veg_items)

    def test_filter_items_combined(self, sample_menu_items: List[MenuItem]):
        filtered = filter_items(
            sample_menu_items, max_price=12000, canteen_name="Dallas", required_tags={"vegetarian"}
        )
        assert len(filtered) > 0
        for it in filtered:
            assert it.price <= 12000
            assert "dallas" in it.canteen_name.lower()
            assert "vegetarian" in it.dietary_tags
