"""
setup_users.py
Run this ONCE after every fresh database migration to create login users.

Usage (from your project root):
    python setup_users.py
"""

from app import create_app
from app.extensions import db
from app.auth.models import User

app = create_app()

with app.app_context():
    # Wipe any broken/old user rows
    try:
        User.query.delete()
        db.session.commit()
        print("✅ Old users cleared")
    except Exception as e:
        db.session.rollback()
        print(f"⚠️  Could not clear users (probably empty already): {e}")

    # Admin account
    admin = User(
        username="admin",
        email="admin@ims.local",
        role="admin",
        is_active=True,
    )
    admin.set_password("admin123")
    db.session.add(admin)

    # HR account
    hr = User(
        username="hr",
        email="hr@ims.local",
        role="hr",
        is_active=True,
    )
    hr.set_password("hr123")
    db.session.add(hr)

    db.session.commit()

    print("\n✅ Users created successfully!\n")
    print("  ┌──────────────────────────────┬───────────┬───────┐")
    print("  │ Email                        │ Password  │ Role  │")
    print("  ├──────────────────────────────┼───────────┼───────┤")
    print("  │ admin@ims.local              │ admin123  │ admin │")
    print("  │ hr@ims.local                 │ hr123     │ hr    │")
    print("  └──────────────────────────────┴───────────┴───────┘")
    print("\nNow run:  python run.py")
    print("Login at: http://127.0.0.1:5000/login\n")