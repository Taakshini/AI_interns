from app.interns.models import Intern
from sqlalchemy import func

def calculate_college_performance():
    """Analyze conversion rate by college."""
    interns = Intern.query.all()
    college_stats = {}
    
    for intern in interns:
        college = intern.college_name or "Unknown"
        if college not in college_stats:
            college_stats[college] = {"total": 0, "yes": 0, "no": 0}
        
        college_stats[college]["total"] += 1
        if intern.fte_recommendation == "YES":
            college_stats[college]["yes"] += 1
        else:
            college_stats[college]["no"] += 1
    
    # Calculate conversion rate
    for college, stats in college_stats.items():
        total = stats["total"]
        stats["conversion_rate"] = round((stats["yes"] / total * 100) if total > 0 else 0, 1)
    
    # Sort by conversion rate
    sorted_colleges = sorted(college_stats.items(), 
                            key=lambda x: x[1]["conversion_rate"], 
                            reverse=True)
    
    return dict(sorted_colleges[:10])  # Top 10 colleges

def calculate_department_performance():
    """Analyze performance by business unit/department."""
    interns = Intern.query.all()
    dept_stats = {}
    
    for intern in interns:
        dept = intern.business_unit or "Unassigned"
        if dept not in dept_stats:
            dept_stats[dept] = {"total": 0, "yes": 0, "no": 0}
        
        dept_stats[dept]["total"] += 1
        if intern.fte_recommendation == "YES":
            dept_stats[dept]["yes"] += 1
        else:
            dept_stats[dept]["no"] += 1
    
    for dept, stats in dept_stats.items():
        total = stats["total"]
        stats["conversion_rate"] = round((stats["yes"] / total * 100) if total > 0 else 0, 1)
    
    sorted_depts = sorted(dept_stats.items(), 
                         key=lambda x: x[1]["conversion_rate"], 
                         reverse=True)
    
    return dict(sorted_depts)

def identify_at_risk_interns():
    """Flag interns likely to not convert."""
    at_risk = []
    interns = Intern.query.filter_by(is_archived=False).all()  # ← ADD THIS FILTER

    
    interns = Intern.query.all()
    for intern in interns:
        risk_score = 0
        risk_reasons = []
        
        # Risk factor 1: FTE NO
        if intern.fte_recommendation == "NO":
            risk_score += 50
            risk_reasons.append("Not recommended for FTE")
        
        # Risk factor 2: Relieved status
        if intern.status == "Relieved":
            risk_score += 30
            risk_reasons.append("Internship ended without conversion")
        
        # Risk factor 3: Negative feedback keywords
        feedback = (intern.evaluation_feedback or "").lower()
        if any(word in feedback for word in ["weak", "poor", "struggle", "difficulty", "slow"]):
            risk_score += 20
            risk_reasons.append("Feedback indicates performance concerns")
        
        if risk_score >= 50:
            at_risk.append({
                "intern_id": intern.intern_id,
                "name": intern.name,
                "college": intern.college_name,
                "status": intern.status,
                "fte": intern.fte_recommendation,
                "risk_score": min(100, risk_score),
                "risk_reasons": risk_reasons,
            })
    
    return sorted(at_risk, key=lambda x: x["risk_score"], reverse=True)

def generate_hiring_scores():
    """Generate 0-100 hiring recommendation scores."""
    interns = Intern.query.all()
    scores = []
    
    interns = Intern.query.filter_by(is_archived=False).all()  # ← ADD THIS FILTER

    for intern in interns:
        score = 50  # Base score
        
        # FTE Recommendation (0-30 points)
        if intern.fte_recommendation == "YES":
            score += 30
        elif intern.fte_recommendation == "NO":
            score -= 15
        
        # Status (0-20 points)
        if intern.status == "Pursuing":
            score += 15
        elif intern.status == "Relieved":
            score += 5  # Less favorable but not negative
        
        # Internship Type (0-15 points)
        if "student" in (intern.intern_type or "").lower():
            score += 10
        
        # Paid vs Unpaid (0-15 points)
        if intern.paid_unpaid == "Paid":
            score += 15
        
        # Feedback sentiment (0-20 points)
        feedback = (intern.evaluation_feedback or "").lower()
        positive_words = ["excellent", "great", "strong", "very good", "outstanding"]
        negative_words = ["weak", "poor", "struggle", "difficulty"]
        
        positive_count = sum(1 for word in positive_words if word in feedback)
        negative_count = sum(1 for word in negative_words if word in feedback)
        
        score += (positive_count * 5)
        score -= (negative_count * 5)
        
        # Clamp score
        score = max(0, min(100, score))
        
        # Generate recommendation
        if score >= 85:
            recommendation = "Strongly Recommend"
            color = "green"
        elif score >= 70:
            recommendation = "Recommend"
            color = "lightgreen"
        elif score >= 50:
            recommendation = "Consider"
            color = "yellow"
        else:
            recommendation = "Do Not Recommend"
            color = "red"
        
        scores.append({
            "intern_id": intern.intern_id,
            "name": intern.name,
            "college": intern.college_name,
            "score": score,
            "recommendation": recommendation,
            "color": color,
        })
    
    return sorted(scores, key=lambda x: x["score"], reverse=True)

def predict_next_cohort_conversion():
    """Predict conversion rate for future cohorts."""
    interns = Intern.query.all()
    if not interns:
        return 50
    
    total = len(interns)
    fte_yes = len([i for i in interns if i.fte_recommendation == "YES"])
    current_rate = (fte_yes / total * 100) if total > 0 else 0
    
    # Simple prediction: trending +5% improvement based on system maturity
    predicted_rate = min(95, current_rate + 5)
    
    return round(predicted_rate, 1)

def get_cohort_insights():
    """Generate key insights for the cohort."""
    interns = Intern.query.all()
    
    if not interns:
        return {
            "total": 0,
            "insights": ["No interns to analyze"]
        }
    
    colleges = calculate_college_performance()
    departments = calculate_department_performance()
    at_risk = identify_at_risk_interns()
    
    top_college = list(colleges.keys())[0] if colleges else "Unknown"
    top_college_rate = colleges.get(top_college, {}).get("conversion_rate", 0) if colleges else 0
    
    top_dept = list(departments.keys())[0] if departments else "Unknown"
    top_dept_rate = departments.get(top_dept, {}).get("conversion_rate", 0) if departments else 0
    
    insights = []
    
    # Insight 1: Top college
    insights.append(f"🎓 {top_college} leads with {top_college_rate}% conversion rate")
    
    # Insight 2: Top department
    if top_dept != "Unassigned":
        insights.append(f"🏢 {top_dept} shows strongest performance ({top_dept_rate}%)")
    
    # Insight 3: At-risk count
    if at_risk:
        insights.append(f"⚠️ {len(at_risk)} interns flagged as at-risk, need mentoring intervention")
    
    # Insight 4: Overall health
    total = len(interns)
    fte_yes = len([i for i in interns if i.fte_recommendation == "YES"])
    conversion = round((fte_yes / total * 100) if total > 0 else 0, 1)
    insights.append(f"📊 Overall cohort health: {conversion}% conversion rate")
    
    return {
        "total_interns": total,
        "insights": insights,
    }