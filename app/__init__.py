import os
from pathlib import Path

from dotenv import load_dotenv
from flask import Flask

from .db import init_app
from .routes import bp as main_bp
from .twilio_webhooks import bp as twilio_bp


def create_app(test_config=None):
    load_dotenv()
    app = Flask(
        __name__,
        instance_relative_config=True,
        template_folder="../templates",
        static_folder="../static",
    )
    default_db = Path(app.instance_path) / "releaseguard.db"
    app.config.from_mapping(
        SECRET_KEY=os.getenv("SECRET_KEY", "dev-only-change-me"),
        DATABASE_PATH=os.getenv("DATABASE_PATH", str(default_db)),
        APP_VERSION=os.getenv("APP_VERSION", "1.0.0"),
        BUILD_API_TOKEN=os.getenv("BUILD_API_TOKEN", ""),
        TWILIO_AUTH_TOKEN=os.getenv("TWILIO_AUTH_TOKEN", ""),
        TWILIO_WEBHOOK_URL=os.getenv("TWILIO_WEBHOOK_URL", ""),
        ENABLE_DEMO_CONTROLS=os.getenv("ENABLE_DEMO_CONTROLS", "true").lower() == "true",
    )
    if test_config:
        app.config.update(test_config)

    Path(app.config["DATABASE_PATH"]).parent.mkdir(parents=True, exist_ok=True)
    init_app(app)
    app.register_blueprint(main_bp)
    app.register_blueprint(twilio_bp)

    with app.app_context():
        from .db import init_db
        init_db()
    return app
