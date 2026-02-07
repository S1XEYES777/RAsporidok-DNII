from flask import Blueprint, render_template, request, redirect, session
from models import db, User, Task
import base64
from datetime import date as dt_date

profile_bp = Blueprint("profile", __name__)

def require_login():
    return "user_id" in session

@profile_bp.route("/profile", methods=["GET", "POST"])
def profile():
    if not require_login():
        return redirect("/")

    me = User.query.get(session["user_id"])

    if request.method == "POST":
        text = (request.form.get("text") or "").strip()
        d = (request.form.get("date") or "").strip()
        diff = int(request.form.get("difficulty") or 3)
        diff = max(1, min(6, diff))

        if text and d:
            db.session.add(Task(text=text, date=d, difficulty=diff, user_id=me.id))
            db.session.commit()

        return redirect("/profile")

    tasks = Task.query.filter_by(user_id=me.id).order_by(Task.date.desc(), Task.created_at.desc()).all()
    total = len(tasks)
    done = len([t for t in tasks if t.completed])
    progress = int((done / total) * 100) if total else 0

    return render_template("profile.html", me=me, tasks=tasks, progress=progress)

@profile_bp.route("/profile/upload_avatar", methods=["POST"])
def upload_avatar():
    if not require_login():
        return redirect("/")

    me = User.query.get(session["user_id"])
    file = request.files.get("avatar")
    if not file or file.filename == "":
        return redirect("/profile")

    img_bytes = file.read()
    # сохраняем base64 в БД
    me.avatar = base64.b64encode(img_bytes).decode("utf-8")
    db.session.commit()
    return redirect("/profile")

@profile_bp.route("/profile/change_name", methods=["POST"])
def change_name():
    if not require_login():
        return redirect("/")

    me = User.query.get(session["user_id"])
    new_name = (request.form.get("name") or "").strip()

    if not new_name:
        return redirect("/profile?err=empty")

    # имя уже занято?
    exists = User.query.filter(User.name == new_name, User.id != me.id).first()
    if exists:
        return redirect("/profile?err=taken")

    me.name = new_name
    db.session.commit()
    return redirect("/profile")

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
