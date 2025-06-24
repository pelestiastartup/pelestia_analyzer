# app.py
from flask import Flask, session
from flask_babelplus import Babel
from json import JSONEncoder
from flask import Flask
from flask.json.provider import JSONProvider
from dotenv import load_dotenv
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_mail import Mail
import os
import json
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
SECRET_KEY = os.getenv("SECRET_KEY")
REPLICATE_API_TOKEN = os.getenv("REPLICATE_API_TOKEN")
GMAIL_PASSWORD = os.getenv("GMAIL_PASSWORD")

# Custom JSON Provider to handle special types
class CustomJSONProvider(JSONProvider):
    def default(self, obj):
        if isinstance(obj, pd.DataFrame):
            return {
                '__type__': 'DataFrame',
                'data': obj.to_dict('records'),
                'columns': list(obj.columns)
            }
        if isinstance(obj, pd.Series):
            return {
                '__type__': 'Series',
                'data': obj.to_dict()
            }
        if isinstance(obj, (np.integer, np.int32, np.int64)):
            return int(obj)
        if isinstance(obj, (np.floating, np.float32, np.float64)):
            return float(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        if isinstance(obj, datetime):
            return obj.isoformat()
        if isinstance(obj, dict):
            return {str(k): v for k, v in obj.items()}
        return super().default(obj)

    def dumps(self, obj, **kwargs):
        return json.dumps(self.default(obj), **kwargs)

    def loads(self, s, **kwargs):
        return json.loads(s, **kwargs)

# Initialize extensions without binding to app
db = SQLAlchemy()
jwt = JWTManager()
babel = Babel()
mail = Mail()

def create_app():
    load_dotenv()

    app = Flask(__name__)
    CORS(app)
    app.json_provider_class = CustomJSONProvider
    app.secret_key = os.getenv("SECRET_KEY", "super-secret-key")
    app.config['SESSION_TYPE'] = 'filesystem'
    app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=1)
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///pelestia.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET', 'super-secret-jwt-key')
    app.config['MAIL_SERVER'] = 'smtp.gmail.com'
    app.config['MAIL_PORT'] = 587
    app.config['MAIL_USE_TLS'] = True
    app.config['MAIL_USERNAME'] = 'pelestiastartup@gmail.com'
    app.config['MAIL_PASSWORD'] = os.getenv('GMAIL_PASSWORD')
    app.config['MAIL_DEFAULT_SENDER'] = 'pelestiastartup@gmail.com'

    # Configure upload folder
    UPLOAD_FOLDER = 'uploads'
    ALLOWED_EXTENSIONS = {'csv', 'xlsx', 'xls'}
    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)

    # Initialize Babel
    app.config['LANGUAGES'] = {'en': 'English', 'ar': 'العربية'}
    app.config['BABEL_DEFAULT_LOCALE'] = 'en'

    # Initialize extensions with app
    db.init_app(app)
    jwt.init_app(app)
    babel.init_app(app)
    mail.init_app(app)

    @babel.localeselector
    def get_locale():
        return session.get('language', 'en')

    # Import and register routes blueprint
    from routes import bp as routes_blueprint
    app.register_blueprint(routes_blueprint)

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
