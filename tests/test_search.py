"""Tes untuk core/search.py: filter merchant P0, best_combo P1, status buka dan data usang."""

from datetime import date, datetime

import pytest

from core.loader import Category, MenuItem, Merchant
from core.search import affordable_merchants, best_combo, cheapest_gap, is_open, is_stale


def _item(name, price, cat, merchant="m1", canteen="Kantin A", available=True, updated_at=None, tags=()):
    return MenuItem(
        id=f"{merchant}_{name}", name=name, category=cat, price=price, satisfaction_score=50.0,
        dietary_tags=frozenset(tags), merchant_id=merchant, merchant_name=merchant.upper(),
        canteen_name=canteen, faculty="F", is_available=available, updated_at=updated_at,
    )


def _merchant(mid, name, canteen, items, open_hours=None):
    return Merchant(
        id=mid, name=name, canteen_id=canteen.lower(), canteen_name=canteen, faculty="F",
        rating=4.0, items=items, open_hours=open_hours,
    )


MENU_CONTOH = (
    _item("nasi", 4000, Category.FOOD),
    _item("ayam goreng", 9000, Category.SNACK),
    _item("tempe", 2000, Category.SNACK),
    _item("es teh", 3000, Category.BEVERAGE),
)


# ---- best_combo (P1) -------------------------------------------------------

def test_best_combo_never_exceeds_budget():
    combo = best_combo(MENU_CONTOH, 15_000)
    assert sum(m.price for m in combo) <= 15_000


def test_best_combo_prefers_more_categories():
    assert {m.name for m in best_combo(MENU_CONTOH, 15_000)} == {"nasi", "tempe", "es teh"}


def test_best_combo_empty_menu_returns_empty():
    assert best_combo((), 20_000) == ()


def test_best_combo_budget_below_every_price_returns_empty():
    assert best_combo(MENU_CONTOH, 1_000) == ()


def test_best_combo_budget_equal_to_single_price():
    assert [m.name for m in best_combo((_item("nasi", 4000, Category.FOOD),), 4000)] == ["nasi"]


def test_best_combo_rounds_prices_up_so_total_stays_within_budget():
    menu = (_item("a", 1200, Category.FOOD), _item("b", 1200, Category.BEVERAGE))
    assert sum(m.price for m in best_combo(menu, 2500, unit=500)) <= 2500


def test_best_combo_ignores_unavailable_items():
    menu = (_item("nasi", 4000, Category.FOOD, available=False), _item("es teh", 3000, Category.BEVERAGE))
    assert [m.name for m in best_combo(menu, 20_000)] == ["es teh"]


# ---- affordable_merchants (P0) ---------------------------------------------

def test_affordable_merchants_groups_by_canteen_sorted_by_name():
    ms = [
        _merchant("z", "Zeta", "Kantin B", [_item("nasi", 8000, Category.FOOD, "z", "Kantin B")]),
        _merchant("a", "Alfa", "Kantin B", [_item("teh", 3000, Category.BEVERAGE, "a", "Kantin B")]),
        _merchant("c", "Citra", "Kantin A", [_item("mie", 9000, Category.FOOD, "c", "Kantin A")]),
    ]
    groups = affordable_merchants(ms, 10_000)
    assert [g.canteen for g in groups] == ["Kantin A", "Kantin B"]
    assert [h.merchant.name for h in groups[1].hits] == ["Alfa", "Zeta"]


def test_affordable_merchants_reports_cheapest_and_count():
    ms = [_merchant("a", "Alfa", "K", [
        _item("nasi", 8000, Category.FOOD, "a", "K"),
        _item("teh", 3000, Category.BEVERAGE, "a", "K"),
        _item("steak", 30000, Category.FOOD, "a", "K"),
    ])]
    hit = affordable_merchants(ms, 10_000)[0].hits[0]
    assert (hit.cheapest_price, len(hit.fitting_items)) == (3000, 2)


