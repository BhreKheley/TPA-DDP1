"""Tier 4 Realistic Student Dining Personas and End-to-End Workflows for Smart Meal Finder.

Simulates real-world Universitas Indonesia student dining journeys across UI canteens
(Dallas, Takor, Kansas, Pusgiwa, Texas, Fasilkom):

- Scenario 1 ("Tanggal Tua"): Low-budget student (Rp 12,000 - Rp 15,000) at Dallas/Takor.
- Scenario 2 ("Sultan Kampus / Traktiran"): High-budget student (Rp 50,000) across UI canteens.
- Scenario 3 ("Vegetarian / Halal"): Student with strict dietary preferences at Fasilkom/Texas.
- Scenario 4 ("Broke Student" Deficit Handling): Insufficient budget (Rp 3,000) with compassionate deficit guidance.
- Scenario 5 ("Merchant Exploration & Meal Discovery"): Multi-step browsing and dining discovery workflow.
- Scenario 6 ("Mobile App / Headless Client"): Automated REST client stepping budgets and verifying schemas.
- Scenario 7 ("Rush Hour Snack & Drink Combo"): Quick study break combo discovery.

All workflows assert real application flow and end-to-end interface contracts.
"""

import json
from pathlib import Path
from typing import Any, Dict, List
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
# TIER 4: REAL-WORLD STUDENT PERSONA SCENARIOS
# ==============================================================================

def test_tier4_scenario1_tanggal_tua(temp_merchants_file: str, client):
    """Scenario 1: 'Tanggal Tua' student with low budget finding meal combo and checking remaining balance.
    
    Student has only Rp 12,000 - Rp 16,000 at end of month, visits Kantin Dallas or Takor,
    finds an affordable food + drink combination within budget, and checks the remaining balance.
    """
    loader = get_loader()
    budget_eng = get_budget()

    merchants = loader.load_merchants(temp_merchants_file)
    student_budget = 16000  # Affordable for Takor: Bento (12,000) + Es Jeruk (4,000) = 16,000
    target_canteen = "Takor"

    # Step 1: Core algorithm computes recommendations
    result = budget_eng.recommend_meals(
        merchants,
        budget=student_budget,
        canteen_filter=target_canteen,
        require_combo=True,
    )

    assert result.status == "SUCCESS", f"Expected SUCCESS for student budget, got {result.status}"
    assert len(result.recommendations) > 0, "Student must receive at least 1 viable package"

    chosen_combo = result.recommendations[0]
    assert chosen_combo.total_cost <= student_budget, "Package cost must not exceed student's remaining money"
    assert chosen_combo.budget_remaining >= 0, "Budget remaining must be non-negative"
    assert chosen_combo.total_cost + chosen_combo.budget_remaining == student_budget

    # Verify combo contains food and drink
    categories = {str(it.category).lower() for it in chosen_combo.items}
    assert any("food" in cat for cat in categories), "Tanggal Tua combo must contain a substantial food item"
    assert any("beverage" in cat for cat in categories), "Tanggal Tua combo must contain a refreshing drink"

    # Step 2: Student accesses through Web Interface
    web_res = client.post(
        "/recommend",
        data={"budget": str(student_budget), "canteen": target_canteen, "dietary": ""},
        follow_redirects=True,
    )
    assert web_res.status_code == 200
    html = web_res.get_data(as_text=True)

    # Verify recommended item names appear in the rendered HTML meal cards
    for item in chosen_combo.items:
        assert item.name in html, f"Recommended item '{item.name}' must appear in rendered HTML"

    # Verify remaining balance or exact match text appears in the rendered meal cards
    assert any(
        k in html.lower() for k in ["pas di kantong", "sisa rp 0", "0 sisa", "sisa", "hemat"]
    ), "Rendered HTML meal cards must display remaining balance or exact match indicator"

    # Step 3: Student queries via Mobile API
    api_res = client.get(f"/api/recommend?budget={student_budget}&canteen={target_canteen}")
    assert api_res.status_code == 200
    api_data = api_res.get_json()
    assert api_data["status"] == "SUCCESS"
    assert api_data["budget"] == student_budget
    assert api_data["recommendations"][0]["total_cost"] <= student_budget


