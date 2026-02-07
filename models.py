from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)

    # аватар хранится в БД как base64 (без data:image/..)
    avatar = db.Column(db.Text, nullable=True)

    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(220), nullable=False)
    date = db.Column(db.String(10), nullable=False)   # YYYY-MM-DD
    difficulty = db.Column(db.Integer, default=3)     # 1..6
    completed = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)

class Congrat(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    task_id = db.Column(db.Integer, nullable=False)
    user_id = db.Column(db.Integer, nullable=False)   # кто поздравил
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
