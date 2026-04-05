from flask import Flask
from .config import Config
from .extensions import db, migrate, jwt, cors
from .auth.routes import auth_bp
from .matches.routes import match_bp
from .admin.routes import admin_bp
from .common.routes import common_bp
import os


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    cors.init_app(app, resources={r"/api/*": {"origins": "*"}})

    app.register_blueprint(common_bp, url_prefix='/api')
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(match_bp, url_prefix='/api')
    app.register_blueprint(admin_bp, url_prefix='/api/admin')

    @app.cli.command('seed')
    def seed_command():
        from .seed import run_seed
        run_seed()
        print('Seed data created.')

    return app
