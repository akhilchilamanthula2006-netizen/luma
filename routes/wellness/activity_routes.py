from flask import Blueprint, request, session
from utils.security import login_required
from .wellness_controller import WellnessController

activity_bp = Blueprint('wellness_activity', __name__)

@activity_bp.route('/api/activities/log', methods=['POST'])
@login_required
def log_activity():
    user_id = session.get('user_id')
    payload = request.get_json()
    return WellnessController.log_activity(user_id, payload)
