from flask import Blueprint, render_template, jsonify, send_file, flash, redirect, url_for
from flask_login import login_required
import os
from app.interns.models import Intern
from app.reports.utils import generate_intern_report, generate_cohort_report
from app.config import Config
from app.auth.utils import role_required

reports_bp = Blueprint("reports", __name__)

@reports_bp.route("/reports")
@login_required
@role_required("admin", "hr")
def index():
    interns = Intern.query.all()
    return render_template("reports/index.html", interns=interns)

@reports_bp.route("/download/intern/<int:intern_id>")
@login_required
def download_intern_report(intern_id):
    intern = Intern.query.get_or_404(intern_id)
    filename = f"report_{intern.intern_id}.pdf"
    filepath = os.path.join(Config.UPLOAD_FOLDER, filename)
    
    try:
        from app.reports.utils import generate_intern_report
        generate_intern_report(intern_id, filepath)
        return send_file(filepath, as_attachment=True, download_name=filename)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@reports_bp.route("/download/cohort")
@login_required
@role_required("admin", "hr")
def download_cohort_report():
    filename = f"cohort_report.pdf"
    filepath = os.path.join(Config.UPLOAD_FOLDER, filename)
    
    try:
        from app.reports.utils import generate_cohort_report
        generate_cohort_report(filepath)
        return send_file(filepath, as_attachment=True, download_name=filename)
    except Exception as e:
        return jsonify({"error": str(e)}), 500