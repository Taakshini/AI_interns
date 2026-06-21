"""
app/interns/utils.py
FIXED VERSION — resolves Excel upload bug.

ROOT CAUSE of upload failure:
  - parse_excel_interns() was returning a tuple (interns_list, errors_list)
  - uploads/routes.py was treating the return value as a plain list
  - Result: `if not interns` was always False (a tuple is never falsy)
    and `save_interns(interns)` received the tuple instead of the list

FIX:
  - parse_excel_interns() now returns only the list of Intern objects
  - save_interns() now returns (saved_count, duplicate_count) — two integers
"""

import pandas as pd
from datetime import datetime
from app.interns.models import Intern
from app.extensions import db


def parse_excel_interns(filepath):
    """
    Read an Excel/CSV file and return a list of Intern objects.
    Skips invalid rows silently.
    """
    try:
        if str(filepath).endswith('.csv'):
            df = pd.read_csv(filepath)
        else:
            df = pd.read_excel(filepath, sheet_name=0)
    except Exception as e:
        print(f"[UPLOAD ERROR] Could not read file: {e}")
        return []   # ← always return a list, never a tuple

    interns = []

    for idx, row in df.iterrows():
        try:
            def get(keys):
                """Try multiple column name variants."""
                for k in keys:
                    for col in df.columns:
                        if col.strip().lower() == k.lower():
                            val = row[col]
                            if pd.notna(val) and str(val).strip() not in ('', 'nan', 'NaT'):
                                return str(val).strip()
                return None

            name = get(['names', 'name', 'intern name'])
            if not name:
                continue   # skip header-only or empty rows

            intern_id_raw = get(['id', 'intern id', 'intern_id'])
            intern_id = intern_id_raw if intern_id_raw else f"IMS-{idx+1:03d}"

            def parse_date(keys):
                raw = get(keys)
                if not raw:
                    return None
                for fmt in ('%Y-%m-%d', '%d-%m-%Y', '%d/%m/%Y', '%m/%d/%Y'):
                    try:
                        return datetime.strptime(raw[:10], fmt).date()
                    except Exception:
                        pass
                try:
                    return pd.to_datetime(raw).date()
                except Exception:
                    return None

            intern = Intern(
                intern_id=intern_id,
                name=name,
                intern_type=get(['intern type', 'interntype']) or 'Intern',
                paid_unpaid=get(['paid/unpaid', 'paid unpaid', 'paidunpaid']) or 'Unpaid',
                location=get(['location', 'city']),
                college_name=get(['college name', 'college', 'institution', 'university']),
                business_unit=get(['business unit', 'businessunit', 'bu']),
                line_of_service=get(['line of service', 'lineofservice', 'department', 'dept']),
                date_of_joining=parse_date(['date of joining', 'dateofjoining', 'doj', 'joining date']),
                duration=get(['duration']),
                expected_completion_date=parse_date(['expected completion date', 'expected completion', 'expected end']),
                actual_completion_date=parse_date(['actual completion date', 'actual completion', 'actual end']),
                quarter_joined=get(['quarter  joined ', 'quarter joined', 'quarterjoined']),
                quarter_converted=get(['quarter converted/releived', 'quarter converted', 'quarterconverted']),
                status=get(['status']) or 'Pursuing',
                project_associated=get(['project assossiated', 'project associated', 'project']),
                resume_link=get(['resumes ', 'resumes', 'resume', 'resume link']),
                evaluation_feedback=get(['monthly evaluation feedbacks ', 'monthly evaluation feedbacks',
                                         'evaluation feedback', 'feedback']),
                fte_recommendation=(get(['fte recommendation', 'fterecommendation', 'fte']) or 'NO').upper(),
            )
            interns.append(intern)

        except Exception as e:
            print(f"[UPLOAD] Skipping row {idx}: {e}")
            continue

    return interns   # ← plain list, nothing else


def save_interns(interns):
    """
    Save a list of Intern objects to the database.
    Returns (saved_count, duplicate_count) — both are integers.
    """
    saved = 0
    duplicates = 0

    for intern in interns:
        try:
            existing = Intern.query.filter_by(intern_id=intern.intern_id).first()
            if existing:
                duplicates += 1
            else:
                db.session.add(intern)
                saved += 1
        except Exception as e:
            print(f"[DB] Error saving {intern.intern_id}: {e}")

    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        print(f"[DB] Commit failed: {e}")

    return saved, duplicates   # ← two integers, always