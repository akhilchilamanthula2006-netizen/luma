from flask import Blueprint, render_template, request, session
from utils.security import login_required
from .wellness_controller import WellnessController

meditation_bp = Blueprint('wellness_meditation', __name__)

@meditation_bp.route('/meditation', methods=['GET'])
@login_required
def page():
    return render_template('wellness/meditation.html')

@meditation_bp.route('/api/meditation/session', methods=['POST'])
@login_required
def log_session():
    user_id = session.get('user_id')
    payload = request.get_json()
    return WellnessController.log_meditation_session(user_id, payload)
