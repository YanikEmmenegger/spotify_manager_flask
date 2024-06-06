from flask import Flask, send_from_directory
from app.configs.config import Config
from app.logging_config import configure_logging
import os


def create_app():
    app = Flask(__name__, static_folder="../static/dist", static_url_path="/")

    app.config.from_object(Config)

    configure_logging()

    with app.app_context():
        from app.routes import api, auth
        app.register_blueprint(api.bp, url_prefix='/api')
        app.register_blueprint(auth.bp, url_prefix='/api/auth')

    @app.route('/')
    def index():
        return send_from_directory(app.static_folder, 'index.html')

    @app.route('/<path:path>')
    def static_proxy(path):
        return send_from_directory(app.static_folder, path)

    return app
