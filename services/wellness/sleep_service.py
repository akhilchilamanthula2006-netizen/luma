from datetime import datetime
from bson import ObjectId
from services.mongo_service import MongoService
from models.wellness.sleep_model import SleepLogModel

class SleepService:
    @staticmethod
    def calculate_sleep_score(hours_slept, quality_1_to_5, latency_minutes=15, awakenings=0):
        """
        Compute deterministic sleep score (0 to 100).
        """
        # Duration score (optimal 7.5 - 9.0 hrs)
        if 7.0 <= hours_slept <= 9.0:
            duration_score = 40
        elif 6.0 <= hours_slept < 7.0 or 9.0 < hours_slept <= 10.0:
            duration_score = 30
        elif 5.0 <= hours_slept < 6.0:
            duration_score = 20
        else:
            duration_score = 10

        # Quality rating score (1-5 -> 0-40)
        quality_score = min(40, max(8, quality_1_to_5 * 8))

        # Latency & Awakenings deductions (up to 20 pts)
        latency_penalty = max(0, (latency_minutes - 20) // 10) * 2
        awakening_penalty = awakenings * 4
        subtotal = duration_score + quality_score + 20 - latency_penalty - awakening_penalty

        return max(0, min(100, int(subtotal)))

    @classmethod
    def log_sleep(cls, user_id, sleep_date, bedtime, wake_time, hours_slept, sleep_quality, latency_minutes=15, awakenings=0, source="manual"):
        db = MongoService.get_db()
        score = cls.calculate_sleep_score(hours_slept, sleep_quality, latency_minutes, awakenings)

        sleep_doc = SleepLogModel(
            user_id=user_id,
            sleep_date=sleep_date,
            bedtime=bedtime,
            wake_time=wake_time,
            hours_slept=hours_slept,
            sleep_quality=sleep_quality,
            time_to_fall_asleep_minutes=latency_minutes,
            awakenings_count=awakenings,
            sleep_score=score,
            source=source
        )

        # Upsert by user_id + sleep_date
        query = {"user_id": ObjectId(user_id), "sleep_date": sleep_date}
        db.sleep_logs.update_one(query, {"$set": sleep_doc.to_dict()}, upsert=True)

        return db.sleep_logs.find_one(query)

    @staticmethod
    def get_sleep_history(user_id, days=30):
        db = MongoService.get_db()
        cursor = db.sleep_logs.find({"user_id": ObjectId(user_id)}).sort("sleep_date", -1).limit(days)
        results = []
        for doc in cursor:
            doc["_id"] = str(doc["_id"])
            doc["user_id"] = str(doc["user_id"])
            results.append(doc)
        return results
