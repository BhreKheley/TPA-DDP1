"""Modul Pemuat & Validator Data (Data Loader & Schema Validation)
Smart Meal Finder - DDP1 Gasal 2026/2027 Kelompok 5

Modul ini bertanggung jawab membaca berkas `data/merchants.json` hasil survei
lapangan kantin kampus Universitas Indonesia, memvalidasi integritas data, dan
mengubahnya menjadi objek Python terstruktur (MenuItem dan Merchant).

Konsep Pembelajaran DDP1 yang Diterapkan:
1. Pemrosesan Berkas (File I/O): Membaca berkas JSON dengan encoding UTF-8.
2. Penanganan Eksepsi (Exception Handling): Hierarki kustom untuk mendeteksi
   berkas hilang, JSON tidak valid, dan pelanggaran batasan data/skema.
3. Immutabilitas (Immutable Dataclass): Mengunci MenuItem agar thread-safe dan bebas efek samping.
4. Normalisasi String & Enum: Memastikan kategori dan tag konsisten dalam huruf kecil.

Kontributor:
- Naisya Alikha Putri (NPM: 2606888276) - Desain Skema & Entitas Data
- Bhre Nabil Faeyza (NPM: 2606887563) - Reviewer PR #1 & Pengujian
"""

from dataclasses import dataclass, field
from enum import Enum
import json
from pathlib import Path
from typing import FrozenSet, List, Optional, Set, Union


class Category(str, Enum):
    """Enumeration of valid menu item categories."""
    FOOD = "food"
    BEVERAGE = "beverage"
    SNACK = "snack"


class MealFinderDataError(Exception):
    """Base exception for all data loading and validation errors."""
    pass


class DataFileNotFoundError(MealFinderDataError, FileNotFoundError):
    """Raised when the specified dataset file is not found on disk."""
    pass


class JSONParseError(MealFinderDataError):
    """Raised when the dataset file contains malformed JSON syntax."""
    pass


class DataValidationError(MealFinderDataError):
    """Raised when the dataset schema or data integrity validation fails."""
    pass


@dataclass(frozen=True)
class MenuItem:
    """Immutable data model representing a single menu item in a UI canteen stall.
    
    Attributes:
        id: Unique identifier for the menu item.
        name: Name of the food, beverage, or snack.
        category: Category enum (FOOD, BEVERAGE, SNACK).
        price: Price in Indonesian Rupiah (strictly integer >= 0).
        satisfaction_score: Numeric score (0.0 to 100.0) reflecting utility/taste/portion.
        dietary_tags: FrozenSet of lowercase dietary labels (e.g. 'halal', 'vegetarian').
        merchant_id: Identifier of the selling merchant.
        merchant_name: Name of the selling merchant stall.
        canteen_name: Name of the host campus canteen (e.g. 'Kantin Dallas').
        faculty: Faculty or campus zone (e.g. 'RIK UI', 'Fasilkom UI').
        calories: Optional estimated caloric content in kcal.
        description: Informative description of the item.
        is_available: Operational availability status (default True).
    """
    id: str
    name: str
    category: Category
    price: int
    satisfaction_score: float
    dietary_tags: FrozenSet[str]
    merchant_id: str
    merchant_name: str
    canteen_name: str
    faculty: str
    calories: Optional[int] = None
    description: str = ""
    is_available: bool = True

    def __post_init__(self) -> None:
        """Enforces type and value invariants for frozen MenuItem."""
        # Normalize dietary_tags to frozenset of lowercased strings
        if not isinstance(self.dietary_tags, frozenset):
            tags = (
                frozenset(str(t).strip().lower() for t in self.dietary_tags)
                if self.dietary_tags
                else frozenset()
            )
            object.__setattr__(self, "dietary_tags", tags)

        # Normalize category to Category enum
        if isinstance(self.category, str) and not isinstance(self.category, Category):
            try:
                object.__setattr__(self, "category", Category(self.category.strip().lower()))
            except ValueError:
                raise DataValidationError(f"Invalid category: '{self.category}'")
        elif not isinstance(self.category, Category):
            raise DataValidationError(f"Category must be Category enum or valid string, got {type(self.category).__name__}")


@dataclass
class Merchant:
    """Data model representing a canteen food/beverage stall.
    
    Attributes:
        id: Unique identifier for the merchant.
        name: Name of the merchant stall.
        canteen_id: Unique slug for the canteen.
        canteen_name: Display name of the canteen.
        faculty: Faculty or zone associated with the canteen.
        rating: Customer rating between 0.0 and 5.0.
        items: List of MenuItem objects offered by this merchant.
        description: Brief description of the merchant stall and specialties.
    """
    id: str
    name: str
    canteen_id: str
    canteen_name: str
    faculty: str
    rating: float
    items: List[MenuItem] = field(default_factory=list)
    description: str = ""


