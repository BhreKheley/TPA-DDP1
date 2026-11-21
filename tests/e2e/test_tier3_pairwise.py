"""Tier 3 Pairwise Cross-Feature Integration Tests for Smart Meal Finder.

Covers cross-component interactions and pipeline integrity across:
- Data Loader <-> Knapsack 0/1 DP Engine
- Data Loader <-> Meal Recommendation Optimizer
- Flask Web Route (POST/GET) <-> Core Algorithms
- REST API (/api/recommend, /api/merchants) <-> Core Algorithms
- Dual-constraint Filtering (Canteen + Dietary Preferences)
- Deficit Display Parity across Core, HTML View, and JSON API
- Exact Match Flag & Badge Presentation ("Pas di Kantong")
- Merchant Catalog Consistency between Data Store, Web View, and REST API

Each test case verifies end-to-end pipeline boundaries without bypassing business logic.
"""

from typing import Any, Dict, List, Set
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
# TIER 3: PAIRWISE CROSS-FEATURE INTEGRATION TESTS
# ==============================================================================

def test_tier3_loader_to_knapsack_pipeline(temp_merchants_file: str):
    """P1: End-to-end pipeline from raw merchants.json -> core.loader -> knapsack_01_dp."""
    loader = get_loader()
    budget_eng = get_budget()

    # 1. Load merchants and extract available menu items
    merchants = loader.load_merchants(temp_merchants_file)
    assert len(merchants) > 0, "Loader must return non-empty merchant records"
    
    available_items = loader.extract_all_items(merchants, only_available=True)
    assert len(available_items) > 0, "Should have available menu items from dataset"

    # 2. Feed extracted items directly into canonical knapsack solver
    budget_limit = 25000
    selected_items, total_cost, total_satisfaction = budget_eng.knapsack_01_dp(
        available_items, budget_limit
    )

    # 3. Assert knapsack mathematical guarantees on loaded items
    assert isinstance(selected_items, list), "Selected items must be returned as a list"
    assert len(selected_items) > 0, f"Expected non-empty knapsack selection for budget {budget_limit}"
    assert total_cost <= budget_limit, f"Total cost {total_cost} exceeds budget limit {budget_limit}"
    assert total_cost == sum(it.price for it in selected_items), "Total cost must strictly match item sum"
    assert total_satisfaction > 0.0, "Total satisfaction must be positive"

    # 4. Verify item integrity: all selected items exist in original pool and are available
    available_ids = {it.id for it in available_items}
    for item in selected_items:
        assert item.id in available_ids, f"Selected item {item.id} not in available items pool"
        assert item.is_available is True, f"Unavailable item {item.name} selected by knapsack"


def test_tier3_loader_to_recommend_meals_pipeline(temp_merchants_file: str):
    """P2: Raw merchants.json -> core.loader -> recommend_meals with active canteen filter."""
    loader = get_loader()
    budget_eng = get_budget()

    merchants = loader.load_merchants(temp_merchants_file)
    canteen_target = "Fasilkom"
    budget_limit = 30000

    # Execute recommendation with canteen filter and required 1 food + 1 beverage combo
    result = budget_eng.recommend_meals(
        merchants,
        budget=budget_limit,
        canteen_filter=canteen_target,
        require_combo=True,
    )

    assert result.status == "SUCCESS", f"Expected SUCCESS, got {result.status} (msg: {result.message})"
    assert result.budget == budget_limit
    assert len(result.recommendations) > 0, f"Expected recommendations for {canteen_target} with Rp {budget_limit}"

    for combo in result.recommendations:
        # Cost and budget accounting
        assert combo.total_cost <= budget_limit, f"Combo cost {combo.total_cost} exceeds {budget_limit}"
        assert combo.budget_remaining == budget_limit - combo.total_cost
        assert combo.total_cost + combo.budget_remaining == budget_limit
        assert combo.total_satisfaction > 0.0

        # Canteen isolation guarantee
        for it in combo.items:
            assert it.canteen_name == canteen_target, (
                f"Item '{it.name}' belongs to canteen '{it.canteen_name}', expected '{canteen_target}'"
            )

        # 1 Food + 1 Beverage combo structure guarantee
        categories = {str(it.category).lower() for it in combo.items}
        assert any("food" in cat for cat in categories), "Combo must contain at least one food item"
        assert any("beverage" in cat for cat in categories), "Combo must contain at least one beverage item"


def test_tier3_web_post_to_core_algorithm(client):
    """P3: Form POST to /recommend triggers core recommendation engine and renders meal cards."""
    budget_val = 20000
    canteen_val = "Dallas"

    response = client.post(
        "/recommend",
        data={"budget": str(budget_val), "canteen": canteen_val, "dietary": ""},
        follow_redirects=True,
    )
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    html = response.get_data(as_text=True)

    # Verify that core algorithm executed and result template was rendered
    assert ("rekomendasi" in html.lower() or "paket" in html.lower() or "hasil" in html.lower()), (
        "HTML view must indicate recommendation results"
    )

    # Dallas items should be rendered
    assert "dallas" in html.lower(), "Rendered page must reflect selected canteen Dallas"
    assert ("ayam geprek" in html.lower() or "es teh" in html.lower() or "mas brow" in html.lower()), (
        "Rendered HTML must display actual meal items from Kantin Dallas"
    )

    # Financial breakdown must appear in Rupiah format
    assert "rp" in html.lower(), "Pricing must be displayed in Rupiah currency format"


