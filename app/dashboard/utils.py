from app.interns.models import Intern
from sqlalchemy import func


def get_dashboard_stats():
    """
    Calculate all metrics for the dashboard (excluding archived interns).
    Returns dict with all stats including chart data.
    """
    # Get all non-archived interns
    interns = Intern.query.filter_by(is_archived=False).all()
    total = len(interns)
    
    # Handle empty database
    if total == 0:
        return {
            "total_interns": 0,
            "pursuing_count": 0,
            "relieved_count": 0,
            "conversion_rate": 0,
            "fte_yes": 0,
            "fte_no": 0,
            "by_status": {"Pursuing": 0, "Relieved": 0},
            "by_college": {"No Data": 0},
        }
    
    # Count by status
    pursuing = len([i for i in interns if i.status == "Pursuing"])
    relieved = len([i for i in interns if i.status == "Relieved"])
    
    # Count by FTE
    fte_yes = len([i for i in interns if i.fte_recommendation == "YES"])
    fte_no = len([i for i in interns if i.fte_recommendation == "NO"])
    
    # Count by college
    college_dist = {}
    for intern in interns:
        college = intern.college_name or "Unknown"
        college_dist[college] = college_dist.get(college, 0) + 1
    
    # Sort by count and take top 5
    top_colleges = dict(sorted(college_dist.items(), key=lambda x: x[1], reverse=True)[:5])
    
    # Ensure by_status has all keys
    by_status = {
        "Pursuing": pursuing,
        "Relieved": relieved,
    }
    
    return {
        "total_interns": total,
        "pursuing_count": pursuing,
        "relieved_count": relieved,
        "conversion_rate": round((fte_yes / total * 100) if total > 0 else 0, 1),
        "fte_yes": fte_yes,
        "fte_no": fte_no,
        "by_status": by_status,  # For chart_status() endpoint
        "by_college": top_colleges,  # For chart_college() endpoint
    }


def get_recent_interns(limit=5):
    """Get most recently added interns (excluding archived)."""
    return (
        Intern.query
        .filter_by(is_archived=False)
        .order_by(Intern.created_at.desc())
        .limit(limit)
        .all()
    )


def get_at_risk_interns():
    """Identify interns with FTE: NO (excluding archived)."""
    return (
        Intern.query
        .filter_by(is_archived=False, fte_recommendation="NO")
        .all()
    )