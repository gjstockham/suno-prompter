"""Flask application entry point for the Suno Prompter backend."""

import logging
import os
import sys
from pathlib import Path
from typing import Iterable

from dotenv import load_dotenv
from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))
DIST_DIR = BASE_DIR / "frontend" / "dist"


def load_environment(env_paths: Iterable[Path] | None = None) -> None:
    """
    Load environment variables from common .env locations.

    Order:
    1. ./backend/.env (if present)
    2. Project root .env
    3. ~/.suno-prompter/.env
    """
    candidates = list(env_paths or [])
    if not candidates:
        project_root = Path(__file__).resolve().parent.parent
        candidates = [
            project_root / "backend" / ".env",
            project_root / ".env",
            Path.home() / ".suno-prompter" / ".env",
        ]

    for env_path in candidates:
        if env_path.exists():
            logger.info("Loading environment from %s", env_path)
            load_dotenv(env_path)
            return

    logger.info("No .env file found in default locations; relying on process env.")


def create_app() -> Flask:
    """Create and configure the Flask application."""
    load_environment()

    # Reconfigure logger now that environment variables are loaded
    from backend.services.utils.logging import get_logger

    global logger  # noqa: PLW0603
    logger = get_logger(__name__)

    app = Flask(
        __name__,
        static_folder=str(DIST_DIR),
        static_url_path="/",
    )
    CORS(app, resources={r"/api/*": {"origins": "*"}})

    @app.route("/api/health", methods=["GET"])
    def health():
        """Simple health check endpoint."""
        return jsonify({"status": "ok"}), 200

    from backend.api.prompter import api_bp

    app.register_blueprint(api_bp)

    if DIST_DIR.exists():
        logger.info("Serving frontend assets from %s", DIST_DIR)

        @app.route("/", defaults={"path": ""})
        @app.route("/<path:path>")
        def serve_frontend(path: str):
            """Serve the built React SPA."""
            if path.startswith("api/"):
                return jsonify({"error": "Not found"}), 404

            target = DIST_DIR / path
            if path and target.exists():
                return send_from_directory(app.static_folder, path)  # type: ignore[arg-type]
            return send_from_directory(app.static_folder, "index.html")  # type: ignore[arg-type]
    else:
        logger.warning("Frontend build not found at %s; running API-only.", DIST_DIR)

    return app


if __name__ == "__main__":
    flask_app = create_app()
    port = int(os.getenv("PORT", 5000))
    debug = os.getenv("FLASK_DEBUG", "false").lower() == "true"
    flask_app.run(host="0.0.0.0", port=port, debug=debug)
