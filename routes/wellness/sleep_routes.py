from flask import Blueprint, render_template, request, session
from utils.security import login_required
from .wellness_controller import WellnessController

sleep_bp = Blueprint('wellness_sleep', __name__)

@sleep_bp.route('/sleep', methods=['GET'])
@login_required
def page():
    return render_template('wellness/sleep.html')

@sleep_bp.route('/api/sleep/log', methods=['POST'])
@login_required
def log_sleep():
    user_id = session.get('user_id')
    payload = request.get_json()
    return WellnessController.log_sleep(user_id, payload)

@sleep_bp.route('/api/sleep/history', methods=['GET'])
@login_required
def get_history():
    user_id = session.get('user_id')
    days = int(request.args.get('days', 30))
    return WellnessController.get_sleep_history(user_id, days)
