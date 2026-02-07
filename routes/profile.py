import os
from flask import Blueprint, render_template, request, redirect, session, current_app
from werkzeug.utils import secure_filename
from models import db, User, Task

profile_bp = Blueprint("profile", __name__)

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "webp"}

def require_login():
    return "user_id" in session

def allowed_file(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

@profile_bp.route("/profile", methods=["GET", "POST"])
def profile():
    if not require_login():
        return redirect("/")

    me = User.query.get(session["user_id"])

    if request.method == "POST":
        text = (request.form.get("text") or "").strip()
        d = (request.form.get("date") or "").strip()
        diff = int(request.form.get("difficulty") or 3)

        if not text or not d:
            return redirect("/profile")

        diff = max(1, min(6, diff))

        db.session.add(Task(text=text, date=d, difficulty=diff, user_id=me.id))
        db.session.commit()
        return redirect("/profile")

    tasks = Task.query.filter_by(user_id=me.id).order_by(Task.date.desc(), Task.created_at.desc()).all()

    total = len(tasks)
    done = len([t for t in tasks if t.completed])
    progress = int((done / total) * 100) if total else 0

    return render_template("profile.html", me=me, tasks=tasks, progress=progress)

@profile_bp.route("/profile/toggle/<int:task_id>")
def toggle_task(task_id):
    if not require_login():
        return redirect("/")

    me_id = session["user_id"]
    t = Task.query.get(task_id)
    if t and t.user_id == me_id:
        t.completed = not t.completed
        db.session.commit()
    return redirect("/profile")

@profile_bp.route("/profile/delete/<int:task_id>")
def delete_task(task_id):
    if not require_login():
        return redirect("/")

    me_id = session["user_id"]
    t = Task.query.get(task_id)
    if t and t.user_id == me_id:
        db.session.delete(t)
        db.session.commit()
    return redirect("/profile")

@profile_bp.route("/profile/upload_avatar", methods=["POST"])
def upload_avatar():
    if not require_login():
        return redirect("/")

    me = User.query.get(session["user_id"])

    file = request.files.get("avatar")
    if not file or file.filename == "":
        return redirect("/profile")

    if not allowed_file(file.filename):
        return redirect("/profile")

    filename = secure_filename(file.filename)
    filename = f"user_{me.id}_{filename}"

    path = os.path.join(current_app.config["UPLOAD_FOLDER"], filename)
    file.save(path)

    me.avatar = filename
    db.session.commit()
    return redirect("/profile")