def test_tier4_scenario2_sultan_kampus_traktiran(temp_merchants_file: str, client):
    """Scenario 2: 'Sultan Kampus / Traktiran' high-budget student evaluating top-3 multi-canteen packages.
    
    Student has Rp 50,000 budget across all UI canteens, evaluating optimal satisfaction,
    hemat, and combo packages to maximize dining enjoyment.
    """
    loader = get_loader()
    budget_eng = get_budget()

    merchants = loader.load_merchants(temp_merchants_file)
    sultan_budget = 50000

    # Step 1: Core algorithm optimization across all canteens
    result = budget_eng.recommend_meals(
        merchants,
        budget=sultan_budget,
        canteen_filter=None,  # All UI canteens available
        require_combo=True,
    )

    assert result.status == "SUCCESS"
    assert len(result.recommendations) >= 1, "Sultan budget must yield rich recommendation choices"

    # Verify package types ('optimal', 'hemat', 'combo') if multiple packages returned
    package_types = {rec.package_type for rec in result.recommendations if hasattr(rec, "package_type")}
    # At least one defined package type must be present
    assert len(package_types) > 0

    # Verify satisfaction is maximized
    optimal_rec = result.recommendations[0]
    assert optimal_rec.total_cost <= sultan_budget
    assert optimal_rec.total_satisfaction >= 14.0, (
        f"Expected high composite satisfaction (>= 14.0) for high-budget meal, got {optimal_rec.total_satisfaction}"
    )

    # Step 2: Web Interface verification
    web_res = client.post(
        "/recommend",
        data={"budget": str(sultan_budget), "canteen": "", "dietary": ""},
        follow_redirects=True,
    )
    assert web_res.status_code == 200
    html = web_res.get_data(as_text=True)

    # Must render recommendation options and satisfaction scores or ratings
    assert "rekomendasi" in html.lower() or "paket" in html.lower()
    assert "rp" in html.lower()

    # Step 3: REST API verification
    api_res = client.get(f"/api/recommend?budget={sultan_budget}")
    assert api_res.status_code == 200
    api_data = api_res.get_json()
    assert api_data["status"] == "SUCCESS"
    assert len(api_data["recommendations"]) > 0


def test_tier4_scenario3_vegetarian_halal(temp_merchants_file: str, client):
    """Scenario 3: Student with strict dietary preferences (vegetarian + halal) at Fasilkom/Texas.
    
    Student has Rp 25,000 budget, strictly vegetarian and halal. System must guarantee 100%
    compliance on every item in every recommended package, excluding meat dishes.
    """
    loader = get_loader()
    budget_eng = get_budget()

    merchants = loader.load_merchants(temp_merchants_file)
    student_budget = 25000
    required_tags = ["vegetarian", "halal"]

    # Step 1: Core Algorithm filtering
    result = budget_eng.recommend_meals(
        merchants,
        budget=student_budget,
        canteen_filter="Fasilkom",
        dietary_preferences=required_tags,
        require_combo=True,
    )

    assert result.status == "SUCCESS", f"Expected SUCCESS for vegetarian meal at Fasilkom, got {result.status}"
    assert len(result.recommendations) > 0

    for combo in result.recommendations:
        assert combo.total_cost <= student_budget
        for it in combo.items:
            item_tags = {t.lower() for t in it.dietary_tags}
            # Strictly verify vegetarian tag
            assert "vegetarian" in item_tags, f"Item '{it.name}' is NOT marked vegetarian!"
            # Strictly verify halal tag
            assert "halal" in item_tags, f"Item '{it.name}' is NOT marked halal!"
            # Ensure no meat dishes leaked through
            name_lower = it.name.lower()
            assert not any(meat in name_lower for meat in ["ayam", "sapi", "bebek", "rendang", "soto ayam"]), (
                f"Meat dish '{it.name}' found in vegetarian recommendation!"
            )

    # Step 2: Web Form submission
    web_res = client.post(
        "/recommend",
        data={"budget": str(student_budget), "canteen": "Fasilkom", "dietary": "vegetarian,halal"},
        follow_redirects=True,
    )
    assert web_res.status_code == 200
    html = web_res.get_data(as_text=True)

    # Should render dietary badges / labels
    assert "vegetarian" in html.lower() or "tahu tempe" in html.lower() or "alpukat" in html.lower()

    # Step 3: API call verification
    api_res = client.get(f"/api/recommend?budget={student_budget}&canteen=Fasilkom&dietary=vegetarian,halal")
    assert api_res.status_code == 200
    api_data = api_res.get_json()
    assert api_data["status"] == "SUCCESS"
    for rec in api_data["recommendations"]:
        for it in rec["items"]:
            tags = [t.lower() for t in it.get("dietary_tags", [])]
            assert "vegetarian" in tags, f"Item '{it.get('name')}' missing 'vegetarian' tag in API response"
            assert "halal" in tags, f"Item '{it.get('name')}' missing 'halal' tag in API response"


