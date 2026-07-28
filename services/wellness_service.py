from services.wellness.breathing_service import BreathingService
from services.wellness.meditation_service import MeditationService
from services.wellness.focus_service import FocusService
from services.wellness.music_service import MusicService
from services.wellness.sleep_service import SleepService
from services.wellness.activity_service import ActivityService
from services.wellness.wellness_score_service import WellnessScoreService
from services.wellness.statistics_service import StatisticsService
from services.wellness.insights_service import InsightsService

class WellnessService:
    """
    Unified Facade Service for the Wellness Hub.
    Provides a single entry point for dashboard summaries, timeline queries,
    and sub-service delegation.
    """

    @staticmethod
    def get_dashboard_summary(user_id):
        score_data = WellnessScoreService.calculate_score(user_id)
        summary = StatisticsService.get_summary(user_id)
        ai_insight = InsightsService.generate_ai_insight_summary(user_id)
        activities = ActivityService.get_daily_activities(user_id)

        return {
            "wellness_score": {
                "current": score_data["current"],
                "label": score_data["label"],
                "components": score_data["components"]
            },
            "sleep_score": {
                "current": summary.get("sleep_score", 80),
                "last_night_hours": summary.get("sleep_hours", 7.5),
                "quality_label": "Restful" if summary.get("sleep_score", 80) >= 75 else "Moderate"
            },
            "mood_trend": {
                "primary_mood_7d": score_data.get("components", {}).get("mood_score", 75),
                "sentiment_direction": "stable"
            },
            "ai_insight": ai_insight,
            "current_streak": {
                "days": summary.get("streak_count", 1),
                "active_today": True
            },
            "today_activities": activities,
            "wellness_summary": {
                "breathing_mins": summary.get("breathing_minutes", 0),
                "meditation_mins": summary.get("meditation_minutes", 0),
                "focus_mins": summary.get("focus_minutes", 0),
                "music_mins": summary.get("music_minutes", 0)
            }
        }

    @staticmethod
    def get_activities():
        """Legacy helper for backward compatibility."""
        return [
            {"id": "breath_1", "type": "breathing", "title": "Box Breathing", "duration": "5 min"},
            {"id": "med_1", "type": "meditation", "title": "Mindful Calm", "duration": "10 min"}
        ]

