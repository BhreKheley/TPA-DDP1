"""Modul Rute Web & REST API Controller (Flask Web Application)
Smart Meal Finder - DDP1 Gasal 2026/2027 Kelompok 5

Modul ini menghubungkan antarmuka peramban (browser) dan klien API dengan modul logika
inti (core/budget.py). Bertanggung jawab atas:
1. Menerima permintaan HTTP (GET dan POST) dari formulir pencarian mahasiswa.
2. Memvalidasi input nominal Rupiah (menolak nilai negatif, teks non-angka, input kosong).
3. Memanggil fungsi `recommend_meals` untuk mengeksekusi algoritma knapsack DP.
4. Merender halaman web Jinja2 responsif atau menyajikan data JSON untuk REST API.

Kontributor:
- Johannes Praba Aji (NPM: 2606748465) - Pengembang Utama Web App & CI/CD
- Bhre Nabil Faeyza (NPM: 2606887563) - Reviewer PR #3 & Integrasi Logika
"""

from datetime import datetime, timedelta, timezone
import re
from typing import Any, Dict, List, Optional, Set
from flask import (
    Blueprint,
    abort,
    current_app,
    jsonify,
    render_template,
    request,
)

from core.budget import recommend_meals
from core.search import affordable_merchants, best_combo, cheapest_gap, is_open, is_stale

# Inisialisasi Blueprint Flask untuk modularitas rute aplikasi
main_bp = Blueprint("main", __name__)

# WIB tetap UTC+7 (Indonesia tanpa DST); tidak memakai zoneinfo agar jalan di Windows tanpa paket tzdata.
WIB = timezone(timedelta(hours=7))
MAX_BUDGET = 10_000_000
_BUDGET_FORMAT = re.compile(r"^(\d{1,3}([.,\s]\d{3})+|\d+)$")


class BudgetError(ValueError):
    """Nominal anggaran tidak valid. `title` dan `message` siap tampil ke pengguna."""

    def __init__(self, title: str, message: str) -> None:
        super().__init__(message)
        self.title = title
        self.message = message


def parse_budget(raw: Any) -> int:
    """Mengubah input nominal ('15000', '15.000', 'Rp 15.000') menjadi bilangan bulat positif."""
    text = re.sub(r"^rp\.?\s*", "", str(raw or "").strip(), flags=re.IGNORECASE)
    if not text:
        raise BudgetError("Input Budget Wajib Diisi", "Ketik nominal uang makanmu, misalnya 15.000.")
    if text.startswith("-") and text[1:].isdigit():
        raise BudgetError("Budget Negatif", "Nominal tidak boleh negatif. Ketik angka positif, misalnya 15.000.")
    if not _BUDGET_FORMAT.match(text):
        raise BudgetError(
            "Format Budget Tidak Valid",
            "Gunakan angka bulat saja, misalnya 15000 atau 15.000. Hapus huruf dan simbol lain.",
        )
    value = int(re.sub(r"[.,\s]", "", text))
    if value == 0:
        raise BudgetError("Budget Harus Lebih dari Nol", "Nominal 0 tidak bisa dicari. Isi minimal harga satu menu, misalnya 5.000.")
    if value > MAX_BUDGET:
        raise BudgetError("Budget Terlalu Besar", "Nominal maksimal Rp 10.000.000. Ketik uang makan harianmu.")
    return value


@main_bp.app_template_global("freshness")
def freshness(updated_at: Optional[str]) -> Dict[str, Any]:
    """Label kesegaran harga untuk template: tanggal pembaruan, atau penanda usang setelah 1 bulan."""
    stale = is_stale(updated_at, today=datetime.now(WIB).date())
    if stale is None:
        return {"text": "Tanggal harga belum tercatat", "stale": False}
    return {"text": f"Harga per {updated_at}" + (", mungkin sudah berubah" if stale else ""), "stale": stale}


def _extract_canteen_list(merchants) -> List[str]:
    """Mengekstrak daftar nama kantin UI unik dan terurut dari dataset merchant."""
    canteens = sorted(list({m.canteen_name for m in merchants}))
    return canteens


