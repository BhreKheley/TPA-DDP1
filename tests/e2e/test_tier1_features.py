"""Tier 1 Feature Coverage Tests for Smart Meal Finder.

Covers the primary behavior (happy paths and core contracts) across all 5 features:
- Feature 1 (F1): Data Loader & Schema Validation
- Feature 2 (F2): Knapsack 0/1 DP Engine
- Feature 3 (F3): Meal Combo & Deficit Optimizer
- Feature 4 (F4): Flask Web App Routes & UI Flow
- Feature 5 (F5): REST API Endpoints

Each feature area includes at least 5 distinct, assertion-rich test cases (Total: 25 tests).
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
# FEATURE 1 (F1): Data Loader & Schema Validation
# ==============================================================================

def test_tier1_loader_valid_merchants(temp_merchants_file: str):
    """F1.1: Successfully loads valid merchants.json and parses Merchant records."""
    loader = get_loader()
    merchants = loader.load_merchants(temp_merchants_file)

    assert isinstance(merchants, list), "Loaded merchants must be returned as a list"
    assert len(merchants) == 6, f"Expected 6 merchants across 6 canteens, got {len(merchants)}"
    
    for merchant in merchants:
        assert hasattr(merchant, "id") and merchant.id, "Merchant must possess a non-empty id"
        assert hasattr(merchant, "name") and merchant.name, "Merchant must possess a non-empty name"
        assert hasattr(merchant, "canteen_name") and merchant.canteen_name, "Merchant must specify canteen_name"
        assert hasattr(merchant, "faculty") and merchant.faculty, "Merchant must specify faculty"
        assert hasattr(merchant, "rating") and isinstance(merchant.rating, (int, float)), "Merchant rating must be numeric"
        assert 1.0 <= merchant.rating <= 5.0, f"Merchant rating {merchant.rating} out of realistic range [1.0, 5.0]"
        assert hasattr(merchant, "items") and isinstance(merchant.items, list), "Merchant must contain items list"
        assert len(merchant.items) > 0, f"Merchant {merchant.name} should have at least 1 menu item"


def test_tier1_loader_item_counts_and_types(temp_merchants_file: str):
    """F1.2: Validates loaded menu item count, integer pricing, and float satisfaction."""
    loader = get_loader()
    merchants = loader.load_merchants(temp_merchants_file)
    all_items = loader.extract_all_items(merchants, only_available=False)

    # 4 in Dallas + 2 in Takor + 2 in Kansas + 2 in Pusgiwa + 2 in Texas + 3 in Fasilkom = 15 items
    assert len(all_items) == 15, f"Expected 15 total items in sample dataset, got {len(all_items)}"

    for item in all_items:
        assert isinstance(item.id, str) and item.id, "MenuItem id must be non-empty string"
        assert isinstance(item.name, str) and item.name, "MenuItem name must be non-empty string"
        assert isinstance(item.price, int), f"MenuItem price must be strictly integer (Rupiah), got {type(item.price)}"
        assert item.price > 0, f"MenuItem price must be strictly positive, got {item.price}"
        assert isinstance(item.satisfaction_score, (int, float)), "Satisfaction score must be numeric"
        assert 1.0 <= float(item.satisfaction_score) <= 10.0, f"Satisfaction score {item.satisfaction_score} must be in [1.0, 10.0]"
        assert isinstance(item.dietary_tags, (set, frozenset)), "Dietary tags must be set or frozenset"


def test_tier1_loader_canteen_distribution(temp_merchants_file: str):
    """F1.3: Validates all 6 UI canteens (Dallas, Takor, Kansas, Pusgiwa, Texas, Fasilkom) are present."""
    loader = get_loader()
    merchants = loader.load_merchants(temp_merchants_file)

    expected_canteens = {"Dallas", "Takor", "Kansas", "Pusgiwa", "Texas", "Fasilkom"}
    found_canteens = {m.canteen_name for m in merchants}

    assert expected_canteens == found_canteens, (
        f"Missing or unexpected UI canteens. Expected {expected_canteens}, found {found_canteens}"
    )


def test_tier1_loader_categories(temp_merchants_file: str):
    """F1.4: Validates item category mappings (food, beverage, snack) adhere to specification."""
    loader = get_loader()
    merchants = loader.load_merchants(temp_merchants_file)
    all_items = loader.extract_all_items(merchants, only_available=False)

    valid_categories = {"food", "beverage", "snack"}
    observed_categories = set()

    for item in all_items:
        # Category may be an Enum or str
        cat_val = item.category.value if hasattr(item.category, "value") else str(item.category)
        assert cat_val in valid_categories, f"Invalid category {cat_val} on item {item.name}"
        observed_categories.add(cat_val)

    assert observed_categories == valid_categories, f"Expected all categories {valid_categories} to be populated"


def test_tier1_loader_extract_available_items(temp_merchants_file: str):
    """F1.5: Verifies extract_all_items respects only_available filter."""
    loader = get_loader()
    merchants = loader.load_merchants(temp_merchants_file)

    all_items = loader.extract_all_items(merchants, only_available=False)
    available_items = loader.extract_all_items(merchants, only_available=True)

    assert len(all_items) == 15
    assert len(available_items) == 14, "Only 14 items should be available (1 Dallas item is marked sold out)"
    
    sold_out_ids = {it.id for it in all_items if not it.is_available}
    assert "item_dallas_04" in sold_out_ids, "item_dallas_04 should be flagged as not available"
    
    for it in available_items:
        assert it.is_available is True, f"Item {it.id} should have is_available=True"
        assert it.id != "item_dallas_04"


# ==============================================================================
# FEATURE 2 (F2): Knapsack 0/1 DP Engine
# ==============================================================================

def test_tier1_knapsack_basic_selection(temp_merchants_file: str):
    """F2.1: Knapsack algorithm selects an optimal non-empty subset within standard budget."""
    loader = get_loader()
    budget_eng = get_budget()
    
    merchants = loader.load_merchants(temp_merchants_file)
    items = loader.extract_all_items(merchants, only_available=True)
    
    budget_limit = 20000
    selected, total_cost, total_sat = budget_eng.knapsack_01_dp(items, budget_limit)
    
    assert isinstance(selected, list), "Selected items must be returned as a list"
    assert len(selected) > 0, "Knapsack should select at least 1 item for Rp 20,000 budget"
    assert total_cost <= budget_limit, f"Total cost {total_cost} must not exceed budget {budget_limit}"
    assert total_sat > 0.0, "Total satisfaction must be positive"


def test_tier1_knapsack_cost_within_limit(temp_merchants_file: str):
    """F2.2: Verifies strictly that total cost is <= budget and matches sum of selected items."""
    loader = get_loader()
    budget_eng = get_budget()

    merchants = loader.load_merchants(temp_merchants_file)
    items = loader.extract_all_items(merchants, only_available=True)

    test_budgets = [5000, 10000, 15000, 25000, 40000]
    for b in test_budgets:
        selected, total_cost, total_sat = budget_eng.knapsack_01_dp(items, b)
        calculated_cost = sum(it.price for it in selected)
        calculated_sat = sum(it.satisfaction_score for it in selected)

        assert total_cost <= b, f"Cost {total_cost} exceeded budget {b}"
        assert total_cost == calculated_cost, f"Reported cost {total_cost} != sum of items {calculated_cost}"
        assert abs(total_sat - calculated_sat) < 1e-4, "Reported satisfaction must match item sum"


def test_tier1_knapsack_maximizes_satisfaction():
    """F2.3: Verifies knapsack selects the higher satisfaction set over lower satisfaction options."""
    loader = get_loader()
    budget_eng = get_budget()

    Category = getattr(loader, "Category", None)
    cat_food = Category.FOOD if Category else "food"

    # Synthetic setup:
    # Option 1: Item 1 (Price 10000, Sat 6.0)
    # Option 2: Item 2 (Price 5000, Sat 4.0) + Item 3 (Price 5000, Sat 5.5) -> Total cost 10000, Sat 9.5
    items = [
        loader.MenuItem(
            id="synth_1", name="Item 1", category=cat_food, price=10000,
            satisfaction_score=6.0, dietary_tags=frozenset(), merchant_id="m",
            merchant_name="M", canteen_name="C", faculty="F"
        ),
        loader.MenuItem(
            id="synth_2", name="Item 2", category=cat_food, price=5000,
            satisfaction_score=4.0, dietary_tags=frozenset(), merchant_id="m",
            merchant_name="M", canteen_name="C", faculty="F"
        ),
        loader.MenuItem(
            id="synth_3", name="Item 3", category=cat_food, price=5000,
            satisfaction_score=5.5, dietary_tags=frozenset(), merchant_id="m",
            merchant_name="M", canteen_name="C", faculty="F"
        ),
    ]

    selected, cost, sat = budget_eng.knapsack_01_dp(items, budget=10000)
    selected_ids = {it.id for it in selected}

    assert cost == 10000
    assert abs(sat - 9.5) < 1e-4, f"Knapsack did not maximize satisfaction! Expected 9.5, got {sat}"
    assert selected_ids == {"synth_2", "synth_3"}, "Knapsack should have selected synth_2 and synth_3"


def test_tier1_knapsack_empty_item_pool():
    """F2.4: Knapsack handles empty item list gracefully without error."""
    budget_eng = get_budget()
    selected, cost, sat = budget_eng.knapsack_01_dp([], budget=20000)

    assert selected == [], "Selected items must be empty"
    assert cost == 0, "Total cost must be 0"
    assert sat == 0.0, "Total satisfaction must be 0.0"


def test_tier1_knapsack_single_item_exact():
    """F2.5: Budget exactly matches a single available item."""
    loader = get_loader()
    budget_eng = get_budget()

    cat_food = getattr(loader, "Category", None)
    cat_food = cat_food.FOOD if cat_food else "food"

    single_item = loader.MenuItem(
        id="exact_item", name="Single Exact Meal", category=cat_food, price=12500,
        satisfaction_score=8.4, dietary_tags=frozenset(), merchant_id="m",
        merchant_name="M", canteen_name="Dallas", faculty="Fisip"
    )

    selected, cost, sat = budget_eng.knapsack_01_dp([single_item], budget=12500)

    assert len(selected) == 1
    assert selected[0].id == "exact_item"
    assert cost == 12500
    assert abs(sat - 8.4) < 1e-4


# ==============================================================================
# FEATURE 3 (F3): Meal Combo & Deficit Optimizer
# ==============================================================================

def test_tier1_recommend_standard_combo(temp_merchants_file: str):
    """F3.1: Recommends realistic 1 Food + 1 Drink meal packages within budget."""
    loader = get_loader()
    budget_eng = get_budget()

    merchants = loader.load_merchants(temp_merchants_file)
    result = budget_eng.recommend_meals(merchants, budget=20000, require_combo=True)

    assert result.status == "SUCCESS", f"Expected SUCCESS, got {result.status}"
    assert len(result.recommendations) > 0, "Expected at least 1 meal recommendation"
    
    first_combo = result.recommendations[0]
    assert first_combo.total_cost <= 20000, "Recommended combo cost must be <= budget"
    assert first_combo.budget_remaining == 20000 - first_combo.total_cost
    
    # Assert combo composition contains food and beverage
    categories = set()
    for it in first_combo.items:
        cat_val = it.category.value if hasattr(it.category, "value") else str(it.category)
        categories.add(cat_val)

    assert "food" in categories, "Combo must contain at least 1 food item"
    assert "beverage" in categories, "Combo must contain at least 1 drink item"


def test_tier1_recommend_insufficient_budget(temp_merchants_file: str):
    """F3.2: Returns INSUFFICIENT_BUDGET status with positive deficit when budget is too low."""
    loader = get_loader()
    budget_eng = get_budget()

    merchants = loader.load_merchants(temp_merchants_file)
    # Rp 1,500 is lower than any food or drink in dataset (cheapest beverage is Rp 2,500)
    result = budget_eng.recommend_meals(merchants, budget=1500, require_combo=True)

    assert result.status == "INSUFFICIENT_BUDGET"
    assert result.budget == 1500
    assert len(result.recommendations) == 0, "No recommendations should be returned on insufficient budget"
    assert result.deficit > 0, "Deficit must be strictly positive"
    assert result.cheapest_item_price > 1500, "Cheapest price must be greater than budget"
    assert "kurang" in result.message.lower() or "insufficient" in result.message.lower() or result.deficit > 0


def test_tier1_recommend_exact_match_flag(temp_merchants_file: str):
    """F3.3: Correctly flags is_exact_match=True when combo cost exactly equals budget."""
    loader = get_loader()
    budget_eng = get_budget()

    merchants = loader.load_merchants(temp_merchants_file)
    # In Takor: Bento (12000) + Es Jeruk (4000) = 16000
    result = budget_eng.recommend_meals(merchants, budget=16000, require_combo=True)

    assert result.status == "SUCCESS"
    exact_matches = [rec for rec in result.recommendations if rec.is_exact_match]
    assert len(exact_matches) > 0, "Should contain at least one combo with is_exact_match=True"
    for em in exact_matches:
        assert em.total_cost == 16000, f"Exact match cost {em.total_cost} must be exactly 16000"
        assert em.budget_remaining == 0, "Exact match budget remaining must be 0"


def test_tier1_recommend_top_k_ranking(temp_merchants_file: str):
    """F3.4: Returns a ranked list of top-K recommendations ordered by satisfaction."""
    loader = get_loader()
    budget_eng = get_budget()

    merchants = loader.load_merchants(temp_merchants_file)
    result = budget_eng.recommend_meals(merchants, budget=35000, require_combo=True)

    assert result.status == "SUCCESS"
    assert len(result.recommendations) >= 1
    
    # Verify recommendations are sorted by total_satisfaction descending
    satisfactions = [rec.total_satisfaction for rec in result.recommendations]
    assert satisfactions == sorted(satisfactions, reverse=True), "Recommendations must be sorted by satisfaction desc"


def test_tier1_recommend_dietary_filtering(temp_merchants_file: str):
    """F3.5: Filters recommendations respecting required dietary preferences (e.g. vegetarian)."""
    loader = get_loader()
    budget_eng = get_budget()

    merchants = loader.load_merchants(temp_merchants_file)
    result = budget_eng.recommend_meals(
        merchants, budget=30000, dietary_preferences=["vegetarian"], require_combo=True
    )

    assert result.status == "SUCCESS"
    assert len(result.recommendations) > 0

    for combo in result.recommendations:
        for it in combo.items:
            tags = {t.lower() for t in it.dietary_tags}
            assert "vegetarian" in tags, f"Item {it.name} does not have required 'vegetarian' tag"


# ==============================================================================
# FEATURE 4 (F4): Flask Web App Routes & UI Flow
# ==============================================================================

def test_tier1_route_index_get(client):
    """F4.1: GET / returns 200, contains budget form input and UI Yellow elements."""
    response = client.get("/")
    assert response.status_code == 200
    html = response.get_data(as_text=True)

    assert "<form" in html, "Homepage must contain a budget input form"
    assert "budget" in html.lower(), "Homepage form must include budget input field"
    # Check for Makara Yellow UI brand elements or UI Yellow styling
    assert "#ffc700" in html.lower() or "yellow" in html.lower() or "smart meal finder" in html.lower()


def test_tier1_route_merchants_get(client):
    """F4.2: GET /merchants returns 200, lists UI canteens and merchants."""
    response = client.get("/merchants")
    assert response.status_code == 200
    html = response.get_data(as_text=True)

    assert "Dallas" in html, "Merchants page should list Kantin Dallas"
    assert "Fasilkom" in html, "Merchants page should list Kantin Fasilkom"


def test_tier1_route_recommend_post_valid(client):
    """F4.3: POST /recommend with valid budget renders recommendation results."""
    response = client.post(
        "/recommend",
        data={"budget": "20000", "canteen": "", "dietary": ""},
        follow_redirects=True,
    )
    assert response.status_code == 200
    html = response.get_data(as_text=True)

    assert "rekomendasi" in html.lower() or "recommendation" in html.lower() or "paket" in html.lower()
    assert "rp" in html.lower(), "Results should display price in Rupiah format"


def test_tier1_route_recommend_get_query(client):
    """F4.4: GET /recommend?budget=25000 handles URL query parameters."""
    response = client.get("/recommend?budget=25000")
    assert response.status_code == 200
    html = response.get_data(as_text=True)

    assert "25" in html or "hasil" in html.lower() or "rekomendasi" in html.lower()


def test_tier1_route_recommend_deficit_view(client):
    """F4.5: POST /recommend with budget below minimum renders deficit view."""
    response = client.post(
        "/recommend",
        data={"budget": "2000"},
        follow_redirects=True,
    )
    assert response.status_code == 200
    html = response.get_data(as_text=True)

    # Deficit or insufficient budget alert should be clearly rendered
    assert "kurang" in html.lower() or "insufficient" in html.lower() or "deficit" in html.lower() or "maaf" in html.lower()


# ==============================================================================
# FEATURE 5 (F5): REST API Endpoints
# ==============================================================================

def test_tier1_api_merchants_json(client):
    """F5.1: GET /api/merchants returns HTTP 200 and JSON array of merchants."""
    response = client.get("/api/merchants")
    assert response.status_code == 200
    assert "application/json" in response.content_type

    data = response.get_json()
    assert isinstance(data, (list, dict)), "API must return JSON array or dictionary"
    merchants_list = data if isinstance(data, list) else data.get("merchants", [])
    assert len(merchants_list) > 0, "API should return non-empty merchants list"


def test_tier1_api_recommend_valid(client):
    """F5.2: GET /api/recommend?budget=20000 returns valid JSON RecommendationResult."""
    response = client.get("/api/recommend?budget=20000")
    assert response.status_code == 200
    assert "application/json" in response.content_type

    data = response.get_json()
    assert data.get("status") == "SUCCESS", f"Expected SUCCESS, got {data.get('status')}"
    assert "recommendations" in data, "JSON response must include recommendations list"
    assert len(data["recommendations"]) > 0


def test_tier1_api_recommend_insufficient(client):
    """F5.3: GET /api/recommend?budget=1000 returns INSUFFICIENT_BUDGET status with deficit."""
    response = client.get("/api/recommend?budget=1000")
    assert response.status_code == 200
    assert "application/json" in response.content_type

    data = response.get_json()
    assert data.get("status") == "INSUFFICIENT_BUDGET"
    assert data.get("deficit", 0) > 0, "Deficit must be greater than 0"
    assert "cheapest_item_price" in data or "cheapest_combo_price" in data or data.get("deficit") > 0


def test_tier1_api_recommend_canteen_filter(client):
    """F5.4: GET /api/recommend?budget=30000&canteen=Fasilkom restricts results to Fasilkom."""
    response = client.get("/api/recommend?budget=30000&canteen=Fasilkom")
    assert response.status_code == 200
    data = response.get_json()

    assert data.get("status") == "SUCCESS"
    for rec in data.get("recommendations", []):
        for item in rec.get("items", []):
            assert item.get("canteen_name") == "Fasilkom", (
                f"Item {item.get('name')} belongs to {item.get('canteen_name')}, expected Fasilkom"
            )


def test_tier1_api_recommend_dietary_filter(client):
    """F5.5: GET /api/recommend?budget=30000&dietary=vegetarian restricts results to vegetarian items."""
    response = client.get("/api/recommend?budget=30000&dietary=vegetarian")
    assert response.status_code == 200
    data = response.get_json()

    assert data.get("status") == "SUCCESS"
    for rec in data.get("recommendations", []):
        for item in rec.get("items", []):
            tags = [t.lower() for t in item.get("dietary_tags", [])]
            assert "vegetarian" in tags, f"Item {item.get('name')} missing 'vegetarian' tag"
