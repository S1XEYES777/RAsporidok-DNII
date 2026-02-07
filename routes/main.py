from flask import Blueprint, render_template, session, redirect, jsonify
from models import User, Task, Congrat, db
from datetime import date

main_bp = Blueprint("main", __name__)

@main_bp.route("/main")
def main():

    if "user_id" not in session:
        return redirect("/")

    return render_template("main.html")


@main_bp.route("/api/data")
def data():

    today = str(date.today())
    users = User.query.all()

    result = []

    for u in users:

        tasks = Task.query.filter_by(user_id=u.id, date=today).all()

        result.append({
            "name":u.name,
            "avatar":u.avatar,
            "tasks":[
                {
                    "id":t.id,
                    "text":t.text,
                    "difficulty":t.difficulty,
                    "completed":t.completed,
                    "congrats": Congrat.query.filter_by(task_id=t.id).count(),
                    "user_congrat": bool(
                        Congrat.query.filter_by(
                            task_id=t.id,
                            user_id=session["user_id"]
                        ).first()
                    )
                }
                for t in tasks
            ]
        })

    return jsonify(result)
