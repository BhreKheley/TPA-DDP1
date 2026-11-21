"""Tier 2 Boundary and Corner Case Tests for Smart Meal Finder.

Covers Boundary Value Analysis (BVA), anomaly handling, input sanitization,
extreme numeric values, and algorithmic corner cases across 5 categories:
- Boundary 1 (B1): Extreme Budgets (0, negative, deficit - 1, massive budget, exact minimum)
- Boundary 2 (B2): Dataset & Loader Anomalies (missing files, malformed schemas, corrupt values)
- Boundary 3 (B3): Strict Filter & Constraint Edges (impossible tags, unknown canteens, missing categories)
- Boundary 4 (B4): Web & API Input Boundaries (non-numeric, injection characters, whitespace, empty)
- Boundary 5 (B5): Optimality & Combination Corner Cases (duplicate costs, GCD scaling, tie-breaking)

Each category contains at least 5 distinct, assertion-rich test cases (Total: 27 tests).
"""

from typing import Any, List
import pytest


def get_loader():
    """Dynamically imports core.loader with progressive skip handling."""
    try:
        import core.loader as loader
        return loader
    except ImportError as e:
        pytest.skip(f"core.loader not yet implemented: {e}")


def get_budget():
    """Dynamically imports core.budget with progressive skip handling."""
    try:
        import core.budget as budget
        return budget
    except ImportError as e:
        pytest.skip(f"core.budget not yet implemented: {e}")


# ==============================================================================
# BOUNDARY 1 (B1): Extreme Budgets
# ==============================================================================

def test_tier2_budget_zero(temp_merchants_file: str):
    """B1.1: Budget = 0 returns INSUFFICIENT_BUDGET with deficit equal to cheapest meal/combo."""
    loader = get_loader()
    budget_eng = get_budget()

    merchants = loader.load_merchants(temp_merchants_file)
    result = budget_eng.recommend_meals(merchants, budget=0, require_combo=True)

    assert result.status == "INSUFFICIENT_BUDGET"
    assert result.budget == 0
    assert len(result.recommendations) == 0
    assert result.deficit > 0, "Deficit must be greater than 0 for budget=0"
    assert result.cheapest_item_price > 0, "Cheapest price must be non-zero positive"
    # Deficit when budget is 0 equals the cost of the cheapest meal
    assert result.deficit == result.cheapest_item_price


def test_tier2_budget_negative(temp_merchants_file: str):
    """B1.2: Negative budget is rejected gracefully (INSUFFICIENT_BUDGET or ValueError, never 500 crash)."""
    loader = get_loader()
    budget_eng = get_budget()

    merchants = loader.load_merchants(temp_merchants_file)
    try:
        result = budget_eng.recommend_meals(merchants, budget=-5000, require_combo=True)
        assert result.status in ("INSUFFICIENT_BUDGET", "INVALID_INPUT")
        assert len(result.recommendations) == 0
    except (ValueError, budget_eng.RecommendationError if hasattr(budget_eng, "RecommendationError") else ValueError) as exc:
        # Graceful exception is also acceptable per contract
        assert "budget" in str(exc).lower() or "negative" in str(exc).lower() or "-5000" in str(exc)


def test_tier2_budget_one_rupiah_short(temp_merchants_file: str):
    """B1.3: Budget exactly 1 Rupiah short of the cheapest meal returns deficit == 1."""
    loader = get_loader()
    budget_eng = get_budget()

    merchants = loader.load_merchants(temp_merchants_file)
    # Probe cheapest meal cost by calling with 0
    probe = budget_eng.recommend_meals(merchants, budget=0, require_combo=True)
    cheapest_cost = probe.cheapest_item_price

    # Now call with budget = cheapest_cost - 1
    tight_budget = cheapest_cost - 1
    result = budget_eng.recommend_meals(merchants, budget=tight_budget, require_combo=True)

    assert result.status == "INSUFFICIENT_BUDGET"
    assert result.budget == tight_budget
    assert len(result.recommendations) == 0
    assert result.deficit == 1, f"Expected deficit of exactly 1 Rupiah, got {result.deficit}"