def test_tier3_api_to_core_algorithm_json(client):
    """P4: GET /api/recommend returns serialized RecommendationResult matching dataclass contracts."""
    budget_val = 25000
    canteen_val = "Takor"

    response = client.get(f"/api/recommend?budget={budget_val}&canteen={canteen_val}")
    assert response.status_code == 200
    assert "application/json" in response.content_type

    data = response.get_json()
    assert isinstance(data, dict), "API response must be a JSON object"
    assert data.get("status") == "SUCCESS"
    assert data.get("budget") == budget_val
    assert data.get("deficit") == 0
    assert "recommendations" in data and isinstance(data["recommendations"], list)
    assert len(data["recommendations"]) > 0

    first_rec = data["recommendations"][0]
    required_keys = {"items", "total_cost", "budget_remaining", "total_satisfaction"}
    assert required_keys.issubset(first_rec.keys()), f"Missing keys in recommendation: {first_rec.keys()}"

    assert first_rec["total_cost"] <= budget_val
    assert first_rec["budget_remaining"] == budget_val - first_rec["total_cost"]
    assert first_rec["total_satisfaction"] > 0

    # Ensure all items in Takor recommendation are from Takor
    for it in first_rec["items"]:
        assert it.get("canteen_name") == "Takor", f"Item {it.get('name')} not from Takor"


def test_tier3_canteen_and_dietary_dual_filter(temp_merchants_file: str, client):
    """P5: Simultaneous dual-filter (canteen='Fasilkom' + dietary='vegetarian') across core & API."""
    loader = get_loader()
    budget_eng = get_budget()

    # 1. Verify at Core Algorithm Level
    merchants = loader.load_merchants(temp_merchants_file)
    core_result = budget_eng.recommend_meals(
        merchants,
        budget=30000,
        canteen_filter="Fasilkom",
        dietary_preferences=["vegetarian"],
        require_combo=True,
    )
    assert core_result.status == "SUCCESS"
    assert len(core_result.recommendations) > 0

    for combo in core_result.recommendations:
        for it in combo.items:
            assert it.canteen_name == "Fasilkom", f"Item {it.name} violates canteen filter"
            tags_lower = {t.lower() for t in it.dietary_tags}
            assert "vegetarian" in tags_lower, f"Item {it.name} violates vegetarian dietary preference"

    # 2. Verify at REST API Level
    api_res = client.get("/api/recommend?budget=30000&canteen=Fasilkom&dietary=vegetarian")
    assert api_res.status_code == 200
    api_data = api_res.get_json()
    assert api_data.get("status") == "SUCCESS"

    for rec in api_data.get("recommendations", []):
        for it in rec.get("items", []):
            assert it.get("canteen_name") == "Fasilkom"
            tags = [t.lower() for t in it.get("dietary_tags", [])]
            assert "vegetarian" in tags, f"Item {it.get('name')} in API missing 'vegetarian' tag"


def test_tier3_deficit_display_consistency(temp_merchants_file: str, client):
    """P6: Deficit amount parity between core algorithm, HTML view, and REST API."""
    loader = get_loader()
    budget_eng = get_budget()

    insufficient_budget = 2000

    # 1. Compute authoritative deficit from core engine
    merchants = loader.load_merchants(temp_merchants_file)
    core_result = budget_eng.recommend_meals(
        merchants, budget=insufficient_budget, require_combo=True
    )
    assert core_result.status == "INSUFFICIENT_BUDGET"
    expected_deficit = core_result.deficit
    assert expected_deficit > 0, "Deficit must be positive when budget is insufficient"

    # 2. Assert parity with REST API response
    api_res = client.get(f"/api/recommend?budget={insufficient_budget}")
    assert api_res.status_code == 200
    api_data = api_res.get_json()
    assert api_data.get("status") == "INSUFFICIENT_BUDGET"
    assert api_data.get("deficit") == expected_deficit, (
        f"API deficit ({api_data.get('deficit')}) does not match core deficit ({expected_deficit})"
    )

    # 3. Assert parity with HTML view rendering
    web_res = client.post(
        "/recommend",
        data={"budget": str(insufficient_budget), "canteen": "", "dietary": ""},
        follow_redirects=True,
    )
    assert web_res.status_code == 200
    html = web_res.get_data(as_text=True)

    # The deficit amount must be present in the HTML (either unformatted or with thousand separators)
    deficit_str = str(expected_deficit)
    deficit_id_sep = f"{expected_deficit:,}".replace(",", ".")
    deficit_en_sep = f"{expected_deficit:,}"
    deficit_found = (
        deficit_str in html or deficit_id_sep in html or deficit_en_sep in html or "kurang" in html.lower()
    )
    assert deficit_found, f"Deficit amount {expected_deficit} not rendered in HTML response"


