"""Flask application package and factory for Smart Meal Finder.

Universitas Indonesia DDP1 - Kelompok 5
Johannes Praba Aji (NPM 2606748465)
"""

import json
import os
from pathlib import Path
import tempfile
from typing import Any, Dict, List, Optional
from flask import Flask, jsonify, render_template, request

from core.loader import Merchant, load_merchants


def format_rupiah(value: Any) -> str:
    """Jinja filter formatting numbers into standard Indonesian Rupiah notation."""
    if value is None:
        return "Rp 0"
    try:
        val = int(value)
        formatted = f"{val:,}".replace(",", ".")
        return f"Rp {formatted}"
    except (ValueError, TypeError):
        return f"Rp {value}"


def create_app(test_config: Optional[Dict[str, Any]] = None) -> Flask:
    """Creates and configures the Flask application instance."""
    app = Flask(__name__, instance_relative_config=True)

    # Base configuration
    app.config.from_mapping(
        SECRET_KEY=os.environ.get("SECRET_KEY", "smart-meal-finder-ui-kelompok5-secret"),
        DATA_PATH=os.environ.get("DATA_PATH"),
        TESTING=False,
    )

    if test_config:
        app.config.update(test_config)

    # Register custom Jinja filters
    app.jinja_env.filters["format_rupiah"] = format_rupiah
    app.jinja_env.filters["rupiah"] = format_rupiah

    # Data Loader Helper bound to app context
    def get_merchants() -> List[Merchant]:
        """Loads merchants dataset according to application environment."""
        # 1. If explicit DATA_PATH is provided and file exists
        data_path = app.config.get("DATA_PATH")
        if data_path and Path(data_path).is_file():
            is_testing = bool(app.config.get("TESTING"))
            return load_merchants(data_path, strict=not is_testing)

        # 2. If running under pytest with TESTING=True without custom DATA_PATH
        if app.config.get("TESTING"):
            try:
                from tests.e2e.conftest import SAMPLE_MERCHANTS_DICT
                with tempfile.NamedTemporaryFile(
                    mode="w", suffix=".json", delete=False, encoding="utf-8"
                ) as tf:
                    json.dump(SAMPLE_MERCHANTS_DICT, tf)
                    temp_name = tf.name
                try:
                    return load_merchants(temp_name, strict=False)
                finally:
                    if os.path.exists(temp_name):
                        os.unlink(temp_name)
            except (ImportError, Exception):
                pass

        # 3. Default fallback to standard data/merchants.json
        default_path = Path(__file__).resolve().parent.parent / "data" / "merchants.json"
        if default_path.is_file():
            return load_merchants(default_path, strict=True)
        return []

    app.get_merchants = get_merchants

    # Register routes blueprint
    from app.routes import main_bp
    app.register_blueprint(main_bp)

    # Error handlers
    @app.errorhandler(400)
    def bad_request(error):
        msg = getattr(error, "description", "Permintaan tidak valid.")
        if request.path.startswith("/api/"):
            return jsonify({"status": "ERROR", "message": msg, "error": msg}), 400
        return render_template("error.html", code=400, title="Input Tidak Valid", message=msg), 400

    @app.errorhandler(404)
    def not_found(error):
        msg = "Halaman atau endpoint yang Anda cari tidak tersedia."
        if request.path.startswith("/api/"):
            return jsonify({"status": "ERROR", "error": msg, "message": msg}), 404
        return render_template("error.html", code=404, title="Halaman Tidak Ditemukan", message=msg), 404

    @app.errorhandler(500)
    def internal_error(error):
        msg = "Terjadi gangguan internal pada server. Silakan coba beberapa saat lagi."
        if request.path.startswith("/api/"):
            return jsonify({"status": "ERROR", "error": msg, "message": msg}), 500
        return render_template("error.html", code=500, title="Terjadi Kesalahan Server", message=msg), 500

    return app
