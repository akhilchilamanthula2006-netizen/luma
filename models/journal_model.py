from datetime import datetime
from services.mongo_service import MongoService

class JournalModel:
    """
    Journal model mapping to entries in MongoDB.
    """
    def __init__(self, user_id: str, title: str, content: str, mood_rating: int = None, ai_analysis: dict = None, created_at: datetime = None):
        self.user_id = user_id
        self.title = title
        self.content = content
        self.mood_rating = mood_rating
        self.ai_analysis = ai_analysis or {}
        self.created_at = created_at or datetime.utcnow()

    def to_dict(self) -> dict:
        return {
            "user_id": self.user_id,
            "title": self.title,
            "content": self.content,
            "mood_rating": self.mood_rating,
            "ai_analysis": self.ai_analysis,
            "created_at": self.created_at
        }

    @staticmethod
    def get_collection():
        db = MongoService.get_db()
        return db["journals"] if db is not None else None