def test_tier2_budget_massive(temp_merchants_file: str):
    """B1.4: Massive budget (Rp 10,000,000) is handled cleanly without memory crash or timeout."""
    loader = get_loader()
    budget_eng = get_budget()

    merchants = loader.load_merchants(temp_merchants_file)
    massive_budget = 10_000_000
    result = budget_eng.recommend_meals(merchants, budget=massive_budget, require_combo=True)

    assert result.status == "SUCCESS"
    assert len(result.recommendations) > 0
    top_combo = result.recommendations[0]
    assert top_combo.total_cost <= massive_budget
    assert top_combo.budget_remaining == massive_budget - top_combo.total_cost
    assert top_combo.budget_remaining >= 0


def test_tier2_budget_exact_cheapest(temp_merchants_file: str):
    """B1.5: Budget exactly equal to cheapest valid combo returns valid combo with deficit=0."""
    loader = get_loader()
    budget_eng = get_budget()

    merchants = loader.load_merchants(temp_merchants_file)
    probe = budget_eng.recommend_meals(merchants, budget=0, require_combo=True)
    cheapest_cost = probe.cheapest_item_price

    result = budget_eng.recommend_meals(merchants, budget=cheapest_cost, require_combo=True)

    assert result.status == "SUCCESS"
    assert result.deficit == 0
    assert len(result.recommendations) > 0
    assert result.recommendations[0].total_cost == cheapest_cost
    assert result.recommendations[0].is_exact_match is True


# ==============================================================================
# BOUNDARY 2 (B2): Dataset & Loader Anomalies
# ==============================================================================

def test_tier2_loader_nonexistent_file(corrupt_dataset_factory):
    """B2.1: Loading a nonexistent file raises FileNotFoundError or DataValidationError."""
    loader = get_loader()
    nonexistent_path = corrupt_dataset_factory("nonexistent")

    with pytest.raises((FileNotFoundError, loader.DataValidationError)):
        loader.load_merchants(nonexistent_path)


def test_tier2_loader_empty_json(corrupt_dataset_factory):
    """B2.2: Empty JSON object {} raises DataValidationError or InvalidSchemaError."""
    loader = get_loader()
    empty_json_path = corrupt_dataset_factory("empty_json")

    with pytest.raises(loader.DataValidationError):
        loader.load_merchants(empty_json_path)


def test_tier2_loader_invalid_schema(corrupt_dataset_factory):
    """B2.3: JSON missing required merchant/item fields triggers DataValidationError."""
    loader = get_loader()
    missing_keys_path = corrupt_dataset_factory("missing_keys")

    with pytest.raises(loader.DataValidationError):
        loader.load_merchants(missing_keys_path)


def test_tier2_loader_negative_price(corrupt_dataset_factory):
    """B2.4: Menu item with negative price triggers DataValidationError."""
    loader = get_loader()
    neg_price_path = corrupt_dataset_factory("negative_price")

    with pytest.raises(loader.DataValidationError):
        loader.load_merchants(neg_price_path)


def test_tier2_loader_empty_merchants_list(corrupt_dataset_factory):
    """B2.5: JSON with empty merchants array returns empty list safely without crashing."""
    loader = get_loader()
    empty_merchants_path = corrupt_dataset_factory("empty_merchants")

    merchants = loader.load_merchants(empty_merchants_path, strict=False)
    assert isinstance(merchants, list)
    assert len(merchants) == 0


def test_tier2_loader_invalid_category(corrupt_dataset_factory):
    """B2.6: Menu item with invalid/unsupported category raises DataValidationError."""
    loader = get_loader()
    invalid_cat_path = corrupt_dataset_factory("invalid_category")

    with pytest.raises(loader.DataValidationError):
        loader.load_merchants(invalid_cat_path)


# ==============================================================================
# BOUNDARY 3 (B3): Strict Filter & Constraint Edges
# ==============================================================================

def test_tier2_filter_impossible_tags(temp_merchants_file: str):
    """B3.1: Filtering for impossible dietary tags returns NO_MATCHING_ITEMS safely."""
    loader = get_loader()
    budget_eng = get_budget()

    merchants = loader.load_merchants(temp_merchants_file)
    result = budget_eng.recommend_meals(
        merchants,
        budget=30000,
        dietary_preferences=["impossible_quantum_tag_xyz"],
        require_combo=True,
    )

    assert result.status in ("NO_MATCHING_ITEMS", "INSUFFICIENT_BUDGET")
    assert len(result.recommendations) == 0


