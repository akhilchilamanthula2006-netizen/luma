from flask import Blueprint, render_template, request, session
from utils.security import login_required
from .wellness_controller import WellnessController

focus_bp = Blueprint('wellness_focus', __name__)

@focus_bp.route('/focus', methods=['GET'])
@login_required
def page():
    return render_template('wellness/focus.html')

@focus_bp.route('/api/focus/presets', methods=['GET'])
@login_required
def get_presets():
    return WellnessController.get_focus_presets()

@focus_bp.route('/api/focus/session', methods=['POST'])
@login_required
def log_session():
    user_id = session.get('user_id')
    payload = request.get_json()
    return WellnessController.log_focus_session(user_id, payload)
