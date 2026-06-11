from flask import Blueprint

# ✅ Create the blueprint FIRST
auth_bp = Blueprint("auth", __name__)

# Then use it below
@auth_bp.route("/login")
def login():
    return "Login page coming soon"

@auth_bp.route("/logout")
def logout():
    return "Logout coming soon"

@auth_bp.route("/register")
def register():
    return "Register coming soon"