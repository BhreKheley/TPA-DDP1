"""Memuat dan memvalidasi data/merchants.json menjadi objek Merchant.

Harga tanpa tanggal pembaruan dan merchant tanpa kantin ditolak saat dimuat,
sesuai aturan kualitas data di rancangan.
"""

import json
from datetime import date, time
from pathlib import Path
from typing import Any, Dict, List, Set, Union

from core.models import Category, DataError, MenuItem, Merchant


def _text(raw: Dict[str, Any], key: str, where: str) -> str:
    value = raw.get(key)
    if not isinstance(value, str) or not value.strip():
        raise DataError(f"{where}: field '{key}' wajib berisi teks.")
    return value.strip()


def _clock(raw: Dict[str, Any], key: str, where: str):
    value = raw.get(key)
    if value is None:
        return None
    try:
        return time.fromisoformat(value)
    except (TypeError, ValueError):
        raise DataError(f"{where}: '{key}' harus berformat JJ:MM, misalnya 07:30.") from None


def _item(raw: Any, where: str, seen: Set[str]) -> MenuItem:
    if not isinstance(raw, dict):
        raise DataError(f"{where}: menu harus berupa objek.")
    item_id = _text(raw, "id", where)
    where = f"{where} / menu '{item_id}'"
    if item_id in seen:
        raise DataError(f"{where}: id menu dobel.")
    seen.add(item_id)
    price = raw.get("price")
    if isinstance(price, bool) or not isinstance(price, int) or price <= 0:
        raise DataError(f"{where}: 'price' harus bilangan bulat rupiah lebih dari 0, ditemukan {price!r}.")
    try:
        category = Category(raw.get("category"))
    except ValueError:
        valid = ", ".join(c.value for c in Category)
        raise DataError(f"{where}: 'category' harus salah satu dari {valid}.") from None
    return MenuItem(item_id, _text(raw, "name", where), category, price)


def _merchant(raw: Any, index: int, seen_items: Set[str], seen_ids: Set[str]) -> Merchant:
    if not isinstance(raw, dict):
        raise DataError(f"Merchant ke-{index + 1} harus berupa objek.")
    merchant_id = _text(raw, "id", f"Merchant ke-{index + 1}")
    where = f"Merchant '{merchant_id}'"
    if merchant_id in seen_ids:
        raise DataError(f"{where}: id merchant dobel.")
    seen_ids.add(merchant_id)

    canteen = _text(raw, "canteen", where)
    try:
        updated_at = date.fromisoformat(raw.get("updated_at"))
    except (TypeError, ValueError):
        raise DataError(f"{where}: 'updated_at' wajib berformat TTTT-BB-HH (tanggal harga dicek).") from None

    items_raw = raw.get("items")
    if not isinstance(items_raw, list) or not items_raw:
        raise DataError(f"{where}: 'items' harus berisi minimal satu menu.")
    opens, closes = _clock(raw, "opens", where), _clock(raw, "closes", where)
    if (opens is None) != (closes is None) or (opens is not None and opens == closes):
        raise DataError(f"{where}: isi 'opens' dan 'closes' berbeda keduanya, atau kosongkan keduanya.")

    return Merchant(
        id=merchant_id,
        name=_text(raw, "name", where),
        canteen=canteen,
        items=tuple(_item(i, where, seen_items) for i in items_raw),
        updated_at=updated_at,
        verified=raw.get("verified") is True,
        opens=opens,
        closes=closes,
        note=str(raw.get("note", "")).strip(),
    )


def load_merchants(path: Union[str, Path]) -> List[Merchant]:
    path = Path(path)
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        raise DataError(f"Berkas data tidak ditemukan: {path}") from None
    except json.JSONDecodeError as err:
        raise DataError(f"JSON tidak valid di {path}: {err}") from err
    if not isinstance(raw, list) or not raw:
        raise DataError("Berkas data harus berupa daftar merchant yang tidak kosong.")
    seen_items: Set[str] = set()
    seen_ids: Set[str] = set()
    return [_merchant(m, i, seen_items, seen_ids) for i, m in enumerate(raw)]
