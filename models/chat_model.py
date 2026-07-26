from datetime import datetime
from services.mongo_service import MongoService

class ChatModel:
    """
    Chat message schema and helpers.
    """
    def __init__(self, user_id: str, sender: str, message: str, timestamp: datetime = None):
        self.user_id = user_id
        self.sender = sender # 'user' or 'ai'
        self.message = message
        self.timestamp = timestamp or datetime.utcnow()

    def to_dict(self) -> dict:
        return {
            "user_id": self.user_id,
            "sender": self.sender,
            "message": self.message,
            "timestamp": self.timestamp
        }

    @staticmethod
    def get_collection():
        db = MongoService.get_db()
        return db["chats"] if db is not None else None
