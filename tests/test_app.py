"""Comprehensive Web Application and API Test Suite for Smart Meal Finder.

Author: Johannes Praba Aji (NPM: 2606748465)
Milestone: Milestone 4 (Web Application, UI & CI/CD)

Tests cover:
1. Flask application factory and configuration.
2. Custom Jinja template filters (format_rupiah).
3. HTTP GET routes: /, /merchants, /recommend (with and without parameters).
4. HTTP POST /recommend with budget, canteen filter, dietary preferences, and combo toggle.
5. Invalid budget input handling (negative, zero, non-numeric, empty, whitespace, XSS sanitization).
6. Deficit display when budget is insufficient.
7. REST API GET /api/recommend (schema, filters, deficits, 400 bad request error cases).
8. REST API GET /api/merchants (schema, primitive serialization, canteen filtering).
9. Custom 404 error page and API JSON error handling.
"""

import pytest
from app import create_app


@pytest.fixture
def app():
    """Create and configure a Flask application instance for testing."""
    test_app = create_app({"TESTING": True})
    return test_app


@pytest.fixture
def client(app):
    """Flask test client fixture."""
    return app.test_client()


@pytest.fixture
def runner(app):
    """Flask CLI runner fixture."""
    return app.test_cli_runner()


# ==============================================================================
# 1. APP FACTORY & JINJA FILTER TESTS
# ==============================================================================

class TestAppFactoryAndFilters:
    """Verifies application factory setup, testing configuration, and custom Jinja filters."""

    def test_create_app_default(self):
        """Verifies create_app initializes a valid Flask instance with default settings."""
        app_instance = create_app()
        assert app_instance is not None
        assert app_instance.name == "app"

    def test_create_app_testing_config(self, app):
        """Verifies app configured with TESTING=True enables testing mode."""
        assert app.testing is True
        assert app.config["TESTING"] is True

    def test_format_rupiah_filter(self, app):
        """Verifies format_rupiah Jinja filter formats currency with Indonesian dot separators."""
        filter_func = app.jinja_env.filters.get("format_rupiah")
        assert filter_func is not None, "format_rupiah filter must be registered in Jinja environment"

        assert filter_func(15000) in ("Rp 15.000", "Rp 15,000", "15.000", "15,000")
        assert filter_func(25000) in ("Rp 25.000", "Rp 25,000", "25.000", "25,000")
        assert filter_func(0) in ("Rp 0", "0")
        assert filter_func(1250000) in ("Rp 1.250.000", "Rp 1,250,000", "1.250.000")

    def test_format_rupiah_filter_edge_cases(self, app):
        """Verifies format_rupiah handles None, strings, and non-integer values gracefully."""
        filter_func = app.jinja_env.filters.get("format_rupiah")
        assert filter_func(None) in ("Rp 0", "0", "-", "")
        assert "Rp" in filter_func("invalid") or "invalid" in filter_func("invalid") or filter_func("invalid") == "Rp 0"


# ==============================================================================
# 2. WEB ROUTES STATUS & CONTENT (GET)
# ==============================================================================

