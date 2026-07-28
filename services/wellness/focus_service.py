from bson import ObjectId
from services.mongo_service import MongoService
from models.wellness.focus_model import FocusSessionModel
from utils.wellness_constants import FOCUS_PRESETS

class FocusService:
    @staticmethod
    def get_presets():
        return FOCUS_PRESETS

    @staticmethod
    def log_session(user_id, session_type, work_duration_minutes, break_duration_minutes, completed_work_intervals, total_focus_seconds, interrupted=False):
        db = MongoService.get_db()
        session = FocusSessionModel(
            user_id=user_id,
            session_type=session_type,
            work_duration_minutes=work_duration_minutes,
            break_duration_minutes=break_duration_minutes,
            completed_work_intervals=completed_work_intervals,
            total_focus_seconds=total_focus_seconds,
            interrupted=interrupted
        )
        res = db.focus_sessions.insert_one(session.to_dict())
        session.id = str(res.inserted_id)
        return session.to_dict()

    @staticmethod
    def get_user_history(user_id, limit=20):
        db = MongoService.get_db()
        cursor = db.focus_sessions.find({"user_id": ObjectId(user_id)}).sort("created_at", -1).limit(limit)
        results = []
        for doc in cursor:
            doc["_id"] = str(doc["_id"])
            doc["user_id"] = str(doc["user_id"])
            results.append(doc)
        return results
