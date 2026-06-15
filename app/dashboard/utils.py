from app.interns.models import Intern
from sqlalchemy import func

def get_dashboard_stats():
    """Calculate all metrics for the dashboard (excluding archived interns)."""
    interns = Intern.query.filter_by(is_archived=False).all()  # ← ADD THIS FILTER
    total = len(interns)
    
    if total == 0:
        return {
            "total_interns": 0,
            "pursuing_count": 0,
            "relieved_count": 0,
            "conversion_rate": 0,
            "fte_yes": 0,
            "fte_no": 0,
            "diversity": {"male": 0, "female": 0, "other": 0},
            "by_status": {},
            "by_college": {},
        }
    
    pursuing = len([i for i in interns if i.status == "Pursuing"])
    relieved = len([i for i in interns if i.status == "Relieved"])
    fte_yes = len([i for i in interns if i.fte_recommendation == "YES"])
    fte_no = len([i for i in interns if i.fte_recommendation == "NO"])
    
    return {
        "total_interns": total,
        "pursuing_count": pursuing,
        "relieved_count": relieved,
        "conversion_rate": round((fte_yes / total * 100) if total > 0 else 0, 1),
        "fte_yes": fte_yes,
        "fte_no": fte_no,
        "diversity": {
            "male": len([i for i in interns if "male" in (i.intern_type or "").lower()]),
            "female": len([i for i in interns if "female" in (i.intern_type or "").lower()]),
            "other": total - len([i for i in interns if "male" in (i.intern_type or "").lower() or "female" in (i.intern_type or "").lower()]),
        },
        "by_status": {
            "Pursuing": pursuing,
            "Relieved": relieved,
        },
        "by_college": _get_college_distribution(interns),
    }

def get_recent_interns(limit=5):
    """Get most recently added interns (excluding archived)."""
    return Intern.query.filter_by(is_archived=False).order_by(Intern.created_at.desc()).limit(limit).all()

def get_at_risk_interns():
    """Identify interns that might not convert (excluding archived)."""
    return Intern.query.filter_by(is_archived=False, fte_recommendation="NO").all()
    
def _get_college_distribution(interns):
    """Group interns by college."""
    dist = {}
    for intern in interns:
        college = intern.college_name or "Unknown"
        dist[college] = dist.get(college, 0) + 1
    return dict(sorted(dist.items(), key=lambda x: x[1], reverse=True)[:5])

def get_recent_interns(limit=5):
    """Get most recently added interns."""
    return Intern.query.order_by(Intern.created_at.desc()).limit(limit).all()

def get_at_risk_interns():
    """Identify interns that might not convert (FTE NO)."""
    return Intern.query.filter_by(fte_recommendation="NO").all()