def load_merchants(filepath: Union[str, Path], strict: bool = True) -> List[Merchant]:
    """Loads and validates UI canteen merchants and menu items from a JSON file.
    
    Args:
        filepath: Path to the JSON data file.
        strict: If True, enforces strict validation (non-empty lists, all fields present).
        
    Returns:
        List of validated Merchant objects.
        
    Raises:
        DataFileNotFoundError: If filepath does not exist or is not a file.
        JSONParseError: If file content is not valid JSON syntax.
        DataValidationError: If JSON data fails schema or domain constraints.
    """
    path = Path(filepath)
    if not path.is_file():
        raise DataFileNotFoundError(f"Data file not found: {filepath}")

    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except json.JSONDecodeError as err:
        raise JSONParseError(f"Failed to parse JSON file {filepath}: {err}") from err

    # Normalize top-level structure: accept either list or dict with 'merchants' key
    if isinstance(data, list):
        merchants_raw = data
    elif isinstance(data, dict):
        if "merchants" in data and isinstance(data["merchants"], list):
            merchants_raw = data["merchants"]
        else:
            raise DataValidationError("Top-level JSON dictionary must contain a 'merchants' list")
    else:
        raise DataValidationError(f"Expected top-level JSON list or dict with 'merchants', got {type(data).__name__}")

    if not merchants_raw:
        if strict:
            raise DataValidationError("Merchant list cannot be empty when strict=True")
        return []

    merchants: List[Merchant] = []

    for m_idx, m_dict in enumerate(merchants_raw):
        if not isinstance(m_dict, dict):
            raise DataValidationError(f"Merchant at index {m_idx} must be a JSON object, got {type(m_dict).__name__}")

        m_id = m_dict.get("id")
        m_name = m_dict.get("name")
        canteen_name = m_dict.get("canteen_name")
        faculty = m_dict.get("faculty")
        rating_raw = m_dict.get("rating")
        items_raw = m_dict.get("items")
        canteen_id = m_dict.get("canteen_id")
        description = m_dict.get("description", "")

        if not m_id or not isinstance(m_id, str):
            raise DataValidationError(f"Merchant at index {m_idx} missing valid 'id'")
        if not m_name or not isinstance(m_name, str):
            raise DataValidationError(f"Merchant '{m_id}' missing valid 'name'")
        if not canteen_name or not isinstance(canteen_name, str):
            raise DataValidationError(f"Merchant '{m_name}' missing valid 'canteen_name'")
        if not faculty or not isinstance(faculty, str):
            raise DataValidationError(f"Merchant '{m_name}' missing valid 'faculty'")

        if not canteen_id:
            canteen_id = canteen_name.lower().replace(" ", "_")

        if rating_raw is None or not isinstance(rating_raw, (int, float)) or isinstance(rating_raw, bool):
            raise DataValidationError(f"Merchant '{m_name}' missing valid numeric 'rating'")
        rating = float(rating_raw)
        if not (0.0 <= rating <= 5.0):
            raise DataValidationError(f"Merchant '{m_name}' rating {rating} outside valid range [0.0, 5.0]")

        if items_raw is None or not isinstance(items_raw, list):
            raise DataValidationError(f"Merchant '{m_name}' missing 'items' list")
        if strict and len(items_raw) == 0:
            raise DataValidationError(f"Merchant '{m_name}' must contain at least 1 menu item when strict=True")

        parsed_items: List[MenuItem] = []
        for it_idx, it_dict in enumerate(items_raw):
            if not isinstance(it_dict, dict):
                raise DataValidationError(f"Item {it_idx} in merchant '{m_name}' must be an object")

            it_id = it_dict.get("id")
            it_name = it_dict.get("name")
            category_raw = it_dict.get("category")
            price_raw = it_dict.get("price")
            satisfaction_raw = it_dict.get("satisfaction_score")
            dietary_raw = it_dict.get("dietary_tags", [])
            calories_raw = it_dict.get("calories")
            it_desc = it_dict.get("description", "")
            is_available = it_dict.get("is_available", True)

            if not it_id or not isinstance(it_id, str):
                raise DataValidationError(f"Item {it_idx} in merchant '{m_name}' missing valid 'id'")
            if not it_name or not isinstance(it_name, str):
                raise DataValidationError(f"Item '{it_id}' in merchant '{m_name}' missing valid 'name'")

            # Category validation
            if isinstance(category_raw, Category):
                category = category_raw
            elif isinstance(category_raw, str):
                try:
                    category = Category(category_raw.strip().lower())
                except ValueError:
                    raise DataValidationError(f"Item '{it_name}' has invalid category '{category_raw}'")
            else:
                raise DataValidationError(f"Item '{it_name}' missing valid 'category'")

            # Price validation (strictly non-negative integer)
            if price_raw is None or not isinstance(price_raw, int) or isinstance(price_raw, bool):
                raise DataValidationError(f"Item '{it_name}' price must be an integer, got {price_raw}")
            if price_raw < 0:
                raise DataValidationError(f"Item '{it_name}' price cannot be negative: {price_raw}")

            # Satisfaction score validation
            if satisfaction_raw is None or not isinstance(satisfaction_raw, (int, float)) or isinstance(satisfaction_raw, bool):
                raise DataValidationError(f"Item '{it_name}' satisfaction_score must be numeric, got {satisfaction_raw}")
            satisfaction_score = float(satisfaction_raw)
            if not (0.0 <= satisfaction_score <= 100.0):
                raise DataValidationError(f"Item '{it_name}' satisfaction_score {satisfaction_score} outside [0.0, 100.0]")

            # Dietary tags normalization
            if dietary_raw is None:
                dietary_tags = frozenset()
            elif isinstance(dietary_raw, (set, list, tuple, frozenset)):
                dietary_tags = frozenset(str(t).strip().lower() for t in dietary_raw)
            else:
                raise DataValidationError(f"Item '{it_name}' dietary_tags must be a list or set")

            calories = (
                int(calories_raw)
                if calories_raw is not None and isinstance(calories_raw, (int, float)) and not isinstance(calories_raw, bool)
                else None
            )

            menu_item = MenuItem(
                id=it_id,
                name=it_name,
                category=category,
                price=price_raw,
                satisfaction_score=satisfaction_score,
                dietary_tags=dietary_tags,
                merchant_id=it_dict.get("merchant_id") or m_id,
                merchant_name=it_dict.get("merchant_name") or m_name,
                canteen_name=it_dict.get("canteen_name") or canteen_name,
                faculty=it_dict.get("faculty") or faculty,
                calories=calories,
                description=str(it_desc),
                is_available=bool(is_available),
            )
            parsed_items.append(menu_item)

        merchant = Merchant(
            id=m_id,
            name=m_name,
            canteen_id=canteen_id,
            canteen_name=canteen_name,
            faculty=faculty,
            rating=rating,
            items=parsed_items,
            description=str(description),
        )
        merchants.append(merchant)

    return merchants


