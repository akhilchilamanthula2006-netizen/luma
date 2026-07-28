from bson import ObjectId
from services.mongo_service import MongoService
from models.wellness.meditation_model import MeditationSessionModel

class MeditationService:
    @staticmethod
    def log_session(user_id, duration_minutes, elapsed_seconds, completed=True, guided=False, ambient_sound=None):
        db = MongoService.get_db()
        session = MeditationSessionModel(
            user_id=user_id,
            duration_minutes=duration_minutes,
            elapsed_seconds=elapsed_seconds,
            completed=completed,
            guided=guided,
            ambient_sound=ambient_sound
        )
        res = db.meditation_sessions.insert_one(session.to_dict())
        session.id = str(res.inserted_id)
        return session.to_dict()

    @staticmethod
    def get_user_history(user_id, limit=20):
        db = MongoService.get_db()
        cursor = db.meditation_sessions.find({"user_id": ObjectId(user_id)}).sort("created_at", -1).limit(limit)
        results = []
        for doc in cursor:
            doc["_id"] = str(doc["_id"])
            doc["user_id"] = str(doc["user_id"])
            results.append(doc)
        return results
