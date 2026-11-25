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

from typing import Any, Dict, List, Optional, Set
from flask import (
    Blueprint,
    current_app,
    jsonify,
    render_template,
    request,
)

from core.budget import recommend_meals

# Inisialisasi Blueprint Flask untuk modularitas rute aplikasi
main_bp = Blueprint("main", __name__)

DIETARY_OPTIONS: List[Dict[str, str]] = [
    {"id": "halal", "label": "Halal"},
    {"id": "vegetarian", "label": "Vegetarian"},
    {"id": "spicy", "label": "Pedas"},
    {"id": "non-spicy", "label": "Tidak Pedas"},
]

CANTEEN_NOTES: Dict[str, str] = {
    "dallas": "Di Bawah Lindungan Allah SWT. Posisinya tepat di bawah musala FMIPA UI.",
    "kansas": "Kantin Sastra dengan atap kerucut khasnya di lingkungan FIB UI.",
    "takor": "Taman Korea di FISIP UI. Area ini dulunya akrab disapa Balsem (Balik Semak).",
    "texas": "Kantin Teknik (Kantek) di FT UI, bersebelahan dengan Jembatan Teksas.",
    "fasilkom": "Balik Gedung Bundar (Balgebun), tempat makan harian anak Fasilkom UI.",
    "pusgiwa": "Kantin Pusat Kegiatan Mahasiswa UI, titik kumpul anak UKM dan kepanitiaan.",
}


def _extract_canteen_list(merchants) -> List[str]:
    """Mengekstrak daftar nama kantin UI unik dan terurut dari dataset merchant."""
    canteens = sorted(list({m.canteen_name for m in merchants}))
    return canteens


def _build_canteen_summaries(merchants) -> List[Dict[str, Any]]:
    """Menyusun ringkasan data terverifikasi untuk setiap kantin dari dataset aktif."""
    grouped: Dict[str, Dict[str, Any]] = {}
    for m in merchants:
        entry = grouped.setdefault(
            m.canteen_name,
            {
                "canteen_id": m.canteen_id,
                "canteen_name": m.canteen_name,
                "faculty": m.faculty,
                "lore": CANTEEN_NOTES.get(m.canteen_id, f"Kawasan kantin {m.faculty}."),
                "merchant_count": 0,
                "available_count": 0,
                "min_price": None,
            },
        )
        entry["merchant_count"] += 1
        for it in m.items:
            if it.is_available:
                entry["available_count"] += 1
                if entry["min_price"] is None or it.price < entry["min_price"]:
                    entry["min_price"] = it.price
    return [grouped[name] for name in sorted(grouped.keys())]


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


def _resolve_dining_mode(source) -> tuple[bool, bool, str]:
    """Mengonversi parameter `mode` atau flag `require_combo`/`food_only` secara konsisten."""
    raw_mode = source.get("mode", "").strip().lower()
    if raw_mode == "tumbler":
        return False, True, "tumbler"
    if raw_mode == "flexible":
        return False, False, "flexible"
    if raw_mode == "combo":
        return True, False, "combo"

    raw_combo = source.get("require_combo")
    if raw_combo is None:
        raw_combo = source.get("combo")

    food_only = str(source.get("food_only", "off")).lower() in ("true", "1", "on", "yes")
    if food_only:
        return False, True, "tumbler"

    if raw_combo is not None:
        require_combo = str(raw_combo).lower() not in ("false", "0", "off", "no")
    else:
        require_combo = True

    active_mode = "combo" if require_combo else "flexible"
    return require_combo, False, active_mode


def _compute_dataset_metrics(merchants) -> Dict[str, int]:
    """Menghitung metrik terverifikasi langsung dari dataset aktif (tanpa angka fiktif)."""
    canteens = {m.canteen_name for m in merchants}
    available_items = sum(1 for m in merchants for it in m.items if it.is_available)
    return {
        "canteen_count": len(canteens),
        "merchant_count": len(merchants),
        "available_item_count": available_items,
    }


@main_bp.route("/", methods=["GET"])
def index():
    """Halaman Beranda (Home Page): Menampilkan formulir pencarian anggaran dan direktori kantin."""
    merchants = current_app.get_merchants()
    canteens = _extract_canteen_list(merchants)
    canteen_summaries = _build_canteen_summaries(merchants)
    metrics = _compute_dataset_metrics(merchants)
    presets = [10000, 15000, 20000, 25000]
    return render_template(
        "index.html",
        canteens=canteens,
        canteen_summaries=canteen_summaries,
        metrics=metrics,
        presets=presets,
        dietary_options=DIETARY_OPTIONS,
    )


