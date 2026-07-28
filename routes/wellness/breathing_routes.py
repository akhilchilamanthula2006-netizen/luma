from flask import Blueprint, render_template, request, session
from utils.security import login_required
from .wellness_controller import WellnessController

breathing_bp = Blueprint('wellness_breathing', __name__)

@breathing_bp.route('/breathing', methods=['GET'])
@login_required
def page():
    return render_template('wellness/breathing.html')

@breathing_bp.route('/api/breathing/configs', methods=['GET'])
@login_required
def get_configs():
    return WellnessController.get_breathing_configs()

@breathing_bp.route('/api/breathing/session', methods=['POST'])
@login_required
def log_session():
    user_id = session.get('user_id')
    payload = request.get_json()
    return WellnessController.log_breathing_session(user_id, payload)
