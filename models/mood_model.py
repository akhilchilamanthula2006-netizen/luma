from datetime import datetime
from services.mongo_service import MongoService

class MoodModel:
    """
    Mood logging structure representing an entry in mood_logs.
    """
    def __init__(self, user_id: str, mood: str, score: int, source: str = "manual", notes: str = "", timestamp: datetime = None, id: str = None):
        self.id = id
        self.user_id = user_id
        self.mood = mood # e.g. Happy, Calm, Neutral, Sad, Stressed
        self.score = score # e.g. 1 to 5
        self.source = source # e.g. "manual"
        self.notes = notes # For future AI integration
        self.timestamp = timestamp or datetime.now() # Use server local time

    def to_dict(self) -> dict:
        return {
            "user_id": self.user_id,
            "mood": self.mood,
            "score": self.score,
            "source": self.source,
            "notes": self.notes,
            "timestamp": self.timestamp
        }

    @classmethod
    def from_dict(cls, data: dict):
        if not data:
            return None
        return cls(
            id=str(data.get("_id")),
            user_id=data.get("user_id"),
            mood=data.get("mood"),
            score=data.get("score"),
            source=data.get("source", "manual"),
            notes=data.get("notes", ""),
            timestamp=data.get("timestamp")
        )

    @staticmethod
    def get_collection():
        db = MongoService.get_db()
        if db is None:
            raise RuntimeError("Database connection not initialized.")
        return db["mood_logs"]