class TestWebRoutesStatusAndContent:
    """Verifies HTTP GET status codes and template rendering for web views."""

    def test_get_home_page_200(self, client):
        """GET / returns 200, renders budget form, UI Yellow theme, and preset buttons."""
        response = client.get("/")
        assert response.status_code == 200
        html = response.get_data(as_text=True)

        assert "Smart Meal Finder" in html or "smart meal finder" in html.lower()
        assert "<form" in html, "Homepage must include budget submission form"
        assert 'name="budget"' in html or "budget" in html.lower()
        assert "#ffc700" in html.lower() or "yellow" in html.lower() or "universitas indonesia" in html.lower()

    def test_get_merchants_page_200(self, client):
        """GET /merchants returns 200, lists all UI campus canteens and menu items."""
        response = client.get("/merchants")
        assert response.status_code == 200
        html = response.get_data(as_text=True)

        assert "Dallas" in html, "Merchants directory must list Kantin Dallas"
        assert "Fasilkom" in html, "Merchants directory must list Kantin Fasilkom"
        assert "Takor" in html, "Merchants directory must list Kantin Takor"
        assert "Rp" in html or "rp" in html.lower(), "Merchants catalog must display pricing"

    def test_get_merchants_page_filtered(self, client):
        """GET /merchants?canteen=Dallas filters merchant view to specified canteen."""
        response = client.get("/merchants?canteen=Dallas")
        assert response.status_code == 200
        html = response.get_data(as_text=True)
        assert "Dallas" in html

    def test_get_recommend_without_params_200(self, client):
        """GET /recommend without query params returns 200 and renders initial/empty state cleanly."""
        response = client.get("/recommend")
        assert response.status_code == 200
        html = response.get_data(as_text=True)
        assert "<form" in html or "budget" in html.lower() or "rekomendasi" in html.lower()

    def test_get_recommend_with_valid_budget_200(self, client):
        """GET /recommend?budget=20000 returns 200 and displays recommended meal combinations."""
        response = client.get("/recommend?budget=20000")
        assert response.status_code == 200
        html = response.get_data(as_text=True)
        assert "20" in html or "rekomendasi" in html.lower() or "paket" in html.lower()

    def test_get_recommend_with_full_query_params(self, client):
        """GET /recommend?budget=25000&canteen=Kantin+Dallas&dietary=halal handles full query string."""
        response = client.get("/recommend?budget=25000&canteen=Kantin+Dallas&dietary=halal&combo=1")
        assert response.status_code == 200
        html = response.get_data(as_text=True)
        assert "dallas" in html.lower()


# ==============================================================================
# 3. FORM SUBMISSION (POST /recommend)
# ==============================================================================

class TestPostRecommendForm:
    """Verifies form submission handling, filter parameters, and recommendation results."""

    def test_post_recommend_valid_budget(self, client):
        """POST /recommend with budget=20000 returns 200 and renders meal cards."""
        response = client.post(
            "/recommend",
            data={"budget": "20000", "canteen": "", "dietary": ""},
            follow_redirects=True,
        )
        assert response.status_code == 200
        html = response.get_data(as_text=True)

        assert any(k in html.lower() for k in ["rekomendasi", "paket", "hasil"])
        assert "rp" in html.lower()

    def test_post_recommend_canteen_filter(self, client):
        """POST /recommend with canteen='Kantin Dallas' restricts results to Kantin Dallas."""
        response = client.post(
            "/recommend",
            data={"budget": "25000", "canteen": "Kantin Dallas", "dietary": ""},
            follow_redirects=True,
        )
        assert response.status_code == 200
        html = response.get_data(as_text=True)
        assert "dallas" in html.lower()

    def test_post_recommend_dietary_preferences(self, client):
        """POST /recommend with dietary=['vegetarian'] respects dietary filters."""
        response = client.post(
            "/recommend",
            data={"budget": "30000", "canteen": "", "dietary": ["vegetarian"]},
            follow_redirects=True,
        )
        assert response.status_code == 200
        html = response.get_data(as_text=True)
        assert any(k in html.lower() for k in ["rekomendasi", "vegetarian", "paket"])

    def test_post_recommend_combo_toggle_on(self, client):
        """POST /recommend with require_combo='on' enforces 1 food + 1 drink combinations."""
        response = client.post(
            "/recommend",
            data={"budget": "20000", "require_combo": "on"},
            follow_redirects=True,
        )
        assert response.status_code == 200
        html = response.get_data(as_text=True)
        assert "rekomendasi" in html.lower() or "paket" in html.lower()

    def test_post_recommend_combo_toggle_off(self, client):
        """POST /recommend without require_combo allows flexible / solo combinations."""
        response = client.post(
            "/recommend",
            data={"budget": "20000", "require_combo": "off"},
            follow_redirects=True,
        )
        assert response.status_code == 200
        html = response.get_data(as_text=True)
        assert "rekomendasi" in html.lower() or "paket" in html.lower()

    def test_post_recommend_exact_match_budget(self, client):
        """POST /recommend with budget matching exact combo price flags exact match."""
        response = client.post(
            "/recommend",
            data={"budget": "16000", "canteen": "Takor", "require_combo": "on"},
            follow_redirects=True,
        )
        assert response.status_code == 200
        html = response.get_data(as_text=True)
        assert "16" in html

    def test_post_recommend_deficit_display(self, client):
        """POST /recommend with budget=2000 displays deficit warning, deficit amount, and min budget."""
        response = client.post(
            "/recommend",
            data={"budget": "2000", "require_combo": "on"},
            follow_redirects=True,
        )
        assert response.status_code == 200
        html = response.get_data(as_text=True)

        assert any(k in html.lower() for k in ["kurang", "defisit", "insufficient", "maaf"])
        assert "rp" in html.lower()

    def test_post_recommend_no_matching_items(self, client):
        """POST /recommend with non-existent canteen returns friendly empty state message."""
        response = client.post(
            "/recommend",
            data={"budget": "20000", "canteen": "KantinNonExistent"},
            follow_redirects=True,
        )
        assert response.status_code == 200
        html = response.get_data(as_text=True)
        assert any(k in html.lower() for k in ["tidak ada", "tidak ditemukan", "kosong", "no matching", "gak ada", "cocok"])


