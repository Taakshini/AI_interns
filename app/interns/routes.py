from flask import Blueprint, render_template, jsonify
from flask_login import login_required
from app.interns.models import Intern
from app.auth.utils import role_required

interns_bp = Blueprint("interns", __name__)

@interns_bp.route("/interns")
@login_required
def list_interns():
    interns = Intern.query.all()
    return render_template("interns/list.html", interns=interns)

@interns_bp.route("/interns/<int:id>")
@login_required
def profile(id):
    intern = Intern.query.get_or_404(id)
    return render_template("interns/profile.html", intern=intern)

@interns_bp.route("/api/interns")
@login_required
def api_list():
    interns = Intern.query.all()
    return jsonify([i.to_dict() for i in interns])