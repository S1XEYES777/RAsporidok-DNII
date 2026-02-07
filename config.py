import os

class Config:

    SECRET_KEY = os.environ.get("SECRET_KEY", "dev")

    db_url = os.environ.get("DATABASE_URL")

    if db_url and db_url.startswith("postgres://"):
        db_url = db_url.replace("postgres://", "postgresql://", 1)

    SQLALCHEMY_DATABASE_URI = db_url or "sqlite:///database.db"

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = "static/avatars"
