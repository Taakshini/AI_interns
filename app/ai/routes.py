from flask import Blueprint, render_template, jsonify, request
from flask_login import login_required
from app.interns.models import Intern
from app.ai.utils import analyze_intern_feedback, predict_conversion, recommend_tasks, generate_cohort_summary
from app.auth.utils import role_required

ai_bp = Blueprint("ai", __name__)

@ai_bp.route("/ai")
@login_required
def index():
    """AI Agent dashboard."""
    return render_template("ai/index.html")

@ai_bp.route("/api/ai/analyze/<int:intern_id>")
@login_required
def api_analyze(intern_id):
    """Analyze a specific intern's feedback (LOCAL, no API)."""
    intern = Intern.query.get_or_404(intern_id)
    analysis = analyze_intern_feedback(intern)
    return jsonify({
        "intern_id": intern.intern_id,
        "name": intern.name,
        "analysis": analysis,
    })

@ai_bp.route("/api/ai/predict/<int:intern_id>")
@login_required
def api_predict(intern_id):
    """Predict if intern will convert (LOCAL, no API)."""
    intern = Intern.query.get_or_404(intern_id)
    prediction = predict_conversion(intern)
    return jsonify({
        "intern_id": intern.intern_id,
        "name": intern.name,
        "prediction": prediction,
    })

@ai_bp.route("/api/ai/recommend/<int:intern_id>")
@login_required
def api_recommend(intern_id):
    """Recommend tasks for intern (LOCAL, no API)."""
    intern = Intern.query.get_or_404(intern_id)
    recommendations = recommend_tasks(intern)
    return jsonify({
        "intern_id": intern.intern_id,
        "name": intern.name,
        "recommendations": recommendations,
    })

@ai_bp.route("/api/ai/cohort-summary")
@login_required
@role_required("admin", "hr")
def api_cohort_summary():
    """Generate summary for entire cohort (LOCAL, no API)."""
    interns = Intern.query.all()
    summary = generate_cohort_summary(interns)
    return jsonify({
        "total_interns": len(interns),
        "summary": summary,
    })