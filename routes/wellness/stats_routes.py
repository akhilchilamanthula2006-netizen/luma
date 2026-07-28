from flask import Blueprint, render_template, request, session
from utils.security import login_required
from .wellness_controller import WellnessController

stats_bp = Blueprint('wellness_stats', __name__)

@stats_bp.route('/stats', methods=['GET'])
@login_required
def page():
    return render_template('wellness/stats.html')

@stats_bp.route('/api/timeline', methods=['GET'])
@login_required
def get_timeline():
    user_id = session.get('user_id')
    limit = int(request.args.get('limit', 30))
    return WellnessController.get_timeline(user_id, limit)

@stats_bp.route('/api/recommendations/feedback', methods=['POST'])
@login_required
def feedback():
    user_id = session.get('user_id')
    payload = request.get_json()
    return WellnessController.log_recommendation_feedback(user_id, payload)
