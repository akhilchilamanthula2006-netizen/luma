from datetime import datetime
from models.mood_model import MoodModel
import pymongo

class MoodService:
    """
    Service for managing mood tracking data and mapping scores.
    """
    MOOD_SCORE_MAP = {
        "Happy": 5,
        "Calm": 4,
        "Neutral": 3,
        "Sad": 2,
        "Stressed": 1
    }

    @classmethod
    def get_score_for_mood(cls, mood: str) -> int:
        """Centralized mapping of mood string to score."""
        return cls.MOOD_SCORE_MAP.get(mood, 3)

    @classmethod
    def log_mood(cls, user_id: str, mood: str, notes: str = "") -> dict:
        """
        Logs a user mood. Checks if a mood log exists for today
        (server local time) and updates it; otherwise inserts a new record.
        """
        score = cls.get_score_for_mood(mood)
        collection = MoodModel.get_collection()

        # Define boundary for today in server local time
        now = datetime.now()
        start_of_day = now.replace(hour=0, minute=0, second=0, microsecond=0)
        end_of_day = now.replace(hour=23, minute=59, second=59, microsecond=999999)

        # Query for existing log today
        existing_log = collection.find_one({
            "user_id": user_id,
            "timestamp": {"$gte": start_of_day, "$lte": end_of_day}
        })

        if existing_log:
            # Update existing log
            collection.update_one(
                {"_id": existing_log["_id"]},
                {"$set": {
                    "mood": mood,
                    "score": score,
                    "notes": notes,
                    "timestamp": now # Update timestamp to latest check-in
                }}
            )
            action = "updated"
        else:
            # Create a new log
            new_log = MoodModel(
                user_id=user_id,
                mood=mood,
                score=score,
                source="manual",
                notes=notes,
                timestamp=now
            )
            collection.insert_one(new_log.to_dict())
            action = "created"

        return {"status": "success", "action": action, "mood": mood}

    @classmethod
    def get_latest_mood(cls, user_id: str) -> MoodModel:
        """Retrieves the latest logged mood for a given user."""
        collection = MoodModel.get_collection()
        latest = collection.find_one(
            {"user_id": user_id},
            sort=[("timestamp", pymongo.DESCENDING)]
        )
        return MoodModel.from_dict(latest) if latest else None

