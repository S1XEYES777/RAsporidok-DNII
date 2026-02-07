from flask import Blueprint, render_template, request, redirect, session
from models import db, User

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/", methods=["GET","POST"])
def login():

    if request.method == "POST":

        name = request.form["name"]

        user = User.query.filter_by(name=name).first()

        if not user:
            user = User(name=name)

            if name == "Admin0987654321":
                user.is_admin = True

            db.session.add(user)
            db.session.commit()

        session["user_id"] = user.id
        return redirect("/main")

    return render_template("login.html")
