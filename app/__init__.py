from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
import os
from datetime import timedelta
import re
try:
    from markupsafe import Markup, escape
except ImportError:
    from jinja2 import Markup, escape

csrf = CSRFProtect()
db = SQLAlchemy()
login_manager = LoginManager()

_paragraph_re = re.compile(r'(?:\r\n|\r(?!\n)|\n){2,}')

def nl2br(value):
    if not value:
        return ''
    escaped_value = escape(value)
    paragraphs = _paragraph_re.split(escaped_value)
    paragraphs = [p for p in paragraphs if p]
    html_paragraphs = []
    for p_text in paragraphs:
        p_with_br = p_text.replace('\n', '<br>\n')
        html_paragraphs.append(f'<p>{p_with_br}</p>')
    result = '\n\n'.join(html_paragraphs)
    return Markup(result)


def create_app():
    app = Flask(__name__, instance_relative_config=True)

    # --- CONFIGURATION ---
    app.config.from_mapping(
        SECRET_KEY='a_default_development_secret_key_please_change_in_instance_config',
        SQLALCHEMY_DATABASE_URI='sqlite:///' + os.path.join(app.instance_path, 'site.db'),
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        GOOGLE_API_KEY=None,
        PERMANENT_SESSION_LIFETIME=timedelta(days=7),
        MAX_CONTENT_LENGTH=2 * 1024 * 1024,
        UPLOAD_EXTENSIONS=['.jpg', '.png', '.jpeg'],
        WTF_CSRF_ENABLED=True
    )

    if os.path.exists(os.path.join(app.instance_path, 'config.py')):
        app.config.from_pyfile('config.py', silent=False)

    if app.config['SECRET_KEY'] == 'a_default_development_secret_key_please_change_in_instance_config' and \
       not app.debug:
        print("WARNING: Using default SECRET_KEY. Please set a strong SECRET_KEY in instance/config.py for production.")

    app.permanent_session_lifetime = app.config['PERMANENT_SESSION_LIFETIME']
    app.config.setdefault('UPLOAD_EXTENSIONS', ['.jpg', '.png', '.jpeg'])

    # --- INITIALIZE EXTENSIONS WITH THE APP ---
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'main.login'
    login_manager.login_message_category = 'info'
    csrf.init_app(app)

    app.jinja_env.filters['nl2br'] = nl2br

    from . import models

    with app.app_context():
        db.create_all()
        print(f"Database will be created/used at: {app.config['SQLALCHEMY_DATABASE_URI']}")

    from .routes import main_bp
    app.register_blueprint(main_bp)

    return app