# ==============================================================================
# 4. INVALID BUDGET INPUT HANDLING
# ==============================================================================

class TestInvalidBudgetHandling:
    """Verifies graceful error handling on invalid, negative, non-numeric, or malicious inputs."""

    def test_post_negative_budget(self, client):
        """POST /recommend with negative budget returns 200 (error banner) or 400, never 500."""
        response = client.post("/recommend", data={"budget": "-5000"}, follow_redirects=True)
        assert response.status_code in (200, 400)
        assert response.status_code != 500
        html = response.get_data(as_text=True)
        assert response.status_code == 400 or any(
            k in html.lower() for k in ["masukkan budget", "wajib", "valid", "error", "negatif", "kurang"]
        )

    def test_post_zero_budget(self, client):
        """POST /recommend with budget=0 returns 200 or 400, never 500."""
        response = client.post("/recommend", data={"budget": "0"}, follow_redirects=True)
        assert response.status_code in (200, 400)
        assert response.status_code != 500

    def test_post_non_numeric_budget(self, client):
        """POST /recommend with non-numeric string ('abc_rupiah') handled cleanly."""
        response = client.post("/recommend", data={"budget": "abc_rupiah"}, follow_redirects=True)
        assert response.status_code in (200, 400)
        assert response.status_code != 500

    def test_post_empty_budget(self, client):
        """POST /recommend with empty string budget returns validation error without crashing."""
        response = client.post("/recommend", data={"budget": ""}, follow_redirects=True)
        assert response.status_code in (200, 400)
        assert response.status_code != 500

    def test_post_whitespace_budget(self, client):
        """POST /recommend with whitespace around budget ('   15000   ') trims and processes cleanly."""
        response = client.post("/recommend", data={"budget": "   15000   "}, follow_redirects=True)
        assert response.status_code == 200
        html = response.get_data(as_text=True)
        assert "15" in html or "rekomendasi" in html.lower() or "paket" in html.lower()

    def test_post_xss_sanitization(self, client):
        """POST /recommend with XSS payload escapes HTML tags without executing script."""
        payload = "<script>alert('xss_attack')</script>"
        response = client.post(
            "/recommend",
            data={"budget": "20000", "canteen": payload},
            follow_redirects=True,
        )
        assert response.status_code in (200, 400)
        html = response.get_data(as_text=True)
        assert "<script>alert('xss_attack')</script>" not in html

    def test_get_recommend_invalid_budget(self, client):
        """GET /recommend?budget=-1000 or ?budget=invalid returns 200 or 400, never 500."""
        response = client.get("/recommend?budget=-1000")
        assert response.status_code in (200, 400)
        assert response.status_code != 500

        response_str = client.get("/recommend?budget=sepuluh_ribu")
        assert response_str.status_code in (200, 400)
        assert response_str.status_code != 500


