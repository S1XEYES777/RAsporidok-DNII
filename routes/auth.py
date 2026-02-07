from flask import Blueprint, render_template, request, redirect, session
from models import db, User

auth_bp = Blueprint("auth", __name__)
ADMIN_NAME = "Admin0987654321"

@auth_bp.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        name = (request.form.get("name") or "").strip()

        if not name:
            return render_template("login.html", error="Введите имя")

        user = User.query.filter_by(name=name).first()
        if not user:
            user = User(name=name, is_admin=(name == ADMIN_NAME))
            db.session.add(user)
            db.session.commit()

        session["user_id"] = user.id
        return redirect("/main")

    return render_template("login.html", error=None)

@auth_bp.route("/logout")
def logout():
    session.pop("user_id", None)
    return redirect("/")
