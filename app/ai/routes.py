from flask import Blueprint
ai_bp = Blueprint("ai", __name__)

@ai_bp.route("/ai")
def index():
    return "AI agent coming soon"