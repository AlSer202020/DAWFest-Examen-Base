import os
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Configuración centralizada de la aplicación DAW-Fest."""

    SECRET_KEY = os.environ.get("SECRET_KEY", "clave-desarrollo-dawfest-2026")
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL", "sqlite:///dawfest.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    UPLOAD_FOLDER = os.path.join("app", "static", "img", "uploads")
    MAX_CONTENT_LENGTH = 2 * 1024 * 1024

    PERMANENT_SESSION_LIFETIME = timedelta(days=2)

    DEBUG = True
    DEBUG_TB_INTERCEPT_REDIRECTS = False