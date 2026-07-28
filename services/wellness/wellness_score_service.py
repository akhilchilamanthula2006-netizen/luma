from datetime import datetime
from bson import ObjectId
from services.mongo_service import MongoService
from utils.wellness_constants import WELLNESS_SCORE_WEIGHTS, WELLNESS_ACTIVITIES

class WellnessScoreService:
    @classmethod
    def calculate_score(cls, user_id, date_str=None):
        db = MongoService.get_db()
        today = date_str or datetime.now().strftime("%Y-%m-%d")

        # 1. Sleep score (30%)
        sleep_doc = db.sleep_logs.find_one({"user_id": ObjectId(user_id), "sleep_date": today})
        sleep_score = sleep_doc.get("sleep_score", 70) if sleep_doc else 70

        # 2. Mood score (25%)
        mood_doc = db.mood_logs.find_one({"user_id": ObjectId(user_id)})
        primary_mood = mood_doc.get("mood_label", "Neutral") if mood_doc else "Neutral"
        mood_map = {"Happy": 95, "Calm": 90, "Neutral": 75, "Sad": 45, "Stressed": 40, "Anxious": 35, "Angry": 30, "Lonely": 35}
        mood_score = mood_map.get(primary_mood, 75)

        # 3. Mindfulness score (20%)
        b_count = db.breathing_sessions.count_documents({"user_id": ObjectId(user_id)})
        m_count = db.meditation_sessions.count_documents({"user_id": ObjectId(user_id)})
        mindfulness_mins = (b_count * 5) + (m_count * 10)
        mindfulness_score = min(100, max(50, mindfulness_mins * 4))

        # 4. Activity consistency (15%)
        act_cursor = db.activity_logs.find({"user_id": ObjectId(user_id), "date": today})
        completed_types = set(d["activity_type"] for d in act_cursor)
        activity_score = int((len(completed_types) / len(WELLNESS_ACTIVITIES)) * 100)

        # 5. Focus balance (10%)
        focus_doc = db.focus_sessions.find_one({"user_id": ObjectId(user_id)})
        focus_score = 85 if focus_doc else 75

        # Weighted calculation
        overall = (
            sleep_score * WELLNESS_SCORE_WEIGHTS["sleep"] +
            mood_score * WELLNESS_SCORE_WEIGHTS["mood"] +
            mindfulness_score * WELLNESS_SCORE_WEIGHTS["mindfulness"] +
            activity_score * WELLNESS_SCORE_WEIGHTS["activity"] +
            focus_score * WELLNESS_SCORE_WEIGHTS["focus"]
        )
        final_score = int(round(overall))

        label = "Thriving" if final_score >= 80 else "Stable" if final_score >= 65 else "Recovering" if final_score >= 50 else "Needs Attention"

        score_doc = {
            "user_id": ObjectId(user_id),
            "date": today,
            "overall_score": final_score,
            "label": label,
            "components": {
                "sleep_score": sleep_score,
                "mood_score": mood_score,
                "mindfulness_score": mindfulness_score,
                "activity_score": activity_score,
                "focus_score": focus_score
            },
            "calculated_at": datetime.now()
        }

        db.wellness_scores.update_one(
            {"user_id": ObjectId(user_id), "date": today},
            {"$set": score_doc},
            upsert=True
        )

        return {
            "current": final_score,
            "label": label,
            "components": score_doc["components"]
        }
