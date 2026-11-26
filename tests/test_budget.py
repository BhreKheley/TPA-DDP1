from datetime import date, time

import pytest

from core.budget import (affordable_items, best_combo, cheapest, group_by_canteen, is_open, is_stale)
from core.loader import load_merchants
from core.models import Category, MenuItem


@pytest.fixture
def merchants(data_file):
    return load_merchants(data_file)


def test_budget_below_every_price_returns_nothing(merchants):
    assert group_by_canteen(merchants, 1000) == {}


def test_budget_equal_to_a_price_is_included(merchants):
    assert [m.id for m in group_by_canteen(merchants, 15000)["Kantin B"]] == ["m2", "m3"]
    assert [m.id for m in group_by_canteen(merchants, 2000)["Kantin A"]] == ["m1"]


def test_grouped_per_canteen_sorted_by_name_and_same_name_kept(merchants):
    groups = group_by_canteen(merchants, 20000)
    assert list(groups) == ["Kantin A", "Kantin B"]
    assert [m.name for m in groups["Kantin B"]] == ["Bakso", "Warung Murah"]


def test_canteen_filter(merchants):
    assert list(group_by_canteen(merchants, 20000, "Kantin A")) == ["Kantin A"]


def test_affordable_items_sorted_and_limited(merchants):
    assert [i.price for i in affordable_items(merchants[0], 4000)] == [2000, 3000, 4000]


def test_cheapest(merchants):
    price, merchant = cheapest(merchants)
    assert (price, merchant.id) == (2000, "m1")
    assert cheapest([]) is None


def test_best_combo_matches_rancangan_example(merchants):
    combo = best_combo(list(merchants[0].items), 15000)
    assert sorted(i.name for i in combo) == ["Es Teh", "Nasi", "Tempe"]
    assert sum(i.price for i in combo) == 9000


@pytest.mark.parametrize("budget", [0, 1000, 2000, 4999, 7000, 15000, 100000])
def test_best_combo_never_exceeds_budget(merchants, budget):
    combo = best_combo(list(merchants[0].items), budget)
    assert sum(i.price for i in combo) <= budget


def test_best_combo_odd_prices_never_exceed_budget():
    items = [MenuItem("x", "x", Category.FOOD, 2700), MenuItem("y", "y", Category.BEVERAGE, 2300)]
    assert sum(i.price for i in best_combo(items, 5000)) <= 5000


def test_best_combo_empty_menu():
    assert best_combo([], 10000) == []


def test_is_open_handles_midnight(merchants):
    night = merchants[2]  # 22:00 sampai 02:00
    assert is_open(night, time(23, 0)) is True
    assert is_open(night, time(1, 0)) is True
    assert is_open(night, time(12, 0)) is False
    assert is_open(merchants[0], time(12, 0)) is None


def test_is_stale_after_one_month(merchants):
    assert is_stale(merchants[1], date(2026, 11, 25)) is True
    assert is_stale(merchants[0], date(2026, 11, 25)) is False
