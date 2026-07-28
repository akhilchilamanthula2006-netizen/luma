from flask import Blueprint, render_template, request, session
from utils.security import login_required
from .wellness_controller import WellnessController

music_bp = Blueprint('wellness_music', __name__)

@music_bp.route('/music', methods=['GET'])
@login_required
def page():
    return render_template('wellness/music.html')

@music_bp.route('/api/music/tracks', methods=['GET'])
@login_required
def get_tracks():
    category = request.args.get('category')
    return WellnessController.get_music_catalog(category)

@music_bp.route('/api/music/history', methods=['POST'])
@login_required
def log_history():
    user_id = session.get('user_id')
    payload = request.get_json()
    return WellnessController.log_music_history(user_id, payload)