def _parse_dietary_params(form_or_args) -> Optional[List[str]]:
    """Mengekstrak preferensi diet (halal, pedas, vegetarian) dari query string atau form data."""
    raw_list = form_or_args.getlist("dietary")
    tags: Set[str] = set()

    for item in raw_list:
        if "," in item:
            for part in item.split(","):
                if part.strip():
                    tags.add(part.strip().lower())
        elif item.strip():
            tags.add(item.strip().lower())

    single_val = form_or_args.get("dietary")
    if single_val and not tags:
        for part in single_val.split(","):
            if part.strip():
                tags.add(part.strip().lower())

    return list(tags) if tags else None


@main_bp.route("/", methods=["GET"])
def index():
    """Halaman Beranda (Home Page): Menampilkan formulir input anggaran dan pilihan cepat."""
    merchants = current_app.get_merchants()
    canteens = _extract_canteen_list(merchants)
    presets = [10000, 15000, 20000, 25000]
    dietary_options = [
        {"id": "halal", "label": "Halal"},
        {"id": "vegetarian", "label": "Vegetarian"},
        {"id": "pedas", "label": "Pedas"},
        {"id": "non-spicy", "label": "Tidak Pedas"},
    ]
    return render_template(
        "index.html",
        canteens=canteens,
        presets=presets,
        dietary_options=dietary_options,
    )


@main_bp.route("/recommend", methods=["GET", "POST"])
def recommend():
    """Memproses input nominal anggaran dan menyajikan hasil rekomendasi menu atau analisis defisit."""
    merchants = current_app.get_merchants()
    canteens = _extract_canteen_list(merchants)
    presets = [10000, 15000, 20000, 25000]
    dietary_options = [
        {"id": "halal", "label": "Halal"},
        {"id": "vegetarian", "label": "Vegetarian"},
        {"id": "pedas", "label": "Pedas"},
        {"id": "non-spicy", "label": "Tidak Pedas"},
    ]

    source = request.form if request.method == "POST" else request.args

    # Jika pengguna mengakses URL /recommend via GET tanpa parameter, kembalikan ke beranda
    raw_budget = source.get("budget")
    if request.method == "GET" and raw_budget is None:
        return render_template(
            "index.html",
            canteens=canteens,
            presets=presets,
            dietary_options=dietary_options,
        )

    # 1. Validasi Input Anggaran (Budget)
    try:
        budget_val = parse_budget(raw_budget)
    except BudgetError as err:
        return render_template("error.html", code=400, title=err.title, message=err.message), 400

    # 2. Ekstraksi Filter Kantin & Tag Diet
    canteen = source.get("canteen", "").strip() or None
    dietary_tags = _parse_dietary_params(source)

    # 3. Pengaturan Opsi Paket Kombo (1 Makanan + 1 Minuman)
    raw_combo = source.get("require_combo")
    if raw_combo is None:
        raw_combo = source.get("combo")

    if raw_combo is not None:
        require_combo = str(raw_combo).lower() not in ("false", "0", "off", "no")
    else:
        require_combo = True

    # 4. Panggil Mesin Algoritma Knapsack DP
    result = recommend_meals(
        merchants_or_items=merchants,
        budget=budget_val,
        canteen_filter=canteen,
        dietary_preferences=dietary_tags,
        require_combo=require_combo,
    )

    groups = affordable_merchants(merchants, budget_val, canteen=canteen, tags=set(dietary_tags) if dietary_tags else None)
    return render_template(
        "results.html",
        groups=groups,
        gap=None if groups else cheapest_gap(merchants, budget_val),
        result=result,
        budget=budget_val,
        canteen=canteen or "Semua Kantin UI",
        dietary=dietary_tags or [],
        require_combo=require_combo,
        deficit=result.deficit,
        cheapest_item_price=result.cheapest_item_price,
        fallback_recommendations=getattr(result, "fallback_recommendations", []),
        canteens=canteens,
    )


