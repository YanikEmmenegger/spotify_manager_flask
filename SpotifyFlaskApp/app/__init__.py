from flask import Flask, send_from_directory
from app.configs import Config
from app.logging_config import configure_logging
from app.routes import services_bp, auth_bp, user_bp, playlist_bp
from app.scheduler import start_scheduler


def create_app():
    app = Flask(__name__, static_folder="./static", static_url_path="/")

    app.config.from_object(Config)

    configure_logging()

    with app.app_context():
        app.register_blueprint(services_bp, url_prefix='/api/service')
        app.register_blueprint(auth_bp, url_prefix='/api/auth')
        app.register_blueprint(user_bp, url_prefix='/api/user')
        app.register_blueprint(playlist_bp, url_prefix='/api/playlist')

    @app.route('/')
    def index():
        return send_from_directory(app.static_folder, 'index.html')

    @app.route('/<path:path>')
    def static_proxy(path):
        return send_from_directory(app.static_folder, path)

    # Start the scheduler
    start_scheduler()

    return app
