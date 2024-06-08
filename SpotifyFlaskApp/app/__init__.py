# app/__init__.py
from flask import Flask, send_from_directory
from app.configs import Config
from app.logging_config import configure_logging
from app.routes import api_bp, auth_bp  # Ensure these imports are correct


def create_app():
    app = Flask(__name__, static_folder="./static", static_url_path="/")

    app.config.from_object(Config)

    configure_logging()

    with app.app_context():
        app.register_blueprint(api_bp, url_prefix='/api')
        app.register_blueprint(auth_bp, url_prefix='/api/auth')

    @app.route('/')
    def index():
        return send_from_directory(app.static_folder, 'index.html')

    @app.route('/<path:path>')
    def static_proxy(path):
        return send_from_directory(app.static_folder, path)

    return app