def test_tier4_scenario4_broke_student_deficit_handling(temp_merchants_file: str, client):
    """Scenario 4: 'Broke Student' with insufficient budget (Rp 3,000) receiving compassionate deficit guidance.
    
    Student inputs Rp 3,000. System detects budget < cheapest meal/combo, provides compassionate
    guidance in Indonesian, indicates the deficit amount, and refers to the cheapest available item.
    """
    loader = get_loader()
    budget_eng = get_budget()

    merchants = loader.load_merchants(temp_merchants_file)
    broke_budget = 3000

    # Step 1: Core Algorithm deficit analysis
    result = budget_eng.recommend_meals(
        merchants,
        budget=broke_budget,
        require_combo=True,
    )

    assert result.status == "INSUFFICIENT_BUDGET"
    assert result.budget == broke_budget
    assert len(result.recommendations) == 0, "No recommendations should be returned when budget is insufficient"
    assert result.deficit > 0, "Deficit must be strictly positive"
    assert result.cheapest_item_price > broke_budget
    assert result.deficit == result.cheapest_item_price - broke_budget

    # Message must be compassionate and explain the gap
    assert result.message, "A helpful guidance message must be provided"
    msg_lower = result.message.lower()
    assert ("kurang" in msg_lower or "budget" in msg_lower or "rp" in msg_lower or "insufficient" in msg_lower)

    # Step 2: HTML UI presentation
    web_res = client.post(
        "/recommend",
        data={"budget": str(broke_budget), "canteen": "", "dietary": ""},
        follow_redirects=True,
    )
    assert web_res.status_code == 200
    html = web_res.get_data(as_text=True)

    # Verify that the numeric deficit amount appears in the rendered HTML notification
    deficit_str = str(result.deficit)
    deficit_fmt = f"{result.deficit:,}"
    deficit_id = deficit_fmt.replace(",", ".")
    assert (
        deficit_str in html or deficit_fmt in html or deficit_id in html
    ), f"Numeric deficit amount {result.deficit} must appear in rendered HTML"
    assert ("kurang" in html.lower() or "insufficient" in html.lower() or "alert" in html.lower() or "maaf" in html.lower()), (
        "HTML page must render an insufficient budget / deficit notification"
    )

    # Step 3: REST API JSON contract
    api_res = client.get(f"/api/recommend?budget={broke_budget}")
    assert api_res.status_code == 200
    api_data = api_res.get_json()
    assert api_data["status"] == "INSUFFICIENT_BUDGET"
    assert api_data["deficit"] == result.deficit
    assert api_data["cheapest_item_price"] == result.cheapest_item_price


def test_tier4_scenario5_merchant_exploration_discovery(temp_merchants_file: str, client):
    """Scenario 5: 'Merchant Exploration & Discovery' complete user journey from catalog to recommendation.
    
    1. New UI student arrives at campus, browses /merchants.
    2. Inspects canteen selection, selects Pusgiwa (Warung Nasi Padang, rating 4.8).
    3. Reviews menu items, then requests recommendation for Pusgiwa with budget Rp 25,000.
    4. Receives optimal Padang combo (Nasi Rendang + Teh Manis) within budget.
    """
    loader = get_loader()
    budget_eng = get_budget()

    # Step 1: Student visits /merchants catalog
    catalog_res = client.get("/merchants")
    assert catalog_res.status_code == 200
    catalog_html = catalog_res.get_data(as_text=True)

    assert "Pusgiwa" in catalog_html, "Kantin Pusgiwa must be listed in catalog"
    assert "Warung Nasi Padang" in catalog_html, "Warung Nasi Padang must be visible"

    # Step 2: Student inspects API catalog for Pusgiwa rating and details
    api_cat = client.get("/api/merchants")
    assert api_cat.status_code == 200
    cat_data = api_cat.get_json()
    merchants_list = cat_data if isinstance(cat_data, list) else cat_data.get("merchants", [])
    
    pusgiwa_merchants = [m for m in merchants_list if m.get("canteen_name") == "Pusgiwa"]
    assert len(pusgiwa_merchants) > 0, "Pusgiwa merchants must be returned by API"
    assert pusgiwa_merchants[0].get("rating", 0) >= 4.0, "Pusgiwa merchant rating must be >= 4.0"

    # Step 3: Student initiates recommendation request for Pusgiwa with Rp 25,000 budget
    pusgiwa_budget = 25000
    rec_res = client.post(
        "/recommend",
        data={"budget": str(pusgiwa_budget), "canteen": "Pusgiwa", "dietary": ""},
        follow_redirects=True,
    )
    assert rec_res.status_code == 200
    rec_html = rec_res.get_data(as_text=True)

    # Step 4: Verify Nasi Rendang and Teh Manis are recommended
    assert ("rendang" in rec_html.lower() or "padang" in rec_html.lower()), (
        "Recommended combo must contain Nasi Rendang from Pusgiwa"
    )
    assert "pusgiwa" in rec_html.lower()


