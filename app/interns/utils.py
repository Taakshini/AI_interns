import pandas as pd
from app.interns.models import Intern
from app.extensions import db
from datetime import datetime

def parse_excel_interns(filepath):
    """
    Read Excel file and return list of Intern objects.
    Validates data before creation.
    """
    try:
        df = pd.read_excel(filepath, sheet_name=0)
        interns = []
        errors = []
        
        for idx, row in df.iterrows():
            try:
                # Map Excel columns to model fields
                intern = Intern(
                    intern_id=str(row.get('ID', f'INT-{idx}')).strip(),
                    name=str(row.get('Names', '')).strip(),
                    intern_type=str(row.get('INTERN TYPE', '')).strip(),
                    paid_unpaid=str(row.get('Paid/Unpaid', '')).strip(),
                    location=str(row.get('Location', '')).strip() if pd.notna(row.get('Location')) else None,
                    college_name=str(row.get('College Name', '')).strip() if pd.notna(row.get('College Name')) else None,
                    business_unit=str(row.get('Business Unit', '')).strip() if pd.notna(row.get('Business Unit')) else None,
                    line_of_service=str(row.get('Line of Service', '')).strip() if pd.notna(row.get('Line of Service')) else None,
                    date_of_joining=pd.to_datetime(row.get('DATE OF JOINING')).date() if pd.notna(row.get('DATE OF JOINING')) else None,
                    duration=str(row.get('DURATION', '')).strip() if pd.notna(row.get('DURATION')) else None,
                    expected_completion_date=pd.to_datetime(row.get('Expected Completion Date')).date() if pd.notna(row.get('Expected Completion Date')) else None,
                    actual_completion_date=pd.to_datetime(row.get('Actual Completion Date')).date() if pd.notna(row.get('Actual Completion Date')) else None,
                    quarter_joined=str(row.get('QUARTER  Joined ', '')).strip() if pd.notna(row.get('QUARTER  Joined ')) else None,
                    quarter_converted=str(row.get('QUARTER CONVERTED/RELEIVED', '')).strip() if pd.notna(row.get('QUARTER CONVERTED/RELEIVED')) else None,
                    status=str(row.get('STATUS', 'Pursuing')).strip(),
                    project_associated=str(row.get('PROJECT ASSOSSIATED', '')).strip() if pd.notna(row.get('PROJECT ASSOSSIATED')) else None,
                    resume_link=str(row.get('RESUMES ', '')).strip() if pd.notna(row.get('RESUMES ')) else None,
                    evaluation_feedback=str(row.get('Monthly Evaluation feedbacks ', '')).strip() if pd.notna(row.get('Monthly Evaluation feedbacks ')) else None,
                    fte_recommendation=str(row.get('FTE RECOMMENDATION', 'NO')).strip().upper(),
                )
                
                interns.append(intern)
            except Exception as e:
                errors.append(f"Row {idx + 1}: {str(e)}")
        
        return interns, errors
    
    except Exception as e:
        return [], [f"File read error: {str(e)}"]

def save_interns(interns):
    """
    Save list of Intern objects to database.
    Returns (count, errors).
    """
    errors = []
    saved = 0
    
    for intern in interns:
        try:
            # Check if already exists
            existing = Intern.query.filter_by(intern_id=intern.intern_id).first()
            if not existing:
                db.session.add(intern)
                saved += 1
        except Exception as e:
            errors.append(f"Save error for {intern.intern_id}: {str(e)}")
    
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        errors.append(f"Commit error: {str(e)}")
    
    return saved, errors