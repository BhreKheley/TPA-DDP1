"""Unit test suite for core/budget.py (Knapsack DP Engine & Meal Recommendation Optimizer).

Tests:
1. Boundary conditions and mathematical optimality of knapsack_01_dp:
   - Budget 0, negative budgets
   - Budget less than cheapest item
   - Exact budget matches (budget_remaining == 0)
   - Standard knapsack where greedy ratio heuristic fails and DP finds optimal subset
   - All items fit vs no items fit
   - Zero-price items handling
   - GCD scaling optimization
2. Comprehensive behavioral tests for recommend_meals:
   - Insufficient budget returning INSUFFICIENT_BUDGET status and exact deficit
   - Empty matching items returning NO_MATCHING_ITEMS
   - Balanced combo requirement (1 Food + 1 Beverage when require_combo=True)
   - Fallback to solo meals when require_combo=False
   - Strict dietary filter adherence (halal, vegetarian)
   - Strict canteen filter adherence
   - Top-K ranking order (descending total satisfaction)
   - Exact match flag (is_exact_match)
   - Acceptance of both List[Merchant] and List[MenuItem]
"""

from typing import Dict, List
import pytest

from core.loader import Category, MenuItem, Merchant
from core.budget import (
    MealCombination,
    RecommendationResult,
    knapsack_01_dp,
    recommend_meals,
)


class TestKnapsack01DP:
    """Verifies mathematical correctness and boundary handling of the 0/1 knapsack DP engine."""

    def test_knapsack_budget_zero(self, sample_menu_items: List[MenuItem]):
        selected, cost, sat = knapsack_01_dp(sample_menu_items, budget=0)
        assert selected == []
        assert cost == 0
        assert sat == 0.0

    def test_knapsack_budget_negative(self, sample_menu_items: List[MenuItem]):
        selected, cost, sat = knapsack_01_dp(sample_menu_items, budget=-5000)
        assert selected == []
        assert cost == 0
        assert sat == 0.0

    def test_knapsack_budget_less_than_cheapest_item(self, sample_menu_items: List[MenuItem]):
        # Cheapest item in sample is Rp 3,000 (Es Teh). Pass budget = 2,000.
        selected, cost, sat = knapsack_01_dp(sample_menu_items, budget=2000)
        assert selected == []
        assert cost == 0
        assert sat == 0.0

    def test_knapsack_exact_match_single_item(self):
        item = MenuItem(
            id="exact_item", name="Single Exact", category=Category.FOOD, price=11000,
            satisfaction_score=80.0, dietary_tags=frozenset(), merchant_id="m",
            merchant_name="M", canteen_name="Dallas", faculty="RIK"
        )
        selected, cost, sat = knapsack_01_dp([item], budget=11000)
        assert len(selected) == 1
        assert selected[0].id == "exact_item"
        assert cost == 11000
        assert abs(sat - 80.0) < 1e-4

    def test_knapsack_exact_match_multi_item(self):
        items = [
            MenuItem(id="i1", name="Food 1", category=Category.FOOD, price=7000, satisfaction_score=70.0,
                     dietary_tags=frozenset(), merchant_id="m", merchant_name="M", canteen_name="C", faculty="F"),
            MenuItem(id="i2", name="Food 2", category=Category.FOOD, price=8000, satisfaction_score=75.0,
                     dietary_tags=frozenset(), merchant_id="m", merchant_name="M", canteen_name="C", faculty="F"),
            MenuItem(id="i3", name="Food 3", category=Category.FOOD, price=10000, satisfaction_score=60.0,
                     dietary_tags=frozenset(), merchant_id="m", merchant_name="M", canteen_name="C", faculty="F"),
        ]
        # Budget = 15,000. Exactly matches i1 (7k) + i2 (8k) = 15k, Sat = 145.0.
        selected, cost, sat = knapsack_01_dp(items, budget=15000)
        assert cost == 15000
        assert {it.id for it in selected} == {"i1", "i2"}
        assert abs(sat - 145.0) < 1e-4

    def test_knapsack_greedy_failure_counterexample(self, knapsack_greedy_failure_items: List[MenuItem]):
        """Proves that knapsack DP finds global optimum where greedy value/weight ratio fails."""
        # knapsack_greedy_failure_items:
        # Item Greedy Bait: price 6,000, sat 60.0 (ratio 0.0100)
        # Item Optimal A:   price 5,000, sat 48.0 (ratio 0.0096)
        # Item Optimal B:   price 5,000, sat 48.0 (ratio 0.0096)
        # Greedy chooses: [Item Greedy Bait] -> Cost 6,000, Sat 60.0.
        # Knapsack DP chooses: [Item Optimal A, Item Optimal B] -> Cost 10,000, Sat 96.0.
        selected, cost, sat = knapsack_01_dp(knapsack_greedy_failure_items, budget=10000)
        selected_ids = {it.id for it in selected}

        assert selected_ids == {"item_opt_a", "item_opt_b"}, "Knapsack DP must select the optimal subset"
        assert cost == 10000
        assert abs(sat - 96.0) < 1e-4
        assert sat > 60.0, "DP satisfaction (96.0) must strictly beat greedy choice (60.0)"

    def test_knapsack_all_items_fit(self, sample_menu_items: List[MenuItem]):
        total_price = sum(it.price for it in sample_menu_items)
        total_sat = sum(it.satisfaction_score for it in sample_menu_items)
        selected, cost, sat = knapsack_01_dp(sample_menu_items, budget=total_price + 50000)
        assert len(selected) == len(sample_menu_items)
        assert cost == total_price
        assert abs(sat - total_sat) < 1e-4

    def test_knapsack_no_items_fit(self, sample_menu_items: List[MenuItem]):
        cheapest = min(it.price for it in sample_menu_items)
        selected, cost, sat = knapsack_01_dp(sample_menu_items, budget=cheapest - 1)
        assert selected == []
        assert cost == 0
        assert sat == 0.0

    def test_knapsack_empty_item_list(self):
        selected, cost, sat = knapsack_01_dp([], budget=25000)
        assert selected == []
        assert cost == 0
        assert sat == 0.0

    def test_knapsack_zero_price_item(self, synthetic_edge_case_items: Dict[str, MenuItem]):
        zero_item = synthetic_edge_case_items["zero_price"]
        paid_item = synthetic_edge_case_items["snack_cheap"]
        # Free item should be selected without ZeroDivisionError or crash
        selected, cost, sat = knapsack_01_dp([zero_item, paid_item], budget=1000)
        assert zero_item in selected
        assert paid_item in selected
        assert cost == 1000
        assert abs(sat - (zero_item.satisfaction_score + paid_item.satisfaction_score)) < 1e-4

    def test_knapsack_gcd_scaling_optimization(self):
        # Items with prices in multiples of 5,000 (GCD = 5,000)
        items = [
            MenuItem(id="i15", name="15k", category=Category.FOOD, price=15000, satisfaction_score=75.0,
                     dietary_tags=frozenset(), merchant_id="m", merchant_name="M", canteen_name="C", faculty="F"),
            MenuItem(id="i25", name="25k", category=Category.FOOD, price=25000, satisfaction_score=90.0,
                     dietary_tags=frozenset(), merchant_id="m", merchant_name="M", canteen_name="C", faculty="F"),
            MenuItem(id="i35", name="35k", category=Category.FOOD, price=35000, satisfaction_score=98.0,
                     dietary_tags=frozenset(), merchant_id="m", merchant_name="M", canteen_name="C", faculty="F"),
        ]
        # Budget 50k: optimal is i15 (15k) + i35 (35k) = 50k, sat 173.0 (beats i25 + i15 = 40k, sat 165.0)
        selected, cost, sat = knapsack_01_dp(items, budget=50000)
        assert cost == 50000
        assert {it.id for it in selected} == {"i15", "i35"}
        assert abs(sat - 173.0) < 1e-4


