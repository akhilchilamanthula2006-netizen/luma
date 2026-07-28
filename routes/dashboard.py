import logging
from flask import Blueprint, render_template, session, redirect, url_for, request, flash
from datetime import datetime

from services.mood_service import MoodService
from services.journal_service import JournalService
from services.intelligence_service import IntelligenceService
from services.wellness_service import WellnessService
from models.mood_model import MoodModel

logger = logging.getLogger(__name__)

dashboard_bp = Blueprint('dashboard', __name__, url_prefix='/dashboard')

# Fallback wellness summary used when MongoDB is unavailable
_WELLNESS_FALLBACK = {
    "wellness_score": {"current": 0, "label": "Recovering", "components": {}},
    "sleep_score":    {"current": 80, "last_night_hours": 7.5, "quality_label": "Restful"},
    "mood_trend":     {"primary_mood_7d": 75, "sentiment_direction": "stable"},
    "ai_insight":     None,
    "current_streak": {"days": 1, "active_today": False},
    "today_activities": [],
    "wellness_summary": {"breathing_mins": 0, "meditation_mins": 0, "focus_mins": 0, "music_mins": 0},
}


@dashboard_bp.route('/')
def index():
    """Render the main dashboard with real wellness data."""
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))

    user_id  = session['user_id']
    username = session['username']

    all_journals    = JournalService.list_entries(user_id)
    recent_journals = all_journals[:3]
    latest_mood     = MoodService.get_latest_mood(user_id)
    today_str       = datetime.now().strftime("%A, %B %d, %Y")

    # ── Single centralized wellness call (safe fallback on error) ────────────
    try:
        wellness_data = WellnessService.get_dashboard_summary(user_id)
    except Exception as exc:
        logger.warning("WellnessService.get_dashboard_summary failed for %s: %s", user_id, exc)
        wellness_data = _WELLNESS_FALLBACK.copy()

    # ── Prefer journal-derived mood when newer than the stored mood log ───────
    if all_journals:
        latest_journal = all_journals[0]
        journal_mood = (
            latest_journal.emotion_snapshot.get("primary_mood")
            if latest_journal.emotion_snapshot else None
        )
        if journal_mood:
            journal_ts = latest_journal.updated_at or latest_journal.created_at
            if not latest_mood or (
                journal_ts and latest_mood.timestamp and journal_ts > latest_mood.timestamp
            ):
                latest_mood = MoodModel(
                    user_id=user_id,
                    mood=journal_mood,
                    score=IntelligenceService.compute_wellness_score(journal_mood),
                    source="journal",
                    timestamp=journal_ts,
                    notes=latest_journal.emotion_snapshot.get("emotion_reason", ""),
                )

    wellness_score = wellness_data["wellness_score"]["current"]
    wellness_level = wellness_data["wellness_score"]["label"]
    streak_days    = f"{wellness_data['current_streak']['days']} Days"

    return render_template(
        'dashboard/index.html',
        username=username,
        today_str=today_str,
        latest_mood=latest_mood,
        recent_journals=recent_journals,
        streak_days=streak_days,
        wellness_level=wellness_level,
        wellness_score=wellness_score,
        wellness_summary=wellness_data,
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
    except Exception as exc:
        flash(f"Error logging mood: {exc}", 'error')

    return redirect(url_for('dashboard.index'))
