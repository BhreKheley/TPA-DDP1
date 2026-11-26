"""Logika inti murni (tanpa Flask): saring menurut anggaran, kombinasi menu, status buka.

Tidak ada skor, ranking, atau jarak: versi 1 hanya menjawab "dengan uang segini,
merchant mana yang masih terjangkau?".
"""

from datetime import date, datetime, time, timedelta, timezone
from typing import Dict, List, Optional, Tuple

from core.models import Category, MenuItem, Merchant

STALE_AFTER_DAYS = 30
WIB = timezone(timedelta(hours=7))  # offset tetap: zoneinfo butuh tzdata yang tidak ada di Windows
UNIT = 500  # kelipatan harga untuk tabel DP; pembulatan ke atas menjamin total tidak melebihi anggaran


def affordable_items(merchant: Merchant, budget: int) -> List[MenuItem]:
    """Menu merchant yang harganya sampai nominal, dari termurah."""
    return sorted((i for i in merchant.items if i.price <= budget), key=lambda i: (i.price, i.name))


def group_by_canteen(
    merchants: List[Merchant], budget: int, canteen: Optional[str] = None
) -> Dict[str, List[Merchant]]:
    """Merchant yang punya minimal satu menu terjangkau, per kantin, diurutkan menurut nama."""
    groups: Dict[str, List[Merchant]] = {}
    for m in sorted(merchants, key=lambda m: (m.canteen, m.name, m.id)):
        if canteen and m.canteen != canteen:
            continue
        if affordable_items(m, budget):
            groups.setdefault(m.canteen, []).append(m)
    return groups


def cheapest(merchants: List[Merchant]) -> Optional[Tuple[int, Merchant]]:
    """Harga menu termurah di seluruh data beserta merchantnya, atau None jika data kosong."""
    pairs = [(i.price, m) for m in merchants for i in m.items]
    return min(pairs, key=lambda p: (p[0], p[1].name, p[1].id)) if pairs else None


def best_combo(items: List[MenuItem], budget: int) -> List[MenuItem]:
    """Kombinasi menu dalam anggaran yang mencakup kategori terbanyak, lalu total termurah.

    DP atas status (kategori yang tercakup, biaya terpakai): paling banyak
    2^kategori * (anggaran / UNIT) status per menu.
    """
    cap = budget // UNIT
    reach: Dict[Tuple[int, int], Tuple[MenuItem, ...]] = {(0, 0): ()}
    bit = {c: 1 << n for n, c in enumerate(Category)}
    for item in sorted(items, key=lambda i: (i.price, i.id)):
        weight = -(-item.price // UNIT)
        for (mask, cost), combo in list(reach.items()):
            key = (mask | bit[item.category], cost + weight)
            if key[1] <= cap and key not in reach:
                reach[key] = combo + (item,)

    def score(combo: Tuple[MenuItem, ...]) -> Tuple[int, int]:
        return len({i.category for i in combo}), -sum(i.price for i in combo)

    return list(max(reach.values(), key=score))


def is_stale(merchant: Merchant, today: date) -> bool:
    return (today - merchant.updated_at).days > STALE_AFTER_DAYS


def is_open(merchant: Merchant, now: time) -> Optional[bool]:
    """True/False jika jam buka diketahui, None jika tidak. Jam yang melewati tengah malam ditangani."""
    if merchant.opens is None or merchant.closes is None:
        return None
    if merchant.opens < merchant.closes:
        return merchant.opens <= now < merchant.closes
    return now >= merchant.opens or now < merchant.closes


def now_wib() -> datetime:
    return datetime.now(WIB)
