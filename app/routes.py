"""Rute web: validasi input, panggil core, render templat. Tanpa logika bisnis."""

from datetime import datetime
from typing import Optional

from flask import Blueprint, abort, current_app, redirect, render_template, request, url_for

from core import budget
from core.models import Category

bp = Blueprint("main", __name__)

QUICK_AMOUNTS = (10000, 15000, 20000)
MAX_NOMINAL = 1_000_000


def parse_nominal(raw: Optional[str]) -> int:
    """Ubah teks nominal menjadi rupiah bulat. Pesan galat menyebut cara memperbaiki."""
    text = (raw or "").replace(".", "").replace(" ", "")
    if not text:
        raise ValueError("Ketik nominal uang makanmu, misalnya 15000.")
    if text.startswith("-"):
        raise ValueError("Nominal tidak boleh negatif. Ketik angka lebih dari 0.")
    if not (text.isascii() and text.isdigit()):
        raise ValueError("Nominal hanya boleh berisi angka, misalnya 15000 atau 15.000.")
    value = int(text)
    if value == 0:
        raise ValueError("Nominal harus lebih dari 0. Ketik angka seperti 10000.")
    if value > MAX_NOMINAL:
        raise ValueError(f"Nominal terlalu besar. Ketik angka sampai {MAX_NOMINAL:,}.".replace(",", "."))
    return value


def _merchants():
    return current_app.config["MERCHANTS"]


def _now() -> datetime:
    return current_app.config.get("NOW") or budget.now_wib()


def _status(merchant):
    """Label status untuk satu merchant: tanggal, usang atau tidak, buka atau tutup."""
    now = _now()
    return {
        "stale": budget.is_stale(merchant, now.date()),
        "open": budget.is_open(merchant, now.timetz().replace(tzinfo=None)),
    }


@bp.get("/")
def index():
    return render_template("index.html", quick=QUICK_AMOUNTS, unverified=_any_unverified())


def _any_unverified() -> bool:
    return any(not m.verified for m in _merchants())


@bp.get("/cari")
def search():
    raw = request.args.get("nominal", "")
    try:
        nominal = parse_nominal(raw)
    except ValueError as err:
        return render_template("index.html", quick=QUICK_AMOUNTS, error=str(err), value=raw,
                               unverified=_any_unverified()), 400

    canteen = request.args.get("kantin") or None
    all_canteens = sorted({m.canteen for m in _merchants()})
    groups = budget.group_by_canteen(_merchants(), nominal, canteen)
    shortfall = None
    if not budget.group_by_canteen(_merchants(), nominal):
        found = budget.cheapest(_merchants())
        if found:
            price, merchant = found
            shortfall = {"price": price, "merchant": merchant, "gap": price - nominal}
    cards = {
        name: [(m, budget.affordable_items(m, nominal), _status(m)) for m in members]
        for name, members in groups.items()
    }
    return render_template("hasil.html", nominal=nominal, cards=cards, canteens=all_canteens,
                           canteen=canteen, shortfall=shortfall, unverified=_any_unverified())


@bp.get("/merchant/<merchant_id>")
def merchant_detail(merchant_id: str):
    merchant = next((m for m in _merchants() if m.id == merchant_id), None)
    if merchant is None:
        abort(404)
    try:
        nominal = parse_nominal(request.args.get("nominal"))
    except ValueError:
        return redirect(url_for("main.index"))
    fitting = budget.affordable_items(merchant, nominal)
    by_category = {c.label: [i for i in fitting if i.category is c] for c in Category}
    by_category = {label: items for label, items in by_category.items() if items}
    combo = budget.best_combo(fitting, nominal)
    return render_template("merchant.html", merchant=merchant, nominal=nominal, by_category=by_category,
                           combo=combo, combo_total=sum(i.price for i in combo), status=_status(merchant))