@main_bp.route("/merchants", methods=["GET"])
def merchants_catalog():
    """Katalog Stan Kantin: Menampilkan direktori seluruh stan makanan di kantin kampus UI."""
    merchants = current_app.get_merchants()
    canteens = _extract_canteen_list(merchants)
    selected_canteen = request.args.get("canteen", "").strip()

    if selected_canteen:
        filtered_merchants = [
            m for m in merchants
            if selected_canteen.lower() in m.canteen_name.lower()
        ]
    else:
        filtered_merchants = merchants

    return render_template(
        "merchants.html",
        merchants=filtered_merchants,
        all_merchants=merchants,
        canteens=canteens,
        selected_canteen=selected_canteen,
    )


@main_bp.route("/merchant/<merchant_id>", methods=["GET"])
def merchant_detail(merchant_id: str):
    """Detail merchant: menu yang muat di anggaran, kombinasi terbaik, jam buka, dan kesegaran harga."""
    merchant = next((m for m in current_app.get_merchants() if m.id == merchant_id), None)
    if merchant is None:
        abort(404)
    try:
        budget = parse_budget(request.args.get("budget")) if request.args.get("budget") else None
    except BudgetError:
        budget = None
    menu = sorted((it for it in merchant.items if it.is_available), key=lambda it: (it.price, it.name))
    combo = best_combo(menu, budget) if budget else ()
    return render_template(
        "merchant_detail.html",
        merchant=merchant,
        budget=budget,
        fitting=[it for it in menu if budget is None or it.price <= budget],
        combo=combo,
        combo_total=sum(it.price for it in combo),
        open_now=is_open(merchant.open_hours, datetime.now(WIB)),
        cheapest=menu[0].price if menu else None,
    )


@main_bp.route("/api/recommend", methods=["GET"])
def api_recommend():
    """Endpoint REST API: Mengembalikan rekomendasi menu dalam format JSON."""
    raw_budget = request.args.get("budget")
    if raw_budget is None or str(raw_budget).strip() == "":
        return jsonify({"status": "ERROR", "message": "Parameter 'budget' wajib disertakan."}), 400

    try:
        budget_val = parse_budget(raw_budget)
    except BudgetError as err:
        return jsonify({"status": "ERROR", "message": f"Parameter 'budget' tidak valid. {err.message}"}), 400

    canteen = request.args.get("canteen", "").strip() or None
    dietary_tags = _parse_dietary_params(request.args)
    raw_combo = request.args.get("require_combo")
    if raw_combo is None:
        raw_combo = request.args.get("combo")
    require_combo = (
        str(raw_combo).lower() not in ("false", "0", "off", "no")
        if raw_combo is not None
        else True
    )

    merchants = current_app.get_merchants()
    result = recommend_meals(
        merchants_or_items=merchants,
        budget=budget_val,
        canteen_filter=canteen,
        dietary_preferences=dietary_tags,
        require_combo=require_combo,
    )

    return jsonify(result.to_dict()), 200


@main_bp.route("/api/merchants", methods=["GET"])
def api_merchants():
    """Endpoint REST API: Mengembalikan seluruh data merchant dan daftar menu dalam format JSON."""
    merchants = current_app.get_merchants()
    canteen_filter = request.args.get("canteen", "").strip().lower()

    if canteen_filter:
        merchants = [
            m for m in merchants
            if canteen_filter in m.canteen_name.lower()
        ]

    serialized = []
    for m in merchants:
        serialized.append({
            "id": m.id,
            "name": m.name,
            "canteen_id": m.canteen_id,
            "canteen_name": m.canteen_name,
            "faculty": m.faculty,
            "rating": m.rating,
            "description": m.description,
            "items": [
                {
                    "id": it.id,
                    "name": it.name,
                    "category": it.category.value if hasattr(it.category, "value") else str(it.category),
                    "price": it.price,
                    "satisfaction_score": it.satisfaction_score,
                    "dietary_tags": sorted(list(it.dietary_tags)),
                    "merchant_id": it.merchant_id,
                    "merchant_name": it.merchant_name,
                    "canteen_name": it.canteen_name,
                    "faculty": it.faculty,
                    "calories": it.calories,
                    "description": it.description,
                    "is_available": it.is_available,
                }
                for it in m.items
            ],
        })

    return jsonify({"merchants": serialized, "count": len(serialized)}), 200
