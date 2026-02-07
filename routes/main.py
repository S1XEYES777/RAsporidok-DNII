from flask import Blueprint, render_template, session, redirect, jsonify, request
from models import db, User, Task, Congrat
from datetime import date
from sqlalchemy import func

main_bp = Blueprint("main", __name__)

def require_login():
    return "user_id" in session

@main_bp.route("/main")
def main():
    if not require_login():
        return redirect("/")
    return render_template("main.html")

@main_bp.route("/api/today")
def api_today():
    if not require_login():
        return jsonify({"error": "not_logged_in"}), 401

    today = str(date.today())
    me_id = session["user_id"]

    users = User.query.order_by(User.created_at.asc()).all()
    tasks = Task.query.filter_by(date=today).all()
    task_ids = [t.id for t in tasks]

    # количество поздравлений по задаче
    congrats_count = {}
    if task_ids:
        rows = (
            db.session.query(Congrat.task_id, func.count(Congrat.id))
            .filter(Congrat.task_id.in_(task_ids))
            .group_by(Congrat.task_id)
            .all()
        )
        congrats_count = {tid: cnt for tid, cnt in rows}

    # поздравлял ли текущий юзер эту задачу
    my_congrats = set()
    if task_ids:
        rows = Congrat.query.filter(Congrat.task_id.in_(task_ids), Congrat.user_id == me_id).all()
        my_congrats = set(r.task_id for r in rows)

    result_users = []
    for u in users:
        u_tasks = [t for t in tasks if t.user_id == u.id]
        result_users.append({
            "id": u.id,
            "name": u.name,
            "avatar": u.avatar,
            "tasks": [
                {
                    "id": t.id,
                    "text": t.text,
                    "difficulty": int(t.difficulty),
                    "completed": bool(t.completed),
                    "congrats": int(congrats_count.get(t.id, 0)),
                    "youCongrat": (t.id in my_congrats),
                    "ownerId": t.user_id
                }
                for t in u_tasks
            ]
        })

    return jsonify({
        "today": today,
        "me": me_id,
        "users": result_users
    })

@main_bp.route("/api/congrat", methods=["POST"])
def api_congrat():
    if not require_login():
        return jsonify({"error": "not_logged_in"}), 401

    me_id = session["user_id"]
    task_id = int((request.json or {}).get("task_id", 0))

    t = Task.query.get(task_id)
    if not t:
        return jsonify({"ok": False, "error": "task_not_found"}), 404

    # поздравлять можно ТОЛЬКО если задача выполнена
    if not t.completed:
        return jsonify({"ok": False, "error": "task_not_completed"}), 400

    # нельзя поздравлять себя
    if t.user_id == me_id:
        return jsonify({"ok": False, "error": "self"}), 400

    exists = Congrat.query.filter_by(task_id=task_id, user_id=me_id).first()
    if exists:
        return jsonify({"ok": False, "error": "already"}), 400

    db.session.add(Congrat(task_id=task_id, user_id=me_id))
    db.session.commit()
    return jsonify({"ok": True})
