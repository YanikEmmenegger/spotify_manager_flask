from flask import Flask, send_from_directory
from app.configs import Config, configure_logging
from flask_restful import Api
from app.routes import register_routes
from app.scheduler import start_scheduler
from flask_cors import CORS


def create_app():
    app = Flask(__name__, static_folder="./static", static_url_path="/")
    api = Api(app)

    # Set CORS to allow all origins
    CORS(app, resources={r"*": {"origins": "*"}})

    app.config.from_object(Config)
    # Set logging configuration
    configure_logging()
    # Register all routes from /routes
    register_routes(api)

    @app.route('/')
    def index():
        return send_from_directory(app.static_folder, 'index.html')

    @app.route('/<path:path>')
    def static_proxy(path):
        return send_from_directory(app.static_folder, path)

    # Start the scheduler
    start_scheduler()

    return app
