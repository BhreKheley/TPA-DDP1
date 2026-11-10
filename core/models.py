"""Modul Model Data (Data Models) - Smart Meal Finder
Dasar-Dasar Pemrograman 1 (DDP1) Gasal 2026/2027 - Kelompok 5

Modul ini menyediakan referensi dan re-export entitas data utama:
- Category: Enumerasi kategori menu (food, beverage, snack).
- MenuItem: Model immutable (frozen dataclass) untuk satu item menu makanan/minuman.
- Merchant: Model stan penjual kantin kampus UI beserta daftar menunya.
- Exception Hierarchy: Penanganan error terstruktur untuk validasi data.

Kontributor:
- Naisya Alikha Putri (NPM: 2606888276) - Desain Skema & Entitas Data
- Bhre Nabil Faeyza (NPM: 2606887563) - Reviewer & Integrasi Logika
"""

from core.loader import (
    Category,
    MenuItem,
    Merchant,
    MealFinderDataError,
    DataFileNotFoundError,
    JSONParseError,
    DataValidationError,
)

__all__ = [
    "Category",
    "MenuItem",
    "Merchant",
    "MealFinderDataError",
    "DataFileNotFoundError",
    "JSONParseError",
    "DataValidationError",
]
