from flask import Blueprint, render_template, session, redirect
from models import db, User, Task, Congrat

admin_bp = Blueprint("admin", __name__)

def is_admin():
    uid = session.get("user_id")
    if not uid:
        return False
    u = User.query.get(uid)
    return bool(u and u.is_admin)

@admin_bp.route("/admin")
def admin():
    if not is_admin():
        return redirect("/main")
    users = User.query.order_by(User.created_at.asc()).all()
    return render_template("admin.html", users=users)

@admin_bp.route("/admin/delete_user/<int:user_id>")
def delete_user(user_id):
    if not is_admin():
        return redirect("/main")

    u = User.query.get(user_id)
    if not u or u.name == "Admin0987654321":
        return redirect("/admin")

    user_tasks = Task.query.filter_by(user_id=user_id).all()
    task_ids = [t.id for t in user_tasks]
    if task_ids:
        Congrat.query.filter(Congrat.task_id.in_(task_ids)).delete(synchronize_session=False)

    Task.query.filter_by(user_id=user_id).delete()
    db.session.delete(u)
    db.session.commit()
    return redirect("/admin")