def test_tier2_filter_nonexistent_canteen(temp_merchants_file: str):
    """B3.2: Filtering for non-existent canteen returns NO_MATCHING_ITEMS safely."""
    loader = get_loader()
    budget_eng = get_budget()

    merchants = loader.load_merchants(temp_merchants_file)
    result = budget_eng.recommend_meals(
        merchants,
        budget=30000,
        canteen_filter="Kantin Hogwarts",
        require_combo=True,
    )

    assert result.status in ("NO_MATCHING_ITEMS", "INSUFFICIENT_BUDGET")
    assert len(result.recommendations) == 0


def test_tier2_filter_food_only_available():
    """B3.3: When no drinks exist in pool, combo requirement falls back gracefully."""
    loader = get_loader()
    budget_eng = get_budget()

    cat_food = getattr(loader, "Category", None)
    cat_food = cat_food.FOOD if cat_food else "food"

    food_only_items = [
        loader.MenuItem(
            id="f1", name="Food Only 1", category=cat_food, price=10000,
            satisfaction_score=8.0, dietary_tags=frozenset(["halal"]),
            merchant_id="m1", merchant_name="M1", canteen_name="Takor", faculty="FEB"
        )
    ]

    result = budget_eng.recommend_meals(food_only_items, budget=15000, require_combo=True)
    # Must either inform user of missing combo components or fall back to food-only package
    assert result.status in ("NO_MATCHING_ITEMS", "SUCCESS", "INSUFFICIENT_BUDGET")
    if result.status == "SUCCESS":
        assert len(result.recommendations) > 0


def test_tier2_filter_single_expensive_item():
    """B3.4: All available items exceed user budget."""
    loader = get_loader()
    budget_eng = get_budget()

    cat_food = getattr(loader, "Category", None)
    cat_food = cat_food.FOOD if cat_food else "food"

    expensive_items = [
        loader.MenuItem(
            id="exp_1", name="Sultan Lobster Meal", category=cat_food, price=150000,
            satisfaction_score=9.9, dietary_tags=frozenset(),
            merchant_id="m1", merchant_name="M1", canteen_name="Dallas", faculty="Fisip"
        )
    ]

    result = budget_eng.recommend_meals(expensive_items, budget=20000, require_combo=False)
    assert result.status == "INSUFFICIENT_BUDGET"
    assert result.deficit == 130000
    assert len(result.recommendations) == 0


def test_tier2_filter_case_insensitivity(temp_merchants_file: str):
    """B3.5: Canteen and dietary filters operate case-insensitively (e.g. 'fAsIlkOm', 'HALAL')."""
    loader = get_loader()
    budget_eng = get_budget()

    merchants = loader.load_merchants(temp_merchants_file)
    result = budget_eng.recommend_meals(
        merchants,
        budget=35000,
        canteen_filter="fAsIlkOm",
        dietary_preferences=["HALAL"],
        require_combo=True,
    )

    assert result.status == "SUCCESS"
    assert len(result.recommendations) > 0
    for combo in result.recommendations:
        for it in combo.items:
            assert it.canteen_name.lower() == "fasilkom"


# ==============================================================================
# BOUNDARY 4 (B4): Web & API Input Boundaries
# ==============================================================================

def test_tier2_web_empty_budget_string(client):
    """B4.1: Submitting empty string budget returns validation error, not 500 crash."""
    response = client.post(
        "/recommend",
        data={"budget": ""},
        follow_redirects=True,
    )
    assert response.status_code in (200, 400)
    assert response.status_code != 500
    html = response.get_data(as_text=True)
    assert any(k in html.lower() for k in ["masukkan budget", "wajib", "valid", "error"])


def test_tier2_web_non_numeric_budget(client):
    """B4.2: Submitting non-numeric budget ('abc', '$20.00') returns user-friendly error, not 500."""
    response = client.post(
        "/recommend",
        data={"budget": "abc_rupiah"},
        follow_redirects=True,
    )
    assert response.status_code in (200, 400)
    assert response.status_code != 500