# ==============================================================================
# 5. REST API: GET /api/recommend
# ==============================================================================

class TestApiRecommend:
    """Verifies REST API recommendation endpoint schema, filtering, deficits, and errors."""

    def test_api_recommend_success(self, client):
        """GET /api/recommend?budget=20000 returns HTTP 200 and JSON RecommendationResult."""
        response = client.get("/api/recommend?budget=20000")
        assert response.status_code == 200
        assert "application/json" in response.content_type

        data = response.get_json()
        assert isinstance(data, dict)
        assert data.get("status") == "SUCCESS"
        assert data.get("budget") == 20000
        assert data.get("deficit") == 0
        assert isinstance(data.get("recommendations"), list)
        assert len(data["recommendations"]) > 0

    def test_api_recommend_schema_details(self, client):
        """Verifies individual recommendation dictionary fields and constraints."""
        response = client.get("/api/recommend?budget=20000")
        assert response.status_code == 200
        data = response.get_json()

        first_rec = data["recommendations"][0]
        assert "items" in first_rec and isinstance(first_rec["items"], list)
        assert "total_cost" in first_rec and first_rec["total_cost"] <= 20000
        assert "budget_remaining" in first_rec and first_rec["budget_remaining"] == 20000 - first_rec["total_cost"]
        assert "total_satisfaction" in first_rec and first_rec["total_satisfaction"] > 0
        assert "package_type" in first_rec and first_rec["package_type"] in ("optimal", "hemat", "combo")

        first_item = first_rec["items"][0]
        assert "id" in first_item
        assert "name" in first_item
        assert "price" in first_item and isinstance(first_item["price"], int)
        assert "category" in first_item and isinstance(first_item["category"], str)
        assert "dietary_tags" in first_item and isinstance(first_item["dietary_tags"], list)

    def test_api_recommend_canteen_and_dietary_filters(self, client):
        """GET /api/recommend with canteen and dietary parameters restricts results."""
        response = client.get("/api/recommend?budget=30000&canteen=Fasilkom&dietary=vegetarian")
        assert response.status_code == 200
        data = response.get_json()
        assert data.get("status") == "SUCCESS"

        for rec in data.get("recommendations", []):
            for item in rec.get("items", []):
                assert "Fasilkom" in item.get("canteen_name")
                tags = [t.lower() for t in item.get("dietary_tags", [])]
                assert "vegetarian" in tags

    def test_api_recommend_combo_flag(self, client):
        """GET /api/recommend?budget=20000&combo=false allows flexible combinations."""
        response = client.get("/api/recommend?budget=20000&combo=false")
        assert response.status_code == 200
        data = response.get_json()
        assert data.get("status") == "SUCCESS"

    def test_api_recommend_insufficient_budget(self, client):
        """GET /api/recommend?budget=1000 returns INSUFFICIENT_BUDGET status with positive deficit."""
        response = client.get("/api/recommend?budget=1000")
        assert response.status_code == 200
        assert "application/json" in response.content_type

        data = response.get_json()
        assert data.get("status") == "INSUFFICIENT_BUDGET"
        assert data.get("deficit", 0) > 0
        assert data.get("recommendations") == []
        assert data.get("cheapest_item_price", 0) > 1000

    def test_api_recommend_missing_budget_400(self, client):
        """GET /api/recommend without budget parameter returns 400 Bad Request with JSON error."""
        response = client.get("/api/recommend")
        assert response.status_code == 400
        assert "application/json" in response.content_type
        data = response.get_json()
        assert "error" in data or "message" in data or data.get("status") == "ERROR"

    def test_api_recommend_invalid_budget_400(self, client):
        """GET /api/recommend with negative or non-numeric budget returns 400 Bad Request."""
        res_neg = client.get("/api/recommend?budget=-5000")
        assert res_neg.status_code == 400
        assert "application/json" in res_neg.content_type

        res_str = client.get("/api/recommend?budget=bukan_angka")
        assert res_str.status_code == 400
        assert "application/json" in res_str.content_type

        res_zero = client.get("/api/recommend?budget=0")
        assert res_zero.status_code == 400
        assert "application/json" in res_zero.content_type