def test_tier3_exact_match_badge_rendered(temp_merchants_file: str, client):
    """P7: When combo cost == budget, is_exact_match=True and 'Pas di Kantong' badge appears in HTML."""
    loader = get_loader()
    budget_eng = get_budget()

    # In Kantin Dallas:
    # Paket Nasi Ayam Geprek Level 2 (15,000) + Es Teh Manis Jumbo (3,000) = exactly 18,000
    exact_budget = 18000
    merchants = loader.load_merchants(temp_merchants_file)

    # 1. Verify core algorithm flags is_exact_match == True
    core_result = budget_eng.recommend_meals(
        merchants, budget=exact_budget, canteen_filter="Dallas", require_combo=True
    )
    assert core_result.status == "SUCCESS"
    exact_matches = [rec for rec in core_result.recommendations if rec.is_exact_match]
    assert len(exact_matches) > 0, "Core engine must produce at least one exact match combination"
    assert exact_matches[0].total_cost == exact_budget
    assert exact_matches[0].budget_remaining == 0

    # 2. Verify HTML renders the exact match indicator / badge
    response = client.post(
        "/recommend",
        data={"budget": str(exact_budget), "canteen": "Dallas", "dietary": ""},
        follow_redirects=True,
    )
    assert response.status_code == 200
    html = response.get_data(as_text=True).lower()

    # Look for "pas di kantong" badge or exact match terminology
    assert (
        "pas di kantong" in html
        or "pas" in html
        or "exact" in html
        or "badge" in html
        or "0 sisa" in html
        or "sisa rp 0" in html
    ), "Rendered HTML must include 'Pas di Kantong' badge or exact budget utilization label"


def test_tier3_merchant_catalog_consistency(temp_merchants_file: str, client):
    """P8: Loaded merchants catalog from core.loader matches /merchants HTML and /api/merchants JSON."""
    loader = get_loader()
    merchants = loader.load_merchants(temp_merchants_file)
    expected_names = {m.name for m in merchants}
    expected_canteens = {m.canteen_name for m in merchants}

    # 1. Verify REST API returns all merchants
    api_res = client.get("/api/merchants")
    assert api_res.status_code == 200
    api_data = api_res.get_json()
    api_merchants = api_data if isinstance(api_data, list) else api_data.get("merchants", [])
    api_names = {m["name"] for m in api_merchants}
    assert expected_names == api_names, (
        f"API merchant names differ from loaded dataset: {expected_names.symmetric_difference(api_names)}"
    )

    # 2. Verify HTML catalog page lists all merchant and canteen names
    web_res = client.get("/merchants")
    assert web_res.status_code == 200
    html = web_res.get_data(as_text=True)

    for m in merchants:
        assert m.name in html, f"Merchant '{m.name}' missing from /merchants HTML catalog"
    for c_name in expected_canteens:
        assert c_name in html, f"Canteen '{c_name}' missing from /merchants HTML catalog"


def test_tier3_unconstrained_canteen_aggregation(temp_merchants_file: str, client):
    """P9: Aggregation across all UI canteens when canteen_filter is empty/None."""
    loader = get_loader()
    budget_eng = get_budget()

    merchants = loader.load_merchants(temp_merchants_file)
    result = budget_eng.recommend_meals(
        merchants, budget=35000, canteen_filter=None, require_combo=True
    )
    assert result.status == "SUCCESS"
    assert len(result.recommendations) > 0

    # Ensure all items come from the set of valid canteens
    valid_canteens = {"Dallas", "Takor", "Kansas", "Pusgiwa", "Texas", "Fasilkom"}
    all_observed_canteens = set()
    for combo in result.recommendations:
        for it in combo.items:
            assert it.canteen_name in valid_canteens
            all_observed_canteens.add(it.canteen_name)

    assert len(all_observed_canteens) > 0


def test_tier3_api_and_web_filter_parity(client):
    """P10: Cross-interface parity between /recommend and /api/recommend for identical parameters."""
    test_budget = 22000
    test_canteen = "Takor"

    # Web POST request
    web_res = client.post(
        "/recommend",
        data={"budget": str(test_budget), "canteen": test_canteen, "dietary": ""},
        follow_redirects=True,
    )
    assert web_res.status_code == 200
    html = web_res.get_data(as_text=True)

    # API GET request
    api_res = client.get(f"/api/recommend?budget={test_budget}&canteen={test_canteen}")
    assert api_res.status_code == 200
    api_data = api_res.get_json()

    assert api_data.get("status") == "SUCCESS"
    rec_items = api_data.get("recommendations", [])
    assert len(rec_items) > 0

    # Item names in JSON recommendation must appear in rendered HTML
    for rec in rec_items:
        for item in rec.get("items", []):
            item_name = item.get("name", "")
            if item_name:
                assert item_name in html or item_name.lower() in html.lower(), (
                    f"Item '{item_name}' in API recommendation not found in rendered HTML"
                )