def test_tier2_web_special_characters(client):
    """B4.3: XSS payload in input form is properly escaped and sanitized without execution."""
    xss_payload = "<script>alert('xss_attack')</script>"
    response = client.post(
        "/recommend",
        data={"budget": "20000", "canteen": xss_payload},
        follow_redirects=True,
    )
    assert response.status_code in (200, 400)
    html = response.get_data(as_text=True)
    # Raw unescaped script tag must NOT be present in output HTML
    assert "<script>alert('xss_attack')</script>" not in html


def test_tier2_web_missing_form_params(client):
    """B4.4: Submitting POST request without any budget field handled gracefully."""
    response = client.post(
        "/recommend",
        data={},
        follow_redirects=True,
    )
    assert response.status_code in (200, 400)
    assert response.status_code != 500


def test_tier2_web_whitespace_budget(client):
    """B4.5: Budget string with leading and trailing whitespaces ('  15000  ') parsed cleanly."""
    response = client.post(
        "/recommend",
        data={"budget": "   15000   "},
        follow_redirects=True,
    )
    assert response.status_code == 200
    html = response.get_data(as_text=True)
    # Should successfully process Rp 15,000 without parsing error
    assert "15" in html or "rekomendasi" in html.lower() or "paket" in html.lower()


def test_tier2_web_negative_budget(client):
    """B4.6: Submitting negative budget returns 400 or user-facing validation error, not 500."""
    response = client.post(
        "/recommend",
        data={"budget": "-5000"},
        follow_redirects=True,
    )
    assert response.status_code != 500
    assert response.status_code in (200, 400)
    html = response.get_data(as_text=True)
    assert response.status_code == 400 or any(
        k in html.lower() for k in ["masukkan budget", "wajib", "valid", "error", "negatif", "kurang"]
    )


# ==============================================================================
# BOUNDARY 5 (B5): Optimality & Combination Corner Cases
# ==============================================================================

def test_tier2_knapsack_duplicate_prices():
    """B5.1: Multiple items with identical prices; algorithm selects highest satisfaction items."""
    loader = get_loader()
    budget_eng = get_budget()

    cat_food = getattr(loader, "Category", None)
    cat_food = cat_food.FOOD if cat_food else "food"

    # Three items, all costing 10000, but with different satisfaction scores
    items = [
        loader.MenuItem(
            id="dup_1", name="Low Sat", category=cat_food, price=10000,
            satisfaction_score=5.0, dietary_tags=frozenset(),
            merchant_id="m1", merchant_name="M", canteen_name="C", faculty="F"
        ),
        loader.MenuItem(
            id="dup_2", name="High Sat", category=cat_food, price=10000,
            satisfaction_score=9.5, dietary_tags=frozenset(),
            merchant_id="m1", merchant_name="M", canteen_name="C", faculty="F"
        ),
        loader.MenuItem(
            id="dup_3", name="Med Sat", category=cat_food, price=10000,
            satisfaction_score=7.0, dietary_tags=frozenset(),
            merchant_id="m1", merchant_name="M", canteen_name="C", faculty="F"
        ),
    ]

    selected, cost, sat = budget_eng.knapsack_01_dp(items, budget=10000)
    assert len(selected) == 1
    assert selected[0].id == "dup_2", "Should pick dup_2 with highest satisfaction (9.5)"
    assert cost == 10000
    assert abs(sat - 9.5) < 1e-4


def test_tier2_knapsack_all_items_affordable():
    """B5.2: Budget exceeds sum of all items in pool; selects all items without crash."""
    loader = get_loader()
    budget_eng = get_budget()

    cat_food = getattr(loader, "Category", None)
    cat_food = cat_food.FOOD if cat_food else "food"

    items = [
        loader.MenuItem(
            id=f"all_{i}", name=f"Item {i}", category=cat_food, price=3000,
            satisfaction_score=5.0 + i, dietary_tags=frozenset(),
            merchant_id="m1", merchant_name="M", canteen_name="C", faculty="F"
        )
        for i in range(5)
    ]
    # Total sum is 5 * 3000 = 15000. Give budget = 50000.
    selected, cost, sat = budget_eng.knapsack_01_dp(items, budget=50000)

    assert len(selected) == 5, "All items should be selected when budget is plenty"
    assert cost == 15000
    assert abs(sat - sum(it.satisfaction_score for it in items)) < 1e-4


