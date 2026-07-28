from flask import Blueprint, session, render_template, request
from utils.security import login_required
from .wellness_controller import WellnessController

wellness_bp = Blueprint('wellness', __name__, url_prefix='/wellness')

# ── Main Hub & Summary ──
@wellness_bp.route('/', methods=['GET'])
@login_required
def index():
    user_id = session.get('user_id')
    summary_data = WellnessController.get_dashboard_summary(user_id)[0].json.get("data", {})
    return render_template('wellness/hub.html', summary=summary_data)

@wellness_bp.route('/api/dashboard/summary', methods=['GET'])
@login_required
def api_dashboard_summary():
    user_id = session.get('user_id')
    return WellnessController.get_dashboard_summary(user_id)

# ── Breathing ──
@wellness_bp.route('/breathing', methods=['GET'])
@login_required
def breathing_page():
    return render_template('wellness/breathing.html')

@wellness_bp.route('/api/breathing/configs', methods=['GET'])
@login_required
def get_breathing_configs():
    return WellnessController.get_breathing_configs()

@wellness_bp.route('/api/breathing/session', methods=['POST'])
@login_required
def log_breathing_session():
    user_id = session.get('user_id')
    payload = request.get_json()
    return WellnessController.log_breathing_session(user_id, payload)

# ── Meditation ──
@wellness_bp.route('/meditation', methods=['GET'])
@login_required
def meditation_page():
    return render_template('wellness/meditation.html')

@wellness_bp.route('/api/meditation/session', methods=['POST'])
@login_required
def log_meditation_session():
    user_id = session.get('user_id')
    payload = request.get_json()
    return WellnessController.log_meditation_session(user_id, payload)

# ── Focus ──
@wellness_bp.route('/focus', methods=['GET'])
@login_required
def focus_page():
    return render_template('wellness/focus.html')

@wellness_bp.route('/api/focus/presets', methods=['GET'])
@login_required
def get_focus_presets():
    return WellnessController.get_focus_presets()

@wellness_bp.route('/api/focus/session', methods=['POST'])
@login_required
def log_focus_session():
    user_id = session.get('user_id')
    payload = request.get_json()
    return WellnessController.log_focus_session(user_id, payload)

# ── Music ──
@wellness_bp.route('/music', methods=['GET'])
@login_required
def music_page():
    return render_template('wellness/music.html')

@wellness_bp.route('/api/music/tracks', methods=['GET'])
@login_required
def get_music_tracks():
    category = request.args.get('category')
    return WellnessController.get_music_catalog(category)

@wellness_bp.route('/api/music/history', methods=['POST'])
@login_required
def log_music_history():
    user_id = session.get('user_id')
    payload = request.get_json()
    return WellnessController.log_music_history(user_id, payload)

# ── Sleep ──
@wellness_bp.route('/sleep', methods=['GET'])
@login_required
def sleep_page():
    return render_template('wellness/sleep.html')

@wellness_bp.route('/api/sleep/log', methods=['POST'])
@login_required
def log_sleep():
    user_id = session.get('user_id')
    payload = request.get_json()
    return WellnessController.log_sleep(user_id, payload)

@wellness_bp.route('/api/sleep/history', methods=['GET'])
@login_required
def get_sleep_history():
    user_id = session.get('user_id')
    days = int(request.args.get('days', 30))
    return WellnessController.get_sleep_history(user_id, days)

# ── Activity ──
@wellness_bp.route('/api/activities/log', methods=['POST'])
@login_required
def log_activity():
    user_id = session.get('user_id')
    payload = request.get_json()
    return WellnessController.log_activity(user_id, payload)

# ── Stats & Timeline ──
@wellness_bp.route('/stats', methods=['GET'])
@login_required
def stats_page():
    return render_template('wellness/stats.html')

@wellness_bp.route('/api/timeline', methods=['GET'])
@login_required
def get_timeline():
    user_id = session.get('user_id')
    limit = int(request.args.get('limit', 30))
    return WellnessController.get_timeline(user_id, limit)

@wellness_bp.route('/api/recommendations/feedback', methods=['POST'])
@login_required
def feedback():
    user_id = session.get('user_id')
    payload = request.get_json()
    return WellnessController.log_recommendation_feedback(user_id, payload)


