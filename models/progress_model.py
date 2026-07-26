from datetime import datetime
from services.mongo_service import MongoService

class ProgressModel:
    """
    Tracks milestones, streaks, and activity progress for the user.
    """
    def __init__(self, user_id: str, streak_days: int = 0, last_active: datetime = None, achievements: list = None):
        self.user_id = user_id
        self.streak_days = streak_days
        self.last_active = last_active or datetime.utcnow()
        self.achievements = achievements or []

    def to_dict(self) -> dict:
        return {
            "user_id": self.user_id,
            "streak_days": self.streak_days,
            "last_active": self.last_active,
            "achievements": self.achievements
        }

    @staticmethod
    def get_collection():
        db = MongoService.get_db()
        return db["progress"] if db is not None else None
