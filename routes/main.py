from flask import Blueprint, render_template, session, redirect
from models import User, Task

from datetime import date

main_bp = Blueprint("main", __name__)

@main_bp.route("/main")
def main():

    if "user_id" not in session:
        return redirect("/")

    today = str(date.today())
    users = User.query.all()

    data = []

    for u in users:
        tasks = Task.query.filter_by(user_id=u.id,date=today).all()

        data.append({
            "user":u,
            "tasks":tasks
        })

    return render_template("main.html", data=data)

