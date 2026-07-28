from bson import ObjectId
from services.mongo_service import MongoService
from models.wellness.breathing_model import BreathingSessionModel
from utils.wellness_constants import BREATHING_PATTERNS

class BreathingService:
    @staticmethod
    def get_patterns():
        return BREATHING_PATTERNS

    @staticmethod
    def log_session(user_id, pattern_type, config, target_cycles, completed_cycles, duration_seconds, completed=True):
        db = MongoService.get_db()
        session = BreathingSessionModel(
            user_id=user_id,
            pattern_type=pattern_type,
            config=config or BREATHING_PATTERNS.get(pattern_type, {}).get("config", {}),
            target_cycles=target_cycles,
            completed_cycles=completed_cycles,
            duration_seconds=duration_seconds,
            completed=completed
        )
        res = db.breathing_sessions.insert_one(session.to_dict())
        session.id = str(res.inserted_id)
        return session.to_dict()

    @staticmethod
    def get_user_history(user_id, limit=20):
        db = MongoService.get_db()
        cursor = db.breathing_sessions.find({"user_id": ObjectId(user_id)}).sort("created_at", -1).limit(limit)
        results = []
        for doc in cursor:
            doc["_id"] = str(doc["_id"])
            doc["user_id"] = str(doc["user_id"])
            results.append(doc)
        return results
