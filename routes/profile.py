from flask import Blueprint, render_template, request, redirect, session
from models import db, User, Task
import base64

profile_bp = Blueprint("profile", __name__)

@profile_bp.route("/profile", methods=["GET", "POST"])
def profile():

    if "user_id" not in session:
        return redirect("/")

    user = User.query.get(session["user_id"])

    if request.method == "POST":

        text = request.form["text"]
        date = request.form["date"]
        difficulty = int(request.form["difficulty"])

        t = Task(
            text=text,
            date=date,
            difficulty=difficulty,
            user_id=user.id
        )

        db.session.add(t)
        db.session.commit()

    tasks = Task.query.filter_by(user_id=user.id).all()

    done = len([t for t in tasks if t.completed])
    progress = int((done / len(tasks)) * 100) if tasks else 0

    return render_template("profile.html",
                           me=user,
                           tasks=tasks,
                           progress=progress)


@profile_bp.route("/profile/upload_avatar", methods=["POST"])
def upload_avatar():

    if "user_id" not in session:
        return redirect("/")

    user = User.query.get(session["user_id"])

    file = request.files.get("avatar")

    if not file:
        return redirect("/profile")

    img_bytes = file.read()

    encoded = base64.b64encode(img_bytes).decode("utf-8")

    user.avatar = encoded
    db.session.commit()

    return redirect("/profile")


@profile_bp.route("/profile/delete/<int:id>")
def delete_task(id):

    t = Task.query.get(id)

    if t and t.user_id == session["user_id"]:
        db.session.delete(t)
        db.session.commit()

    return redirect("/profile")


@profile_bp.route("/profile/toggle/<int:id>")
def toggle_task(id):

    t = Task.query.get(id)

    if t and t.user_id == session["user_id"]:
        t.completed = not t.completed
        db.session.commit()

    return redirect("/profile")
