from services.mongo_service import MongoService

class AIPreferencesModel:
    """
    Model storing customization settings for the AI Companion (e.g. tone, response frequency).
    """
    def __init__(self, user_id: str, tone: str = "Empathetic", notification_frequency: str = "daily"):
        self.user_id = user_id
        self.tone = tone
        self.notification_frequency = notification_frequency

    def to_dict(self) -> dict:
        return {
            "user_id": self.user_id,
            "tone": self.tone,
            "notification_frequency": self.notification_frequency
        }

    @staticmethod
    def get_collection():
        db = MongoService.get_db()
        return db["ai_preferences"] if db is not None else None
