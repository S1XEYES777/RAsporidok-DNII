from flask import Blueprint, render_template, session, redirect
from models import User, Task, db

admin_bp = Blueprint("admin", __name__)

@admin_bp.route("/admin")
def admin():

    user = User.query.get(session["user_id"])

    if not user.is_admin:
        return redirect("/main")

    users = User.query.all()
    return render_template("admin.html",users=users)


@admin_bp.route("/delete_user/<int:id>")
def delete_user(id):

    user = User.query.get(session["user_id"])

    if not user.is_admin:
        return redirect("/main")

    u = User.query.get(id)

    Task.query.filter_by(user_id=id).delete()

    db.session.delete(u)
    db.session.commit()

    return redirect("/admin")
