from app.extensions import db
from app.interns.models import Intern, Attendance, ProgressScore
from datetime import date, timedelta

def mark_attendance(intern_id, attendance_date, status):
    """Mark attendance for an intern."""
    existing = Attendance.query.filter_by(
        intern_id=intern_id, date=attendance_date
    ).first()

    if existing:
        existing.status = status
    else:
        record = Attendance(
            intern_id=intern_id,
            date=attendance_date,
            status=status
        )
        db.session.add(record)

    db.session.commit()
    update_progress_score(intern_id)

def update_progress_score(intern_id):
    """
    Auto-update progress score based on attendance.
    Rule: 5 consecutive absences = -5% per day after that.
    """
    records = Attendance.query.filter_by(intern_id=intern_id)\
                .order_by(Attendance.date.desc()).all()

    if not records:
        return

    # Count consecutive absences from most recent
    consecutive = 0
    for r in records:
        if r.status == "Absent":
            consecutive += 1
        else:
            break

    # Get or create progress score
    progress = ProgressScore.query.filter_by(intern_id=intern_id).first()
    if not progress:
        progress = ProgressScore(intern_id=intern_id, score=100.0)
        db.session.add(progress)

    # Apply rule: >5 consecutive absences = reduce score
    if consecutive > 5:
        penalty = (consecutive - 5) * 5  # 5% per extra day
        base = 100.0
        new_score = max(0, base - penalty)
        progress.score = new_score
        progress.note = f"{consecutive} consecutive absences. Score reduced by {penalty}%"
    else:
        # Recalculate fair score based on overall attendance
        total = len(records)
        present = len([r for r in records if r.status == "Present"])
        late = len([r for r in records if r.status == "Late"])
        
        # Fair formula: present=1pt, late=0.7pt, absent=0pt
        earned = (present * 1.0) + (late * 0.7)
        progress.score = round((earned / total * 100) if total > 0 else 100.0, 1)
        progress.note = f"{present} present, {late} late, {total-present-late} absent"

    progress.consecutive_absences = consecutive
    progress.last_updated = date.today()
    db.session.commit()

def get_intern_attendance_summary(intern_id):
    """Get full attendance summary for an intern."""
    records = Attendance.query.filter_by(intern_id=intern_id)\
                .order_by(Attendance.date.asc()).all()

    total = len(records)
    present = len([r for r in records if r.status == "Present"])
    absent = len([r for r in records if r.status == "Absent"])
    late = len([r for r in records if r.status == "Late"])

    progress = ProgressScore.query.filter_by(intern_id=intern_id).first()
    score = progress.score if progress else 100.0
    consecutive = progress.consecutive_absences if progress else 0
    note = progress.note if progress else "No attendance recorded yet"

    return {
        "total_days": total,
        "present": present,
        "absent": absent,
        "late": late,
        "attendance_rate": round((present / total * 100) if total > 0 else 100, 1),
        "progress_score": score,
        "consecutive_absences": consecutive,
        "records": records,
        "note": note,
    }

def get_leaderboard():
    """Rank all interns by progress score — fair for everyone."""
    interns = Intern.query.filter_by(is_archived=False).all()  # ← ADD THIS FILTER
    scores = []

    for intern in interns:
        progress = ProgressScore.query.filter_by(intern_id=intern.id).first()
        score = progress.score if progress else 100.0
        consecutive = progress.consecutive_absences if progress else 0
        attendance = get_intern_attendance_summary(intern.id)

        scores.append({
            "intern_id": intern.intern_id,
            "name": intern.name,
            "college": intern.college_name,
            "score": score,
            "attendance_rate": attendance["attendance_rate"],
            "consecutive_absences": consecutive,
            "status": "⚠️ At Risk" if consecutive >= 5 else "✅ On Track",
        })

    return sorted(scores, key=lambda x: x["score"], reverse=True)