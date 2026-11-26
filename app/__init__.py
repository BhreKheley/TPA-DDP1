"""Lapisan web Smart Meal Finder: application factory Flask."""

from pathlib import Path
from typing import Any, Dict, Optional

from flask import Flask, render_template

from core.loader import load_merchants

DEFAULT_DATA = Path(__file__).resolve().parent.parent / "data" / "merchants.json"


def format_rupiah(value: int) -> str:
    return "Rp " + f"{int(value):,}".replace(",", ".")


def create_app(test_config: Optional[Dict[str, Any]] = None) -> Flask:
    app = Flask(__name__)
    app.config["DATA_PATH"] = DEFAULT_DATA
    if test_config:
        app.config.update(test_config)

    # Dimuat sekali saat start: data rusak langsung gagal dengan pesan jelas, bukan saat ada pengguna.
    app.config["MERCHANTS"] = load_merchants(app.config["DATA_PATH"])
    app.jinja_env.filters["rupiah"] = format_rupiah

    from app.routes import bp
    app.register_blueprint(bp)

    @app.after_request
    def security_headers(response):
        response.headers["Content-Security-Policy"] = "default-src 'self'; frame-ancestors 'none'"
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["Referrer-Policy"] = "same-origin"
        return response

    @app.errorhandler(404)
    def not_found(_):
        return render_template("error.html", title="Halaman tidak ditemukan",
                               message="Alamat yang kamu buka tidak ada. Kembali ke beranda untuk mencari lagi."), 404

    @app.errorhandler(500)
    def server_error(_):
        return render_template("error.html", title="Ada gangguan di server",
                               message="Coba muat ulang beberapa saat lagi."), 500

    return app