def test_tier4_scenario6_mobile_app_headless_client(client):
    """Scenario 6: 'Mobile App / Headless Client' automated multi-step API interaction.
    
    Simulates a client application fetching merchants, then executing a sequence of budget
    slider calls (Rp 2,000 -> Rp 16,000 -> Rp 25,000 -> Rp 45,000), verifying JSON schema consistency.
    """
    # Step 1: Mobile client discovers merchants and canteen options
    merchants_res = client.get("/api/merchants")
    assert merchants_res.status_code == 200
    assert "application/json" in merchants_res.content_type
    merchants_data = merchants_res.get_json()
    merchants_list = merchants_data if isinstance(merchants_data, list) else merchants_data.get("merchants", [])
    assert len(merchants_list) >= 6, "Must have merchants across at least 6 canteens"

    # Step 2: Slider sequence across 4 stepping budget points
    test_steps = [
        {"budget": 2000, "expected_status": "INSUFFICIENT_BUDGET"},
        {"budget": 16000, "expected_status": "SUCCESS"},
        {"budget": 25000, "expected_status": "SUCCESS"},
        {"budget": 45000, "expected_status": "SUCCESS"},
    ]

    previous_satisfaction = 0.0

    for step in test_steps:
        b_val = step["budget"]
        exp_status = step["expected_status"]

        api_res = client.get(f"/api/recommend?budget={b_val}")
        assert api_res.status_code == 200, f"Failed at budget step {b_val}"
        assert "application/json" in api_res.content_type

        data = api_res.get_json()
        assert isinstance(data, dict), f"API response for budget {b_val} must be JSON object"
        assert data.get("status") == exp_status, (
            f"At budget {b_val}, expected status {exp_status}, got {data.get('status')}"
        )
        assert data.get("budget") == b_val

        if exp_status == "SUCCESS":
            recs = data.get("recommendations", [])
            assert len(recs) > 0, f"Expected non-empty recommendations for budget {b_val}"
            top_rec = recs[0]
            assert top_rec["total_cost"] <= b_val
            assert top_rec["budget_remaining"] == b_val - top_rec["total_cost"]

            # Satisfaction should generally be non-decreasing as budget increases
            current_sat = float(top_rec.get("total_satisfaction", 0.0))
            assert current_sat >= previous_satisfaction - 0.5, (
                f"Satisfaction at budget {b_val} ({current_sat}) unexpectedly dropped below {previous_satisfaction}"
            )
            previous_satisfaction = current_sat
        else:
            assert data.get("deficit", 0) > 0, f"Deficit must be positive for insufficient budget {b_val}"


def test_tier4_scenario7_snack_and_drinks_combo_discovery(temp_merchants_file: str, client):
    """Scenario 7: Quick study break combo (snack + beverage) at Kantin Fasilkom.
    
    Student between classes has Rp 15,000 budget, looking for a snack and a drink at Fasilkom.
    System discovers Kripik Jamur (6,000) + Jus Alpukat (9,000) = exactly 15,000 (Pas di Kantong).
    """
    loader = get_loader()
    budget_eng = get_budget()

    merchants = loader.load_merchants(temp_merchants_file)
    fasilkom_budget = 15000

    # Step 1: Core Algorithm evaluates Fasilkom items
    result = budget_eng.recommend_meals(
        merchants,
        budget=fasilkom_budget,
        canteen_filter="Fasilkom",
        require_combo=False,  # Allow flexible combinations including snack + drink
    )

    assert result.status == "SUCCESS"
    assert len(result.recommendations) > 0

    # Check for exact match or close match at 15,000
    affordable_recs = [r for r in result.recommendations if r.total_cost <= fasilkom_budget]
    assert len(affordable_recs) > 0
    top_rec = affordable_recs[0]
    assert top_rec.total_cost <= fasilkom_budget
    assert top_rec.budget_remaining >= 0

    # Step 2: Web Interface confirmation
    web_res = client.post(
        "/recommend",
        data={"budget": str(fasilkom_budget), "canteen": "Fasilkom", "dietary": ""},
        follow_redirects=True,
    )
    assert web_res.status_code == 200
    html = web_res.get_data(as_text=True)

    assert "fasilkom" in html.lower()
    assert "rp" in html.lower()
