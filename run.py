"""Application server entrypoint for Smart Meal Finder.

Universitas Indonesia DDP1 - Kelompok 5
Johannes Praba Aji (NPM 2606748465)
"""

import os
from app import create_app

app = create_app()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    debug = os.environ.get("FLASK_DEBUG", "True").lower() in ("true", "1")
    app.run(host="0.0.0.0", port=port, debug=debug)
