from datetime import datetime
from bson import ObjectId
from services.mongo_service import MongoService
from models.wellness.activity_model import ActivityLogModel
from utils.wellness_constants import WELLNESS_ACTIVITIES

class ActivityService:
    @staticmethod
    def log_activity(user_id, activity_type, date_str=None, value=1, unit="count"):
        if activity_type not in WELLNESS_ACTIVITIES:
            activity_type = "hydrate"

        db = MongoService.get_db()
        today = date_str or datetime.now().strftime("%Y-%m-%d")

        log = ActivityLogModel(
            user_id=user_id,
            date=today,
            activity_type=activity_type,
            value=value,
            unit=unit
        )
        res = db.activity_logs.insert_one(log.to_dict())
        log.id = str(res.inserted_id)
        return log.to_dict()

    @staticmethod
    def get_daily_activities(user_id, date_str=None):
        db = MongoService.get_db()
        today = date_str or datetime.now().strftime("%Y-%m-%d")
        cursor = db.activity_logs.find({"user_id": ObjectId(user_id), "date": today})

        completed_types = set()
        logs = []
        for doc in cursor:
            completed_types.add(doc["activity_type"])
            doc["_id"] = str(doc["_id"])
            doc["user_id"] = str(doc["user_id"])
            logs.append(doc)

        items = []
        for act in WELLNESS_ACTIVITIES:
            items.append({
                "type": act,
                "completed": act in completed_types
            })

        return {
            "date": today,
            "completed_count": len(completed_types),
            "total_count": len(WELLNESS_ACTIVITIES),
            "items": items,
            "raw_logs": logs
        }
