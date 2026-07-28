from datetime import datetime
from bson import ObjectId
from services.mongo_service import MongoService
from services.wellness.statistics_service import StatisticsService
from services.wellness.wellness_score_service import WellnessScoreService
from models.wellness.statistics_model import RecommendationFeedbackModel

class InsightsService:
    @classmethod
    def get_unified_wellness_context(cls, user_id):
        """
        Builds the unified context struct containing aggregated signals
        from all 7 modules for the AI Intelligence Engine.
        """
        summary = StatisticsService.get_summary(user_id)
        score_info = WellnessScoreService.calculate_score(user_id)

        db = MongoService.get_db()
        mood_doc = db.mood_logs.find_one({"user_id": ObjectId(user_id)})
        primary_mood = mood_doc.get("mood_label", "Neutral") if mood_doc else "Neutral"

        # Pre-evaluation heuristics
        heuristics = []
        if summary.get("sleep_hours", 7.5) < 6.0:
            heuristics.append("LOW_SLEEP_WARNING")
        if summary.get("focus_minutes", 0) > 180 and summary.get("meditation_minutes", 0) == 0:
            heuristics.append("HIGH_WORK_NO_REST")
        if primary_mood in ["Stressed", "Anxious"]:
            heuristics.append("ELEVATED_STRESS")

        return {
            "summary": summary,
            "score": score_info,
            "recent_mood": primary_mood,
            "heuristics": heuristics,
            "context_timestamp": datetime.now().isoformat()
        }

    @staticmethod
    def generate_ai_insight_summary(user_id):
        """
        Derives structured insight text and recommendation type for dashboard.
        """
        ctx = InsightsService.get_unified_wellness_context(user_id)
        heuristics = ctx["heuristics"]
        score = ctx["score"]["current"]

        if "LOW_SLEEP_WARNING" in heuristics:
            return {
                "headline": "Prioritize Rest Today",
                "summary": f"Your sleep was below optimal (score: {ctx['summary']['sleep_score']}). Gentle breathing can help reduce fatigue.",
                "recommended_action": "breathing"
            }
        elif "ELEVATED_STRESS" in heuristics:
            return {
                "headline": "Elevated Stress Detected",
                "summary": "Take a 5-minute calm break to regulate your nervous system.",
                "recommended_action": "meditation"
            }
        elif score >= 80:
            return {
                "headline": "Balanced Wellness State",
                "summary": "Your sleep, mood, and activity levels are well aligned. Great job staying consistent!",
                "recommended_action": "focus"
            }
        else:
            return {
                "headline": "Daily Reflection Invitation",
                "summary": "A 4-7-8 breathing session or quick journal check-in can help stabilize your energy.",
                "recommended_action": "breathing"
            }

    @staticmethod
    def log_recommendation_feedback(user_id, recommendation_id, recommendation_type, accepted=False, dismissed=False, helpful=False, not_helpful=False):
        db = MongoService.get_db()
        fb = RecommendationFeedbackModel(
            user_id=user_id,
            recommendation_id=recommendation_id,
            recommendation_type=recommendation_type,
            accepted=accepted,
            dismissed=dismissed,
            helpful=helpful,
            not_helpful=not_helpful
        )
        res = db.recommendation_feedback.insert_one(fb.to_dict())
        fb.id = str(res.inserted_id)
        return fb.to_dict()
