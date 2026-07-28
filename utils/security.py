from functools import wraps
from flask import session, redirect, url_for, jsonify, request
from werkzeug.security import generate_password_hash, check_password_hash

def hash_password(password: str) -> str:
    """Hashes a plaintext password."""
    return generate_password_hash(password)

def verify_password(password_hash: str, password: str) -> bool:
    """Verifies a password against its hash."""
    return check_password_hash(password_hash, password)

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            if request.path.startswith('/wellness/api/') or request.is_json:
                return jsonify({"success": False, "data": None, "error": "Unauthorized"}), 401
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

