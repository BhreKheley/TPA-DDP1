import pytest

from app.routes import parse_nominal


@pytest.mark.parametrize("raw, value", [("15000", 15000), ("15.000", 15000), (" 10 000 ", 10000)])
def test_parse_nominal_ok(raw, value):
    assert parse_nominal(raw) == value


@pytest.mark.parametrize("raw", [None, "", "abc", "12a", "-5000", "0", "2000000", "²"])
def test_parse_nominal_rejects(raw):
    with pytest.raises(ValueError):
        parse_nominal(raw)


def test_home_has_form_and_quick_links(client):
    html = client.get("/").get_data(as_text=True)
    assert 'name="nominal"' in html and "nominal=10000" in html and "belum diverifikasi" in html


def test_results_grouped_by_canteen(client):
    html = client.get("/cari?nominal=15000").get_data(as_text=True)
    assert html.index("Kantin A") < html.index("Kantin B")
    assert "Bakso" in html and "mulai" in html


def test_results_show_stale_and_open_labels(client):
    html = client.get("/cari?nominal=15000").get_data(as_text=True)
    assert "lebih dari sebulan" in html  # Bakso dicek 2026-09-01
    assert "Tutup" in html  # m3 buka 22:00 sampai 02:00, tes pukul 12:00


def test_canteen_filter_link(client):
    html = client.get("/cari?nominal=15000&kantin=Kantin+A").get_data(as_text=True)
    assert "Warung Murah" in html and "Bakso" not in html


def test_shortfall_shows_cheapest_and_gap(client):
    response = client.get("/cari?nominal=1000")
    html = response.get_data(as_text=True)
    assert response.status_code == 200
    assert "Rp 2.000" in html and "kurang" in html and "Rp 1.000" in html


@pytest.mark.parametrize("value", ["", "abc", "-1", "0"])
def test_bad_nominal_is_rejected_with_message(client, value):
    response = client.get(f"/cari?nominal={value}")
    assert response.status_code == 400
    assert 'role="alert"' in response.get_data(as_text=True)


def test_detail_lists_only_fitting_menu_and_combo(client):
    html = client.get("/merchant/m1?nominal=15000").get_data(as_text=True)
    assert "Kombinasi untuk Rp 15.000" in html and "Rp 9.000" in html
    assert "Ayam" in html  # 9000 muat di anggaran 15000
    small = client.get("/merchant/m1?nominal=3000").get_data(as_text=True)
    assert "Ayam" not in small and "Nasi" not in small


def test_detail_unknown_merchant_and_missing_nominal(client):
    assert client.get("/merchant/zzz?nominal=5000").status_code == 404
    assert client.get("/merchant/m1").status_code == 302


def test_detail_without_fitting_menu_is_not_empty_page(client):
    html = client.get("/merchant/m2?nominal=5000").get_data(as_text=True)
    assert "Tidak ada menu sampai Rp 5.000" in html


def test_security_headers_and_no_inline_script(client):
    response = client.get("/")
    assert "default-src 'self'" in response.headers["Content-Security-Policy"]
    assert "<script" not in response.get_data(as_text=True)


def test_404_page(client):
    assert client.get("/tidak-ada").status_code == 404