def test_affordable_merchants_budget_equal_to_price_is_included():
    ms = [_merchant("a", "Alfa", "K", [_item("teh", 3000, Category.BEVERAGE, "a", "K")])]
    assert len(affordable_merchants(ms, 3000)) == 1


def test_affordable_merchants_budget_below_all_prices_is_empty():
    ms = [_merchant("a", "Alfa", "K", [_item("teh", 3000, Category.BEVERAGE, "a", "K")])]
    assert affordable_merchants(ms, 2999) == []


def test_affordable_merchants_skips_empty_menu_and_unavailable_items():
    ms = [
        _merchant("a", "Kosong", "K", []),
        _merchant("b", "Habis", "K", [_item("teh", 3000, Category.BEVERAGE, "b", "K", available=False)]),
    ]
    assert affordable_merchants(ms, 50_000) == []


def test_same_merchant_name_in_two_canteens_stays_separate():
    ms = [
        _merchant("a1", "Bakso", "Kantin A", [_item("bakso", 9000, Category.FOOD, "a1", "Kantin A")]),
        _merchant("b1", "Bakso", "Kantin B", [_item("bakso", 9000, Category.FOOD, "b1", "Kantin B")]),
    ]
    groups = affordable_merchants(ms, 10_000)
    assert [(g.canteen, len(g.hits)) for g in groups] == [("Kantin A", 1), ("Kantin B", 1)]


def test_affordable_merchants_canteen_and_tag_filters():
    ms = [
        _merchant("a", "Alfa", "Kantin A", [_item("teh", 3000, Category.BEVERAGE, "a", "Kantin A", tags=("halal",))]),
        _merchant("b", "Beta", "Kantin B", [_item("teh", 3000, Category.BEVERAGE, "b", "Kantin B")]),
    ]
    assert [g.canteen for g in affordable_merchants(ms, 5000, canteen="kantin b")] == ["Kantin B"]
    assert [g.canteen for g in affordable_merchants(ms, 5000, tags={"halal"})] == ["Kantin A"]


def test_cheapest_gap_gives_cheapest_price_and_shortfall():
    ms = [_merchant("a", "Alfa", "K", [_item("teh", 3000, Category.BEVERAGE, "a", "K")])]
    assert cheapest_gap(ms, 1000) == (3000, 2000)


def test_cheapest_gap_is_none_without_items():
    assert cheapest_gap([], 1000) is None


# ---- is_stale ---------------------------------------------------------------

def test_is_stale_false_within_a_month():
    assert is_stale("2026-11-22", today=date(2026, 12, 10)) is False


def test_is_stale_true_after_a_month():
    assert is_stale("2026-10-01", today=date(2026, 12, 10)) is True


def test_is_stale_none_when_date_missing():
    assert is_stale(None, today=date(2026, 12, 10)) is None


def test_is_stale_rejects_malformed_date():
    with pytest.raises(ValueError):
        is_stale("22-11-2026", today=date(2026, 12, 10))


# ---- is_open ----------------------------------------------------------------

HOURS = {"senin": ("08:00", "16:00"), "jumat": ("22:00", "02:00")}


def test_is_open_none_without_hours():
    assert is_open(None, datetime(2026, 11, 23, 10, 0)) is None


def test_is_open_inside_and_outside_window():
    monday = datetime(2026, 11, 23, 10, 0)  # Senin
    assert is_open(HOURS, monday) is True
    assert is_open(HOURS, monday.replace(hour=17)) is False


def test_is_open_closed_on_day_without_entry():
    assert is_open(HOURS, datetime(2026, 11, 24, 10, 0)) is False  # Selasa


def test_is_open_past_midnight_spills_into_next_day():
    friday_late = datetime(2026, 11, 27, 23, 0)
    saturday_early = datetime(2026, 11, 28, 1, 0)
    assert is_open(HOURS, friday_late) is True
    assert is_open(HOURS, saturday_early) is True
    assert is_open(HOURS, saturday_early.replace(hour=3)) is False
