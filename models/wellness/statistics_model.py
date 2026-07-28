from datetime import datetime
from bson import ObjectId

class WellnessDailySummaryModel:
    def __init__(self, user_id, date, breathing_minutes=0, meditation_minutes=0, focus_minutes=0, music_minutes=0, activities_completed=0, sleep_hours=0.0, sleep_score=0, overall_score=0, streak_count=0, updated_at=None, _id=None):
        self.id = str(_id) if _id else None
        self.user_id = str(user_id)
        self.date = date  # YYYY-MM-DD
        self.breathing_minutes = breathing_minutes
        self.meditation_minutes = meditation_minutes
        self.focus_minutes = focus_minutes
        self.music_minutes = music_minutes
        self.activities_completed = activities_completed
        self.sleep_hours = sleep_hours
        self.sleep_score = sleep_score
        self.overall_score = overall_score
        self.streak_count = streak_count
        self.updated_at = updated_at or datetime.now()

    def to_dict(self):
        return {
            "user_id": ObjectId(self.user_id),
            "date": self.date,
            "breathing_minutes": self.breathing_minutes,
            "meditation_minutes": self.meditation_minutes,
            "focus_minutes": self.focus_minutes,
            "music_minutes": self.music_minutes,
            "activities_completed": self.activities_completed,
            "sleep_hours": self.sleep_hours,
            "sleep_score": self.sleep_score,
            "overall_score": self.overall_score,
            "streak_count": self.streak_count,
            "updated_at": self.updated_at
        }

    @classmethod
    def from_dict(cls, data):
        if not data:
            return None
        return cls(
            user_id=data.get("user_id"),
            date=data.get("date"),
            breathing_minutes=data.get("breathing_minutes", 0),
            meditation_minutes=data.get("meditation_minutes", 0),
            focus_minutes=data.get("focus_minutes", 0),
            music_minutes=data.get("music_minutes", 0),
            activities_completed=data.get("activities_completed", 0),
            sleep_hours=data.get("sleep_hours", 0.0),
            sleep_score=data.get("sleep_score", 0),
            overall_score=data.get("overall_score", 0),
            streak_count=data.get("streak_count", 0),
            updated_at=data.get("updated_at"),
            _id=data.get("_id")
        )


class RecommendationFeedbackModel:
    def __init__(self, user_id, recommendation_id, recommendation_type, accepted=False, dismissed=False, helpful=False, not_helpful=False, timestamp=None, _id=None):
        self.id = str(_id) if _id else None
        self.user_id = str(user_id)
        self.recommendation_id = recommendation_id
        self.recommendation_type = recommendation_type
        self.accepted = accepted
        self.dismissed = dismissed
        self.helpful = helpful
        self.not_helpful = not_helpful
        self.timestamp = timestamp or datetime.now()

    def to_dict(self):
        return {
            "user_id": ObjectId(self.user_id),
            "recommendation_id": self.recommendation_id,
            "recommendation_type": self.recommendation_type,
            "accepted": self.accepted,
            "dismissed": self.dismissed,
            "helpful": self.helpful,
            "not_helpful": self.not_helpful,
            "timestamp": self.timestamp
        }

    @classmethod
    def from_dict(cls, data):
        if not data:
            return None
        return cls(
            user_id=data.get("user_id"),
            recommendation_id=data.get("recommendation_id"),
            recommendation_type=data.get("recommendation_type"),
            accepted=data.get("accepted", False),
            dismissed=data.get("dismissed", False),
            helpful=data.get("helpful", False),
            not_helpful=data.get("not_helpful", False),
            timestamp=data.get("timestamp"),
            _id=data.get("_id")
        )
