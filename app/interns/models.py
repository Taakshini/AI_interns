from app.extensions import db
from datetime import datetime

class Intern(db.Model):
    __tablename__ = "interns"

    id                       = db.Column(db.Integer, primary_key=True)
    intern_id                = db.Column(db.String(20), unique=True, nullable=False)
    name                     = db.Column(db.String(100), nullable=False)
    intern_type              = db.Column(db.String(50))
    paid_unpaid              = db.Column(db.String(10))
    location                 = db.Column(db.String(100))
    college_name             = db.Column(db.String(150))
    business_unit            = db.Column(db.String(100))
    line_of_service          = db.Column(db.String(100))
    date_of_joining          = db.Column(db.Date)
    duration                 = db.Column(db.String(50))
    expected_completion_date = db.Column(db.Date)
    actual_completion_date   = db.Column(db.Date)
    quarter_joined           = db.Column(db.String(20))
    quarter_converted        = db.Column(db.String(20))
    status                   = db.Column(db.String(30), default="Pursuing")
    project_associated       = db.Column(db.String(150))
    resume_link              = db.Column(db.String(255))
    evaluation_feedback      = db.Column(db.Text)
    fte_recommendation       = db.Column(db.String(5))
    created_at               = db.Column(db.DateTime, default=datetime.utcnow)

    # Archive fields
    is_archived = db.Column(db.Boolean, default=False)
    archived_at = db.Column(db.DateTime)
    archive_reason = db.Column(db.String(255))

    def archive(self, reason=""):
        """Archive this intern (soft delete)."""
        self.is_archived = True
        self.archived_at = datetime.utcnow()
        self.archive_reason = reason or "Archived by system"
        db.session.commit()

    def restore(self):
        """Restore archived intern."""
        self.is_archived = False
        self.archived_at = None
        self.archive_reason = None
        db.session.commit()

    def __repr__(self):
        return f"<Intern {self.intern_id} | {self.name} | {self.status}>"

    def to_dict(self):
        return {
            "id": self.id,
            "intern_id": self.intern_id,
            "name": self.name,
            "intern_type": self.intern_type,
            "paid_unpaid": self.paid_unpaid,
            "location": self.location,
            "college_name": self.college_name,
            "business_unit": self.business_unit,
            "line_of_service": self.line_of_service,
            "date_of_joining": str(self.date_of_joining) if self.date_of_joining else None,
            "duration": self.duration,
            "expected_completion_date": str(self.expected_completion_date) if self.expected_completion_date else None,
            "actual_completion_date": str(self.actual_completion_date) if self.actual_completion_date else None,
            "quarter_joined": self.quarter_joined,
            "quarter_converted": self.quarter_converted,
            "status": self.status,
            "project_associated": self.project_associated,
            "evaluation_feedback": self.evaluation_feedback,
            "fte_recommendation": self.fte_recommendation,
            "is_archived": self.is_archived,
            "archive_reason": self.archive_reason,
        }
    
class Attendance(db.Model):
    __tablename__ = "attendance"

    id = db.Column(db.Integer, primary_key=True)
    intern_id = db.Column(
        db.Integer,
        db.ForeignKey("interns.id"),
        nullable=False
    )

    date = db.Column(db.Date, nullable=False)

    status = db.Column(
        db.String(10),
        default="Present"
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    intern = db.relationship(
        "Intern",
        backref="attendance_records"
    )


class ProgressScore(db.Model):
    __tablename__ = "progress_scores"

    id = db.Column(db.Integer, primary_key=True)

    intern_id = db.Column(
        db.Integer,
        db.ForeignKey("interns.id"),
        nullable=False
    )

    score = db.Column(
        db.Float,
        default=100.0
    )

    consecutive_absences = db.Column(
        db.Integer,
        default=0
    )

    last_updated = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    note = db.Column(db.String(255))

    intern = db.relationship(
        "Intern",
        backref="progress"
    )