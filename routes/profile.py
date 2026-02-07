from flask import Blueprint, render_template, request, redirect, session
from models import db, Task, User
import os
from werkzeug.utils import secure_filename
from flask import current_app

profile_bp = Blueprint("profile", __name__)

ALLOWED_EXTENSIONS = {"png","jpg","jpeg"}

def allowed_file(filename):
    return "." in filename and filename.rsplit(".",1)[1].lower() in ALLOWED_EXTENSIONS

@profile_bp.route("/profile", methods=["GET","POST"])
def profile():

    user = User.query.get(session["user_id"])

    if request.method == "POST":

        text = request.form["text"]
        date = request.form["date"]
        difficulty = request.form["difficulty"]

        task = Task(text=text,date=date,difficulty=difficulty,user_id=user.id)

        db.session.add(task)
        db.session.commit()

        return redirect("/profile")

    tasks = Task.query.filter_by(user_id=user.id).all()

    return render_template("profile.html", tasks=tasks, me=user)


@profile_bp.route("/upload_avatar", methods=["POST"])
def upload_avatar():

    user = User.query.get(session["user_id"])

    file = request.files["avatar"]

    if file and allowed_file(file.filename):

        filename = secure_filename(file.filename)
        filename = f"user_{user.id}_{filename}"

        filepath = os.path.join(current_app.config["UPLOAD_FOLDER"], filename)

        file.save(filepath)

        user.avatar = filename
        db.session.commit()

    return redirect("/profile")