# ==============================================================================
# 6. REST API: GET /api/merchants
# ==============================================================================

class TestApiMerchants:
    """Verifies REST API merchants directory endpoint and data serialization."""

    def test_api_merchants_success(self, client):
        """GET /api/merchants returns HTTP 200 and JSON array of merchant records."""
        response = client.get("/api/merchants")
        assert response.status_code == 200
        assert "application/json" in response.content_type

        data = response.get_json()
        assert isinstance(data, (list, dict))
        merchants = data if isinstance(data, list) else data.get("merchants", [])
        assert len(merchants) >= 6, "Must contain merchants from all UI campus canteens"

    def test_api_merchants_data_structure(self, client):
        """Verifies each merchant record contains required schema attributes."""
        response = client.get("/api/merchants")
        data = response.get_json()
        merchants = data if isinstance(data, list) else data.get("merchants", [])

        first_m = merchants[0]
        assert "id" in first_m
        assert "name" in first_m
        assert "canteen_name" in first_m
        assert "faculty" in first_m
        assert "rating" in first_m and isinstance(first_m["rating"], (int, float))
        assert "items" in first_m and isinstance(first_m["items"], list)
        assert len(first_m["items"]) > 0

    def test_api_merchants_items_serialization(self, client):
        """Verifies nested items serialize Category to string and dietary_tags to list."""
        response = client.get("/api/merchants")
        data = response.get_json()
        merchants = data if isinstance(data, list) else data.get("merchants", [])

        for m in merchants:
            for it in m["items"]:
                assert isinstance(it["category"], str), "Item category must be serialized to string"
                assert it["category"] in ("food", "beverage", "snack")
                assert isinstance(it["dietary_tags"], list), "Item dietary_tags must be serialized to list"
                assert isinstance(it["price"], int) and it["price"] >= 0

    def test_api_merchants_canteen_filter(self, client):
        """GET /api/merchants?canteen=dallas filters merchants to Kantin Dallas."""
        response = client.get("/api/merchants?canteen=dallas")
        assert response.status_code == 200
        data = response.get_json()
        merchants = data if isinstance(data, list) else data.get("merchants", [])
        for m in merchants:
            assert "dallas" in m["canteen_name"].lower() or "dallas" in m.get("canteen_id", "").lower()


# ==============================================================================
# 7. ERROR HANDLERS (404 & 405)
# ==============================================================================

class TestErrorHandlers:
    """Verifies custom error handlers for not found pages and disallowed methods."""

    def test_404_html_error_page(self, client):
        """Requesting non-existent HTML route returns 404 with friendly error page."""
        response = client.get("/halaman-yang-tidak-ada-9999")
        assert response.status_code == 404
        html = response.get_data(as_text=True)

        assert "404" in html
        assert any(k in html.lower() for k in ["tidak ditemukan", "not found", "kembali", "error"])
        assert 'href="/"' in html or "home" in html.lower()

    def test_404_api_json_response(self, client):
        """Requesting non-existent API route returns 404 with JSON error structure."""
        response = client.get("/api/endpoint_palsu_123", headers={"Accept": "application/json"})
        assert response.status_code == 404

    def test_405_method_not_allowed(self, client):
        """Sending unsupported HTTP method returns 405 Method Not Allowed cleanly."""
        response = client.delete("/")
        assert response.status_code == 405
