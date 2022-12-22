import os

import click
from flask import Flask, render_template, request
from flask_login import current_user
from flask_wtf.csrf import CSRFError

from scutwork.blueprints.main import main_bp
from scutwork.blueprints.auth import auth_bp
from scutwork.blueprints.quiz import quiz_bp
#from scutwork.blueprints.api import api_bp
#from scutwork.blueprints.admin import admin_bp
#from scutwork.blueprints.user import user_bp
#from scutwork.blueprints.dashboard import dash_bp
from scutwork.components import csrf, db, login_manager, avatars, toolbar
from scutwork.models import User, Role
from scutwork.settings import config
from scutwork.forger import add_admin, populate_data

basedir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))


def create_app(config_name=None):
    if config_name is None:
        config_name = os.getenv('FLASK_CONFIG', 'production')

    app = Flask('scutwork')
    app.config.from_object(config[config_name])

    register_components(app)
    register_blueprints(app)
    register_commands(app)
    register_error_handlers(app)
    return app


def register_components(app):
    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)
    avatars.init_app(app)
#    toolbar.init_app(app)


def generate_db(app):
    with app.app_context():
        db.create_all()
    Role.init_roles()


def register_blueprints(app):
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(quiz_bp, url_prefix='/quiz')
#    app.register_blueprint(user_bp, url_prefix='/user')
#    app.register_blueprint(dash_bp, url_prefix='/dashboard')
#    app.register_blueprint(api_bp, url_prefix='/api')
#    app.register_blueprint(admin_bp, url_prefix='/admin')


def register_error_handlers(app):
    @app.errorhandler(400)
    def bad_request(e):
        return render_template('error/400.html'), 400

    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('error/404.html'), 404

    @app.errorhandler(500)
    def internal_server_error(e):
        return render_template('error/500.html'), 500

    @app.errorhandler(CSRFError)
    def handle_csrf_error(e):
        return render_template('error/400.html', description=e.description), 400


def register_commands(app):
    @app.cli.command()
    def init():
        '''Initialize database'''
        click.echo('Initializing the database...')
        db.create_all()

        click.echo('Initializing the roles and permissions...')
        Role.init_roles()
        add_admin()
        populate_data()
        click.echo('Done.')