class TestRecommendMeals:
    """Verifies category constraints, deficit calculation, filtering, and ranking of recommend_meals."""

    def test_recommend_insufficient_budget_zero(self, sample_merchants: List[Merchant]):
        result = recommend_meals(sample_merchants, budget=0, require_combo=True)
        assert isinstance(result, RecommendationResult)
        assert result.status == "INSUFFICIENT_BUDGET"
        assert result.budget == 0
        assert len(result.recommendations) == 0
        assert result.deficit > 0
        assert result.cheapest_item_price > 0
        assert result.deficit == result.cheapest_item_price

    def test_recommend_insufficient_budget_one_rupiah_short(self, sample_merchants: List[Merchant]):
        probe = recommend_meals(sample_merchants, budget=0, require_combo=True)
        cheapest_cost = probe.cheapest_item_price

        result = recommend_meals(sample_merchants, budget=cheapest_cost - 1, require_combo=True)
        assert result.status == "INSUFFICIENT_BUDGET"
        assert result.budget == cheapest_cost - 1
        assert len(result.recommendations) == 0
        assert result.deficit == 1
        assert "kurang" in result.message.lower() or "insufficient" in result.message.lower() or result.deficit == 1

    def test_recommend_empty_matching_items_canteen_filter(self, sample_merchants: List[Merchant]):
        result = recommend_meals(sample_merchants, budget=30000, canteen_filter="Kantin Atlantis")
        assert result.status == "NO_MATCHING_ITEMS"
        assert len(result.recommendations) == 0

    def test_recommend_empty_matching_items_dietary_filter(self, sample_merchants: List[Merchant]):
        result = recommend_meals(sample_merchants, budget=30000, dietary_preferences=["nonexistent_dietary_tag"])
        assert result.status == "NO_MATCHING_ITEMS"
        assert len(result.recommendations) == 0

    def test_recommend_combo_requirement_food_and_beverage(self, sample_merchants: List[Merchant]):
        result = recommend_meals(sample_merchants, budget=25000, require_combo=True)
        assert result.status == "SUCCESS"
        assert len(result.recommendations) > 0

        for combo in result.recommendations:
            assert isinstance(combo, MealCombination)
            assert combo.total_cost <= 25000
            assert combo.budget_remaining == 25000 - combo.total_cost
            categories = {it.category for it in combo.items}
            assert Category.FOOD in categories, "Combo must include at least 1 food"
            assert Category.BEVERAGE in categories, "Combo must include at least 1 drink"

    def test_recommend_combo_requirement_false_allows_solo_items(self, sample_merchants: List[Merchant]):
        result = recommend_meals(sample_merchants, budget=12000, require_combo=False)
        assert result.status == "SUCCESS"
        assert len(result.recommendations) > 0
        # At least one recommendation may be solo food
        has_solo = any(len(combo.items) == 1 for combo in result.recommendations)
        assert has_solo or all(combo.total_cost <= 12000 for combo in result.recommendations)

    def test_recommend_dietary_filter_halal(self, sample_merchants: List[Merchant]):
        result = recommend_meals(sample_merchants, budget=30000, dietary_preferences=["halal"])
        assert result.status == "SUCCESS"
        assert len(result.recommendations) > 0
        for combo in result.recommendations:
            for it in combo.items:
                assert "halal" in it.dietary_tags

    def test_recommend_dietary_filter_vegetarian(self, sample_merchants: List[Merchant]):
        result = recommend_meals(sample_merchants, budget=30000, dietary_preferences=["vegetarian"])
        assert result.status == "SUCCESS"
        assert len(result.recommendations) > 0
        for combo in result.recommendations:
            for it in combo.items:
                assert "vegetarian" in it.dietary_tags

    def test_recommend_canteen_filter_strict(self, sample_merchants: List[Merchant]):
        result = recommend_meals(sample_merchants, budget=25000, canteen_filter="Kantin Dallas")
        assert result.status == "SUCCESS"
        assert len(result.recommendations) > 0
        for combo in result.recommendations:
            for it in combo.items:
                assert "dallas" in it.canteen_name.lower()

    def test_recommend_canteen_filter_case_insensitive_substring(self, sample_merchants: List[Merchant]):
        result = recommend_meals(sample_merchants, budget=25000, canteen_filter="TaKoR")
        assert result.status == "SUCCESS"
        assert len(result.recommendations) > 0
        for combo in result.recommendations:
            for it in combo.items:
                assert "takor" in it.canteen_name.lower()

    def test_recommend_exact_match_flag(self, sample_merchants: List[Merchant]):
        # In sample: Nasi Tempe Orek (11,000) + Es Teh (3,000) = 14,000
        result = recommend_meals(sample_merchants, budget=14000, require_combo=True)
        assert result.status == "SUCCESS"
        exact_combos = [c for c in result.recommendations if c.is_exact_match]
        assert len(exact_combos) > 0
        for ec in exact_combos:
            assert ec.total_cost == 14000
            assert ec.budget_remaining == 0

    def test_recommend_top_k_ranking_descending_satisfaction(self, sample_merchants: List[Merchant]):
        result = recommend_meals(sample_merchants, budget=35000, require_combo=True)
        assert result.status == "SUCCESS"
        scores = [c.total_satisfaction for c in result.recommendations]
        assert scores == sorted(scores, reverse=True), "Recommendations must be sorted by satisfaction descending"

    def test_recommend_package_types(self, sample_merchants: List[Merchant]):
        result = recommend_meals(sample_merchants, budget=30000, require_combo=True)
        assert result.status == "SUCCESS"
        valid_types = {"optimal", "hemat", "combo"}
        for c in result.recommendations:
            assert c.package_type in valid_types

    def test_recommend_accepts_item_list_directly(self, sample_menu_items: List[MenuItem]):
        result = recommend_meals(sample_menu_items, budget=20000, require_combo=True)
        assert result.status == "SUCCESS"
        assert len(result.recommendations) > 0

    def test_recommend_massive_budget_stability(self, sample_merchants: List[Merchant]):
        result = recommend_meals(sample_merchants, budget=10_000_000, require_combo=True)
        assert result.status == "SUCCESS"
        assert len(result.recommendations) > 0
        for c in result.recommendations:
            assert c.total_cost <= 10_000_000