@main_bp.route("/recommend", methods=["GET", "POST"])
def recommend():
    """Memproses input nominal anggaran dan menyajikan hasil rekomendasi menu atau analisis defisit."""
    merchants = current_app.get_merchants()
    canteens = _extract_canteen_list(merchants)
    canteen_summaries = _build_canteen_summaries(merchants)
    metrics = _compute_dataset_metrics(merchants)
    presets = [10000, 15000, 20000, 25000]

    source = request.form if request.method == "POST" else request.args

    # Jika pengguna mengakses URL /recommend via GET tanpa parameter, kembalikan ke beranda
    raw_budget = source.get("budget")
    if request.method == "GET" and raw_budget is None:
        return render_template(
            "index.html",
            canteens=canteens,
            canteen_summaries=canteen_summaries,
            metrics=metrics,
            presets=presets,
            dietary_options=DIETARY_OPTIONS,
        )

    # 1. Validasi Input Anggaran (Budget)
    if raw_budget is None or str(raw_budget).strip() == "":
        return render_template(
            "error.html",
            code=400,
            title="Nominal Budget Belum Diisi",
            message="Masukkan dulu nominal uang makanmu (misalnya 15000) untuk mulai mencari paket.",
        ), 400

    clean_budget_str = str(raw_budget).strip()
    try:
        budget_val = int(clean_budget_str)
    except ValueError:
        return render_template(
            "error.html",
            code=400,
            title="Format Angka Tidak Valid",
            message="Tulis nominal budget pakai angka bulat saja ya (contoh: 15000, tanpa titik atau huruf).",
        ), 400

    if budget_val < 0:
        return render_template(
            "error.html",
            code=400,
            title="Budget Tidak Boleh Negatif",
            message="Nominal uang makan minimal Rp 0.",
        ), 400

    # 2. Ekstraksi Filter Kantin, Tag Diet, dan Mode Makan
    canteen = source.get("canteen", "").strip() or None
    dietary_tags = _parse_dietary_params(source)
    require_combo, food_only, active_mode = _resolve_dining_mode(source)

    # 3. Panggil Mesin Algoritma Knapsack DP
    result = recommend_meals(
        merchants_or_items=merchants,
        budget=budget_val,
        canteen_filter=canteen,
        dietary_preferences=dietary_tags,
        require_combo=require_combo,
        food_only=food_only,
    )

    return render_template(
        "results.html",
        result=result,
        budget=budget_val,
        canteen=canteen or "Semua Kantin UI",
        selected_canteen_raw=canteen or "",
        dietary=dietary_tags or [],
        dietary_options=DIETARY_OPTIONS,
        require_combo=require_combo,
        food_only=food_only,
        active_mode=active_mode,
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
        q = selected_canteen.lower()
        filtered_merchants = [
            m for m in merchants
            if q in m.canteen_name.lower() or q in m.canteen_id.lower() or q in m.faculty.lower()
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


@main_bp.route("/api/recommend", methods=["GET"])
def api_recommend():
    """Endpoint REST API: Mengembalikan rekomendasi menu dalam format JSON."""
    raw_budget = request.args.get("budget")
    if raw_budget is None or str(raw_budget).strip() == "":
        return jsonify({"status": "ERROR", "message": "Parameter 'budget' wajib disertakan."}), 400

    try:
        budget_val = int(str(raw_budget).strip())
    except ValueError:
        return jsonify({"status": "ERROR", "message": "Parameter 'budget' harus berupa bilangan bulat valid."}), 400

    if budget_val <= 0:
        return jsonify({"status": "ERROR", "message": "Parameter 'budget' harus lebih besar dari 0."}), 400

    canteen = request.args.get("canteen", "").strip() or None
    dietary_tags = _parse_dietary_params(request.args)
    require_combo, food_only_api, _ = _resolve_dining_mode(request.args)

    merchants = current_app.get_merchants()
    result = recommend_meals(
        merchants_or_items=merchants,
        budget=budget_val,
        canteen_filter=canteen,
        dietary_preferences=dietary_tags,
        require_combo=require_combo,
        food_only=food_only_api,
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
            if canteen_filter in m.canteen_name.lower() or canteen_filter in m.canteen_id.lower()
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
