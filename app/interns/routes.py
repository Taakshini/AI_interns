from flask import Blueprint, render_template, jsonify, request, redirect, url_for, flash
from flask_login import login_required
from app.interns.models import Intern
from app.auth.utils import role_required
from app.interns.attendance import (
    mark_attendance, get_intern_attendance_summary, get_leaderboard
)
from app.interns.archive import (
    archive_intern, restore_intern, get_archived_interns, get_archive_summary
)
from datetime import date as today_date, datetime

interns_bp = Blueprint("interns", __name__)

# ============= ACTIVE INTERNS =============

@interns_bp.route("/interns")
@login_required
def list_interns():
    """List all active (non-archived) interns."""
    interns = Intern.query.filter_by(is_archived=False).all()
    return render_template("interns/list.html", interns=interns)

@interns_bp.route("/interns/<int:id>")
@login_required
def profile(id):
    """View intern profile (active interns only)."""
    intern = Intern.query.filter(
        Intern.id == id,
        Intern.is_archived == False
    ).first_or_404()
    return render_template("interns/profile.html", intern=intern)

@interns_bp.route("/api/interns")
@login_required
def api_list():
    """API: Get all active interns as JSON."""
    interns = Intern.query.filter_by(is_archived=False).all()
    return jsonify([i.to_dict() for i in interns])

# ============= ATTENDANCE =============

@interns_bp.route("/interns/<int:id>/attendance", methods=["GET", "POST"])
@login_required
def attendance(id):
    """Mark and view attendance for an intern."""
    intern = Intern.query.get_or_404(id)
    
    if request.method == "POST":
        attendance_date = request.form.get("date")
        status = request.form.get("status")
        
        parsed_date = datetime.strptime(attendance_date, "%Y-%m-%d").date()
        mark_attendance(id, parsed_date, status)
        flash(f"Attendance marked: {status} for {attendance_date}", "success")
        return redirect(url_for("interns.attendance", id=id))
    
    summary = get_intern_attendance_summary(id)
    return render_template(
        "interns/attendance.html",
        intern=intern,
        summary=summary,
        today=str(today_date.today()),
    )

@interns_bp.route("/leaderboard")
@login_required
def leaderboard():
    """View progress leaderboard."""
    scores = get_leaderboard()
    return render_template("interns/leaderboard.html", scores=scores)

# ============= ARCHIVE =============

@interns_bp.route("/interns/<int:id>/archive", methods=["POST"])
@login_required
@role_required("admin", "hr")
def archive(id):
    """Archive an intern (soft delete)."""
    reason = request.form.get("reason", "Internship Completed")
    archive_intern(id, reason)
    flash(f"Intern archived successfully.", "success")
    return redirect(url_for("interns.list_interns"))

@interns_bp.route("/interns/<int:id>/restore", methods=["POST"])
@login_required
@role_required("admin", "hr")
def restore(id):
    """Restore an archived intern to active status."""
    restore_intern(id)
    flash(f"Intern restored to active status.", "success")
    return redirect(url_for("interns.archive_history"))

@interns_bp.route("/archive")
@login_required
@role_required("admin", "hr")
def archive_history():
    """View archive history page."""
    archived = get_archived_interns()
    summary = get_archive_summary()
    
    return render_template(
        "interns/archive.html",
        archived=archived,
        summary=summary,
    )
def save_interns(interns):
    """Save interns to database, checking for duplicates."""
    from app.extensions import db
    from app.interns.models import Intern
    
    saved = 0
    duplicates = 0
    
    for intern in interns:
        existing = Intern.query.filter_by(intern_id=intern.intern_id).first()
        if existing:
            duplicates += 1
        else:
            db.session.add(intern)
            saved += 1
    
    db.session.commit()
    return saved