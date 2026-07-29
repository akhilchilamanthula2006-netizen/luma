import logging
from flask import Blueprint, render_template, session, redirect, url_for, jsonify
from utils.security import login_required
from services.wellness_service import WellnessService
from services.wellness.statistics_service import StatisticsService
from services.wellness.insights_service import InsightsService

logger = logging.getLogger(__name__)

analytics_bp = Blueprint('analytics', __name__, url_prefix='/analytics')


@analytics_bp.route('/')
@login_required
def index():
    """Render the responsive Analytics page with real wellness data."""
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))

    user_id = session['user_id']
    username = session.get('username', 'User')

    try:
        summary_data = WellnessService.get_dashboard_summary(user_id)
        analytics = StatisticsService.get_7day_analytics(user_id)
        ai_summary = InsightsService.generate_weekly_ai_summary(user_id)
        timeline = StatisticsService.get_unified_timeline(user_id, limit=15)
    except Exception as exc:
        logger.error("Failed to load analytics for user %s: %s", user_id, exc)
        summary_data = {
            "wellness_score": {"current": 0, "label": "--"},
            "sleep_score": {"current": 0, "last_night_hours": 0.0},
            "current_streak": {"days": 0}
        }
        analytics = {
            "has_data": False,
            "is_demo": False,
            "day_labels": ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"],
            "wellness_scores": [0, 0, 0, 0, 0, 0, 0],
            "sleep_hours": [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
            "meditation_mins": [0, 0, 0, 0, 0, 0, 0],
            "breathing_mins": [0, 0, 0, 0, 0, 0, 0],
            "focus_mins": [0, 0, 0, 0, 0, 0, 0],
            "mood_counts": {},
            "activity_distribution": {},
            "total_weekly_activities": 0
        }
        ai_summary = {
            "has_data": False,
            "overall_progress": "",
            "positive_habits": [],
            "areas_for_attention": [],
            "recommendations": []
        }
        timeline = []

    return render_template(
        'analytics/index.html',
        username=username,
        summary=summary_data,
        analytics=analytics,
        ai_summary=ai_summary,
        timeline=timeline
    )


@analytics_bp.route('/api/data', methods=['GET'])
@login_required
def get_analytics_api():
    """API endpoint returning structured analytics JSON for dynamic updates."""
    if 'user_id' not in session:
        return jsonify({"success": False, "error": "Unauthorized"}), 401

    user_id = session['user_id']
    try:
        summary_data = WellnessService.get_dashboard_summary(user_id)
        analytics = StatisticsService.get_7day_analytics(user_id)
        ai_summary = InsightsService.generate_weekly_ai_summary(user_id)
        timeline = StatisticsService.get_unified_timeline(user_id, limit=15)
        return jsonify({
            "success": True,
            "data": {
                "summary": summary_data,
                "analytics": analytics,
                "ai_summary": ai_summary,
                "timeline": timeline
            }
        })
    except Exception as exc:
        logger.error("Analytics API error for user %s: %s", user_id, exc)
        return jsonify({"success": False, "error": str(exc)}), 500
