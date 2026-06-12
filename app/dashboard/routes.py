from flask import Blueprint, render_template, jsonify
from flask_login import login_required
from app.dashboard.utils import get_dashboard_stats, get_recent_interns, get_at_risk_interns
from app.interns.models import Intern

dashboard_bp = Blueprint("dashboard", __name__)

@dashboard_bp.route("/")
@dashboard_bp.route("/dashboard")
@login_required
def index():
    stats = get_dashboard_stats()
    recent = get_recent_interns(5)
    at_risk = get_at_risk_interns()
    
    return render_template(
        "dashboard/index.html",
        stats=stats,
        recent=recent,
        at_risk=at_risk,
    )

@dashboard_bp.route("/api/stats")
@login_required
def api_stats():
    """API endpoint — returns JSON stats for dynamic updates."""
    stats = get_dashboard_stats()
    return jsonify(stats)

@dashboard_bp.route("/api/chart/status")
@login_required
def chart_status():
    """Data for status pie chart."""
    stats = get_dashboard_stats()
    return jsonify({
        "labels": list(stats["by_status"].keys()),
        "data": list(stats["by_status"].values()),
    })

@dashboard_bp.route("/api/chart/college")
@login_required
def chart_college():
    """Data for college bar chart."""
    stats = get_dashboard_stats()
    return jsonify({
        "labels": list(stats["by_college"].keys()),
        "data": list(stats["by_college"].values()),
    })

@dashboard_bp.route("/api/chart/fte")
@login_required
def chart_fte():
    """Data for FTE recommendation pie chart."""
    stats = get_dashboard_stats()
    return jsonify({
        "labels": ["YES", "NO"],
        "data": [stats["fte_yes"], stats["fte_no"]],
    })