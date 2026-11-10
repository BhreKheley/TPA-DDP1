"""Smart Meal Finder - Core Module.

Contains data models, schema validation loader, and meal recommendation algorithms.
"""

from core.loader import (
    Category,
    MenuItem,
    Merchant,
    MealFinderDataError,
    DataFileNotFoundError,
    JSONParseError,
    DataValidationError,
    load_merchants,
    extract_all_items,
    filter_items,
)
from core.budget import (
    MealCombination,
    RecommendationResult,
    RecommendationError,
    knapsack_01_dp,
    recommend_meals,
)

__all__ = [
    "Category",
    "MenuItem",
    "Merchant",
    "MealFinderDataError",
    "DataFileNotFoundError",
    "JSONParseError",
    "DataValidationError",
    "load_merchants",
    "extract_all_items",
    "filter_items",
    "MealCombination",
    "RecommendationResult",
    "RecommendationError",
    "knapsack_01_dp",
    "recommend_meals",
]
