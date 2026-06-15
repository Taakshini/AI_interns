from flask import Blueprint, render_template, jsonify
from flask_login import login_required
from app.interns.models import Intern
from app.dashboard.utils import get_dashboard_stats, get_recent_interns, get_at_risk_interns
from app.auth.utils import role_required 

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
@dashboard_bp.route("/cohort-analytics")
@login_required
@role_required("admin", "hr")
def cohort_analytics():
    from app.dashboard.cohort_analytics import (
        calculate_college_performance,
        calculate_department_performance,
        identify_at_risk_interns,
        generate_hiring_scores,
        predict_next_cohort_conversion,
        get_cohort_insights,
    )
    
    colleges = calculate_college_performance()
    departments = calculate_department_performance()
    at_risk = identify_at_risk_interns()
    hiring_scores = generate_hiring_scores()
    next_cohort = predict_next_cohort_conversion()
    
    # Calculate current conversion rate
    interns = Intern.query.all()
    total = len(interns)
    fte_yes = len([i for i in interns if i.fte_recommendation == "YES"])
    current_rate = round((fte_yes / total * 100) if total > 0 else 0, 1)
    
    cohort_insights = get_cohort_insights()["insights"]
    
    return render_template(
        "cohort_analytics.html",
        colleges=colleges,
        departments=departments,
        at_risk=at_risk,
        hiring_scores=hiring_scores,
        next_cohort_prediction=next_cohort,
        current_conversion_rate=current_rate,
        total_interns=total,
        cohort_insights=cohort_insights,
    )