from flask import Blueprint, render_template, session, redirect, url_for, request, flash
from datetime import datetime

from services.mood_service import MoodService
from services.intelligence_service import IntelligenceService

dashboard_bp = Blueprint('dashboard', __name__, url_prefix='/dashboard')


@dashboard_bp.route('/')
def index():
    """Render the main dashboard with real wellness data."""
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))

    user_id  = session['user_id']
    username = session['username']

    latest_mood = MoodService.get_latest_mood(user_id)
    today_str   = datetime.now().strftime("%A, %B %d, %Y")

    # Compute a real wellness score + label from the latest mood.
    # Falls back to "Recovering" (score 0) when no mood has been logged yet.
    if latest_mood:
        wellness_score = IntelligenceService.compute_wellness_score(latest_mood.mood)
    else:
        wellness_score = 0

    wellness_level = IntelligenceService.wellness_label(wellness_score)

    # Static placeholder — streak will be implemented in a future milestone.
    streak_days = "3 Days"

    return render_template(
        'dashboard/index.html',
        username=username,
        today_str=today_str,
        latest_mood=latest_mood,
        streak_days=streak_days,
        wellness_level=wellness_level,
        wellness_score=wellness_score,
    )


@dashboard_bp.route('/mood', methods=['POST'])
def check_in_mood():
    """Handle an explicit manual mood check-in from the dashboard form."""
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))

    user_id = session['user_id']
    mood    = request.form.get('mood')

    if not mood:
        flash('Invalid mood selection.', 'error')
        return redirect(url_for('dashboard.index'))

    try:
        res = MoodService.log_mood(user_id=user_id, mood=mood, notes="")
        if res.get("action") == "updated":
            flash(f"Today's mood updated to {mood}!", 'success')
        else:
            flash(f"Logged your mood as {mood}. Great job checking in!", 'success')
    except Exception as e:
        flash(f"Error logging mood: {e}", 'error')

    return redirect(url_for('dashboard.index'))