def extract_all_items(merchants: List[Merchant], only_available: bool = True) -> List[MenuItem]:
    """Extracts and flattens all menu items from a collection of merchants.
    
    Args:
        merchants: List of Merchant objects.
        only_available: If True, only returns items where is_available is True.
        
    Returns:
        List of MenuItem objects.
    """
    items: List[MenuItem] = []
    for merchant in merchants:
        for item in merchant.items:
            if not only_available or item.is_available:
                items.append(item)
    return items


def filter_items(
    items: List[MenuItem],
    max_price: Optional[int] = None,
    canteen_name: Optional[str] = None,
    required_tags: Optional[Set[str]] = None,
) -> List[MenuItem]:
    """Filters menu items according to budget, canteen, and dietary constraints.
    
    Args:
        items: List of MenuItem objects to filter.
        max_price: Optional maximum price threshold in Rupiah (inclusive).
        canteen_name: Optional canteen name substring filter (case-insensitive).
        required_tags: Optional set of required dietary tags (all must match).
        
    Returns:
        Filtered list of MenuItem objects.
    """
    filtered: List[MenuItem] = []
    norm_tags = {str(t).strip().lower() for t in required_tags} if required_tags else None
    canteen_query = str(canteen_name).strip().lower() if canteen_name else None

    for item in items:
        if max_price is not None and item.price > max_price:
            continue
        if canteen_query:
            item_canteen = item.canteen_name.lower()
            if canteen_query not in item_canteen and item_canteen not in canteen_query:
                continue
        if norm_tags:
            item_tags = {t.lower() for t in item.dietary_tags}
            if not norm_tags.issubset(item_tags):
                continue
        filtered.append(item)
    return filtered
