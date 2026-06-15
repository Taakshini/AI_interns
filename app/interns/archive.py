from app.interns.models import Intern
from app.extensions import db
from datetime import datetime

def archive_intern(intern_id, reason=""):
    """Archive an intern."""
    intern = Intern.query.get_or_404(intern_id)
    intern.archive(reason)
    return intern

def restore_intern(intern_id):
    """Restore an archived intern."""
    intern = Intern.query.get_or_404(intern_id)
    intern.restore()
    return intern

def get_archived_interns():
    """Get all archived interns."""
    return Intern.query.filter_by(is_archived=True).order_by(Intern.archived_at.desc()).all()

def get_archive_summary():
    """Get archive statistics."""
    archived = Intern.query.filter_by(is_archived=True).all()
    total_archived = len(archived)
    
    by_reason = {}
    for intern in archived:
        reason = intern.archive_reason or "No reason specified"
        by_reason[reason] = by_reason.get(reason, 0) + 1
    
    return {
        "total_archived": total_archived,
        "by_reason": by_reason,
    }