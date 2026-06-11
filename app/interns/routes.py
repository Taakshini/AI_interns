from flask import Blueprint
interns_bp = Blueprint("interns", __name__)

@interns_bp.route("/interns")
def list_interns():
    return "Interns list coming soon"