from flask import Flask
from config import Config
from models import db
from routes.auth import auth_bp
from routes.main import main_bp
from routes.profile import profile_bp
from routes.admin import admin_bp
from werkzeug.middleware.proxy_fix import ProxyFix
import os

app = Flask(__name__)
app.config.from_object(Config)

# Фикс для Render / прокси
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1)

db.init_app(app)

with app.app_context():
    db.create_all()

    # Создаём папку для аватаров
    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

app.register_blueprint(auth_bp)
app.register_blueprint(main_bp)
app.register_blueprint(profile_bp)
app.register_blueprint(admin_bp)

if __name__ == "__main__":
    app.run(debug=True)
