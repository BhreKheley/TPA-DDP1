"""Model data: entitas Merchant dan MenuItem, tanpa ketergantungan pada modul lain."""

from dataclasses import dataclass
from datetime import date, time
from enum import Enum
from typing import Optional, Tuple


class DataError(Exception):
    """Berkas data hilang, rusak, atau melanggar aturan kualitas data."""


class Category(str, Enum):
    FOOD = "food"
    BEVERAGE = "beverage"
    SNACK = "snack"

    @property
    def label(self) -> str:
        return {"food": "Makanan", "beverage": "Minuman", "snack": "Camilan"}[self.value]


@dataclass(frozen=True)
class MenuItem:
    id: str
    name: str
    category: Category
    price: int  # rupiah, bilangan bulat


@dataclass(frozen=True)
class Merchant:
    id: str
    name: str
    canteen: str
    items: Tuple[MenuItem, ...]
    updated_at: date  # tanggal harga terakhir dicek
    verified: bool = False  # True hanya jika harga sudah dicek di lapangan
    opens: Optional[time] = None
    closes: Optional[time] = None  # lebih kecil dari opens berarti lewat tengah malam
    note: str = ""
