from flask import Flask
from app.configs.config import Config
from app.logging_config import configure_logging


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    configure_logging()

    with app.app_context():
        from app.routes import api, auth
        app.register_blueprint(api.bp, url_prefix='/api')
        app.register_blueprint(auth.bp, url_prefix='/api/auth')

    @app.route('/')
    def index():
        return 'Hello, World!'

    return app
