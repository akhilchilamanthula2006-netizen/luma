from flask import Blueprint, render_template, session, redirect, url_for

journal_bp = Blueprint('journal', __name__, url_prefix='/journal')

@journal_bp.route('/')
def index():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    return render_template('journal/index.html')
