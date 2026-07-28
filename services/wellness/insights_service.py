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
    def generate_weekly_ai_summary(user_id):
        """
        Generates structured AI Weekly Summary containing:
        - overall_progress
        - positive_habits
        - areas_for_attention
        - recommendations
        """
        ctx = InsightsService.get_unified_wellness_context(user_id)
        analytics = StatisticsService.get_7day_analytics(user_id)
        score = ctx["score"]["current"]
        heuristics = ctx["heuristics"]
        summary = ctx["summary"]

        # Progress assessment
        if score >= 80:
            overall_progress = "Outstanding momentum! Your wellness markers, sleep quality, and active streak demonstrate strong emotional equilibrium."
        elif score >= 65:
            overall_progress = "Steady and stable progress over the last 7 days. Continuing small daily habits will further strengthen your energy levels."
        else:
            overall_progress = "Your wellness balance is recovering. Focusing on rest and short stress-relief exercises will help rebuild your vitality."

        # Positive habits identified
        positive_habits = []
        if summary.get("sleep_hours", 7.5) >= 7.0:
            positive_habits.append(f"Maintained optimal sleep duration ({summary.get('sleep_hours', 7.5)} hrs/night)")
        if summary.get("streak_count", 1) >= 2:
            positive_habits.append(f"Active wellness habit streak ({summary.get('streak_count', 1)} days)")
        if analytics["activity_distribution"]["Breathing"] + analytics["activity_distribution"]["Meditation"] > 0:
            positive_habits.append("Consistent mindfulness practice (breathing & meditation)")
        if analytics["activity_distribution"]["Journal"] > 0:
            positive_habits.append("Regular emotional check-ins via Reflection Journal")
        if not positive_habits:
            positive_habits.append("Initiated daily wellness tracking and self-awareness check-ins")

        # Areas needing attention
        areas_for_attention = []
        if "LOW_SLEEP_WARNING" in heuristics:
            areas_for_attention.append("Sleep latency & duration fell below the recommended 7-hour threshold")
        if "ELEVATED_STRESS" in heuristics:
            areas_for_attention.append("Recent mood logs indicated elevated stress or anxiety levels")
        if "HIGH_WORK_NO_REST" in heuristics:
            areas_for_attention.append("Extended focus work blocks completed without taking micro-rest breaks")
        if analytics["activity_distribution"]["Breathing"] == 0:
            areas_for_attention.append("Box breathing and parasympathetic nerve regulation exercises underutilized")
        if not areas_for_attention:
            areas_for_attention.append("Maintain current sleep cadence and avoid late-night screen time")

        # Personalised recommendations
        recommendations = []
        if "LOW_SLEEP_WARNING" in heuristics:
            recommendations.append("Log a 4-7-8 Relaxing Breath session 30 minutes before bedtime to lower heart rate.")
        if "HIGH_WORK_NO_REST" in heuristics:
            recommendations.append("Pair 50-minute Pomodoro focus blocks with 5-minute calm ambient soundscapes.")
        if score < 75:
            recommendations.append("Set aside 5 minutes each morning for a guided meditation session.")
        recommendations.append("Keep logging your daily mood check-ins to track long-term emotional patterns.")

        return {
            "overall_progress": overall_progress,
            "positive_habits": positive_habits,
            "areas_for_attention": areas_for_attention,
            "recommendations": recommendations
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
