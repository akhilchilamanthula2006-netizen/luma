from flask import Blueprint, render_template, session, redirect, url_for

wellness_bp = Blueprint('wellness', __name__, url_prefix='/wellness')

@wellness_bp.route('/')
def index():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    return render_template('wellness/index.html')
