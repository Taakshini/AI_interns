from app.interns.models import Intern

def analyze_intern_feedback(intern: Intern):
    """
    Local rule-based analysis (no API calls).
    """
    feedback = (intern.evaluation_feedback or "").lower()
    
    strengths = []
    weaknesses = []
    
    # Strengths detection
    strength_keywords = {
        "proactive": "Takes initiative",
        "quick learner": "Fast learner",
        "excellent": "High quality work",
        "strong": "Strong skills",
        "motivated": "Self-motivated",
        "collaborative": "Great teamwork",
        "creative": "Innovative thinking",
    }
    
    for keyword, strength in strength_keywords.items():
        if keyword in feedback:
            strengths.append(strength)
    
    # Weaknesses detection
    weakness_keywords = {
        "slow": "Needs to work faster",
        "struggle": "Struggling with some tasks",
        "improvement": "Room for improvement",
        "weak": "Needs skill development",
        "late": "Time management issues",
        "communication": "Communication could improve",
    }
    
    for keyword, weakness in weakness_keywords.items():
        if keyword in feedback:
            weaknesses.append(weakness)
    
    # Fallback if no keywords match
    if not strengths:
        strengths = ["Good fundamentals", "Reliable", "Willing to learn"]
    if not weaknesses:
        weaknesses = ["Minimal areas", "Generally solid", "Continuing to grow"]
    
    # Build response
    result = "<b>Strengths:</b><br/>"
    for s in strengths[:3]:
        result += f"• {s}<br/>"
    
    result += "<br/><b>Areas for Improvement:</b><br/>"
    for w in weaknesses[:3]:
        result += f"• {w}<br/>"
    
    return result

def predict_conversion(intern: Intern):
    """
    Local prediction (no API calls).
    Based on simple rules.
    """
    probability = 50  # Base probability
    reasoning = "Neutral assessment"
    
    # Rule 1: Status
    if intern.status == "Pursuing":
        probability += 15
        reasoning = "Currently active in program"
    elif intern.status == "Relieved":
        probability -= 10
        reasoning = "Already completed/left"
    
    # Rule 2: FTE Recommendation
    if intern.fte_recommendation == "YES":
        probability += 25
        reasoning = "Strong FTE recommendation"
    elif intern.fte_recommendation == "NO":
        probability -= 20
        reasoning = "Not recommended for conversion"
    
    # Rule 3: Type
    if "student" in (intern.intern_type or "").lower():
        probability += 10
        reasoning = "Student intern — higher potential"
    
    # Rule 4: Paid vs Unpaid
    if intern.paid_unpaid == "Paid":
        probability += 5
        reasoning = "Paid position — company invested"
    
    # Rule 5: Feedback sentiment
    if intern.evaluation_feedback:
        feedback = intern.evaluation_feedback.lower()
        if any(word in feedback for word in ["excellent", "great", "strong", "very good"]):
            probability += 10
        if any(word in feedback for word in ["weak", "struggle", "poor", "difficulty"]):
            probability -= 10
    
    # Clamp between 0-100
    probability = max(0, min(100, probability))
    
    return {"probability": probability, "reasoning": reasoning}

def recommend_tasks(intern: Intern, available_tasks=None):
    """
    Local task recommendation (no API calls).
    Based on feedback keywords.
    """
    if available_tasks is None:
        available_tasks = {
            "Backend API": ["python", "api", "backend", "server"],
            "Database": ["sql", "database", "data", "db"],
            "Frontend": ["react", "javascript", "ui", "frontend"],
            "Data Analysis": ["data", "analytics", "analysis", "pandas"],
            "DevOps": ["deployment", "docker", "cloud", "infrastructure"],
        }
    
    feedback = (intern.evaluation_feedback or "").lower()
    matched_tasks = []
    
    # Score each task based on skill keywords
    for task_name, keywords in available_tasks.items():
        score = sum(1 for kw in keywords if kw in feedback)
        if score > 0:
            matched_tasks.append((task_name, score))
    
    # Sort and get top 2
    matched_tasks.sort(key=lambda x: x[1], reverse=True)
    top_2 = matched_tasks[:2] if matched_tasks else [("General Project", 1)]
    
    # Format response
    result = ""
    for i, (task, _) in enumerate(top_2, 1):
        result += f"<b>Task {i}:</b> {task} | "
    
    if not result:
        result = "<b>Task 1:</b> Backend Development | <b>Task 2:</b> General Project "
    
    return result

def generate_cohort_summary(interns: list):
    """
    Local cohort summary (no API calls).
    Based on statistics.
    """
    if not interns:
        return "No interns in cohort."
    
    total = len(interns)
    pursuing = len([i for i in interns if i.status == "Pursuing"])
    relieved = len([i for i in interns if i.status == "Relieved"])
    fte_yes = len([i for i in interns if i.fte_recommendation == "YES"])
    fte_no = len([i for i in interns if i.fte_recommendation == "NO"])
    conversion_rate = round(fte_yes / total * 100) if total > 0 else 0
    
    # Generate summary based on metrics
    health = "Strong" if conversion_rate > 60 else "Moderate" if conversion_rate > 40 else "Needs attention"
    
    summary = f"""
    <b>Cohort Health: {health}</b><br/>
    The cohort of {total} interns shows a {conversion_rate}% conversion rate ({fte_yes} recommended for hire).
    Currently, {pursuing} interns are pursuing their internships, with {relieved} having completed.
    The program demonstrates solid performance with focus on quality hiring decisions.
    """
    
    return summary