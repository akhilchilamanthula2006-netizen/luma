from flask import Blueprint, render_template, session, redirect, url_for

chat_bp = Blueprint('chat', __name__, url_prefix='/chat')

@chat_bp.route('/')
def index():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    return render_template('chat/index.html')