def test_tier2_exact_budget_multi_item():
    """B5.3: Budget is perfectly spent leaving budget_remaining == 0 across multiple items."""
    loader = get_loader()
    budget_eng = get_budget()

    cat_food = getattr(loader, "Category", None)
    cat_food = cat_food.FOOD if cat_food else "food"

    items = [
        loader.MenuItem(
            id="multi_1", name="Food Part 1", category=cat_food, price=7500,
            satisfaction_score=7.0, dietary_tags=frozenset(),
            merchant_id="m1", merchant_name="M", canteen_name="C", faculty="F"
        ),
        loader.MenuItem(
            id="multi_2", name="Food Part 2", category=cat_food, price=12500,
            satisfaction_score=8.5, dietary_tags=frozenset(),
            merchant_id="m1", merchant_name="M", canteen_name="C", faculty="F"
        ),
    ]

    selected, cost, sat = budget_eng.knapsack_01_dp(items, budget=20000)
    assert cost == 20000
    assert len(selected) == 2
    assert {it.id for it in selected} == {"multi_1", "multi_2"}


def test_tier2_recommend_tie_breaking():
    """B5.4: Deterministic ranking when combinations have identical satisfaction and cost."""
    loader = get_loader()
    budget_eng = get_budget()

    Category = getattr(loader, "Category", None)
    cat_food = Category.FOOD if Category else "food"
    cat_bev = Category.BEVERAGE if Category else "beverage"

    items = [
        loader.MenuItem(
            id="f_a", name="Ayam A", category=cat_food, price=10000,
            satisfaction_score=8.0, dietary_tags=frozenset(),
            merchant_id="m1", merchant_name="M1", canteen_name="Dallas", faculty="Fisip"
        ),
        loader.MenuItem(
            id="f_b", name="Ayam B", category=cat_food, price=10000,
            satisfaction_score=8.0, dietary_tags=frozenset(),
            merchant_id="m2", merchant_name="M2", canteen_name="Dallas", faculty="Fisip"
        ),
        loader.MenuItem(
            id="b_1", name="Es Teh", category=cat_bev, price=3000,
            satisfaction_score=6.0, dietary_tags=frozenset(),
            merchant_id="m1", merchant_name="M1", canteen_name="Dallas", faculty="Fisip"
        ),
    ]

    # Two runs should yield identical deterministic ordering
    res1 = budget_eng.recommend_meals(items, budget=15000, require_combo=True)
    res2 = budget_eng.recommend_meals(items, budget=15000, require_combo=True)

    combo1_ids = [[it.id for it in c.items] for c in res1.recommendations]
    combo2_ids = [[it.id for it in c.items] for c in res2.recommendations]

    assert combo1_ids == combo2_ids, "Recommendation results must be strictly deterministic across calls"


def test_tier2_gcd_large_prices():
    """B5.5: Tests GCD reduction optimization in DP table for large realistic price values."""
    loader = get_loader()
    budget_eng = get_budget()

    cat_food = getattr(loader, "Category", None)
    cat_food = cat_food.FOOD if cat_food else "food"

    # Prices are large multiples of 5,000 (GCD = 5000)
    items = [
        loader.MenuItem(
            id="gcd_1", name="Item 15k", category=cat_food, price=15000,
            satisfaction_score=7.5, dietary_tags=frozenset(),
            merchant_id="m1", merchant_name="M", canteen_name="C", faculty="F"
        ),
        loader.MenuItem(
            id="gcd_2", name="Item 25k", category=cat_food, price=25000,
            satisfaction_score=9.0, dietary_tags=frozenset(),
            merchant_id="m1", merchant_name="M", canteen_name="C", faculty="F"
        ),
        loader.MenuItem(
            id="gcd_3", name="Item 35k", category=cat_food, price=35000,
            satisfaction_score=9.8, dietary_tags=frozenset(),
            merchant_id="m1", merchant_name="M", canteen_name="C", faculty="F"
        ),
    ]

    # Budget 50,000: optimal is gcd_1 (15k, sat 7.5) + gcd_3 (35k, sat 9.8) = cost 50k, sat 17.3
    # or gcd_2 (25k, sat 9.0) + ...
    selected, cost, sat = budget_eng.knapsack_01_dp(items, budget=50000)
    assert cost == 50000
    assert abs(sat - 17.3) < 1e-4
    assert {it.id for it in selected} == {"gcd_1", "gcd_3"}
