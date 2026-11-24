"""Pencarian merchant berdasarkan anggaran (logika murni, tanpa web dan basis data).

Smart Meal Finder - DDP1 Gasal 2026/2027 Kelompok 5

Isi modul sesuai rancangan:
1. `affordable_merchants`: merchant lolos jika punya minimal satu menu tersedia dengan
   harga <= nominal. Dikelompokkan per kantin, diurutkan menurut nama, tanpa skor (P0).
2. `cheapest_gap`: harga termurah dan selisihnya dari nominal, untuk empty state (P0).
3. `best_combo`: pilih sebagian menu agar total <= anggaran dan jumlah kategori
   tercakup maksimum. Tie-break: total biaya terdekat ke anggaran (P1).
4. `is_stale` dan `is_open`: label data lebih dari satu bulan dan status buka (P1).
"""

from dataclasses import dataclass
from datetime import date, datetime
from typing import Dict, Iterable, List, Optional, Sequence, Set, Tuple

from core.loader import DAY_NAMES, MenuItem, Merchant, filter_items

STALE_AFTER_DAYS = 31


@dataclass(frozen=True)
class MerchantHit:
    """Satu merchant yang lolos filter anggaran beserta menu yang muat."""
    merchant: Merchant
    fitting_items: Tuple[MenuItem, ...]
    cheapest_price: int


@dataclass(frozen=True)
class CanteenGroup:
    """Kumpulan merchant lolos di satu kantin, urut menurut nama merchant."""
    canteen: str
    hits: Tuple[MerchantHit, ...]


def affordable_merchants(
    merchants: Iterable[Merchant],
    budget: int,
    canteen: Optional[str] = None,
    tags: Optional[Set[str]] = None,
) -> List[CanteenGroup]:
    """Merchant dengan minimal satu menu tersedia berharga <= budget, per kantin, urut nama."""
    by_canteen: Dict[str, List[MerchantHit]] = {}
    for m in merchants:
        available = [it for it in m.items if it.is_available]
        fitting = filter_items(available, max_price=budget, canteen_name=canteen, required_tags=tags)
        if not fitting:
            continue
        fitting.sort(key=lambda it: (it.price, it.name.casefold(), it.id))
        by_canteen.setdefault(m.canteen_name, []).append(
            MerchantHit(merchant=m, fitting_items=tuple(fitting), cheapest_price=fitting[0].price)
        )
    return [
        CanteenGroup(
            canteen=name,
            hits=tuple(sorted(hits, key=lambda h: (h.merchant.name.casefold(), h.merchant.id))),
        )
        for name, hits in sorted(by_canteen.items(), key=lambda kv: kv[0].casefold())
    ]


def cheapest_gap(merchants: Iterable[Merchant], budget: int) -> Optional[Tuple[int, int]]:
    """Harga termurah yang ada dan selisihnya dari budget (0 jika sudah cukup). None jika tanpa menu."""
    prices = [it.price for m in merchants for it in m.items if it.is_available]
    if not prices:
        return None
    cheapest = min(prices)
    return cheapest, max(0, cheapest - budget)


def best_combo(menu: Sequence[MenuItem], budget: int, unit: int = 500) -> Tuple[MenuItem, ...]:
    """Pilih menu dengan cakupan kategori terbanyak dalam anggaran.

    DP atas status (mask kategori, biaya dalam satuan `unit`). Harga dibulatkan ke atas
    ke kelipatan `unit`, jadi total sebenarnya tidak pernah melebihi anggaran.
    Kompleksitas: menu x 2^kategori x anggaran/unit.
    """
    items = sorted((it for it in menu if it.is_available), key=lambda it: (it.price, it.name, it.id))
    bit = {c: 1 << i for i, c in enumerate(sorted({it.category.value for it in items}))}
    cap = max(0, budget) // unit
    reach: Dict[Tuple[int, int], Tuple[MenuItem, ...]] = {(0, 0): ()}
    for item in items:
        weight = -(-item.price // unit)
        for (mask, cost), combo in list(reach.items()):
            key = (mask | bit[item.category.value], cost + weight)
            if key[1] <= cap and key not in reach:
                reach[key] = combo + (item,)
    best = max(reach, key=lambda k: (bin(k[0]).count("1"), k[1]))
    return reach[best]


def is_stale(updated_at: Optional[str], today: Optional[date] = None, max_days: int = STALE_AFTER_DAYS) -> Optional[bool]:
    """True jika harga diperbarui lebih dari `max_days` hari lalu. None jika tanggal belum tercatat."""
    if not updated_at:
        return None
    day = date.fromisoformat(updated_at)
    return ((today or date.today()) - day).days > max_days


def _window_covers(hours: Tuple[str, str], hhmm: str, spill: bool) -> bool:
    """Apakah `hhmm` ada di jendela buka. `spill`: cek bagian jendela lewat tengah malam di hari berikutnya."""
    opens, closes = hours
    overnight = closes <= opens
    if spill:
        return overnight and hhmm < closes
    return opens <= hhmm < closes if not overnight else hhmm >= opens


def is_open(open_hours: Optional[Dict[str, Tuple[str, str]]], now: datetime) -> Optional[bool]:
    """Status buka pada waktu `now`. None jika jam buka belum tercatat. Mendukung jam lewat tengah malam."""
    if not open_hours:
        return None
    hhmm = now.strftime("%H:%M")
    today = open_hours.get(DAY_NAMES[now.weekday()])
    yesterday = open_hours.get(DAY_NAMES[(now.weekday() - 1) % 7])
    if today and _window_covers(today, hhmm, spill=False):
        return True
    return bool(yesterday and _window_covers(yesterday, hhmm, spill=True))
