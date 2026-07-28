from datetime import datetime
from bson import ObjectId

class SleepLogModel:
    def __init__(self, user_id, sleep_date, bedtime, wake_time, hours_slept, sleep_quality, time_to_fall_asleep_minutes=15, awakenings_count=0, sleep_score=0, source="manual", external_sync_id=None, created_at=None, _id=None):
        self.id = str(_id) if _id else None
        self.user_id = str(user_id)
        self.sleep_date = sleep_date  # YYYY-MM-DD
        self.bedtime = bedtime
        self.wake_time = wake_time
        self.hours_slept = hours_slept
        self.sleep_quality = sleep_quality  # 1 to 5
        self.time_to_fall_asleep_minutes = time_to_fall_asleep_minutes
        self.awakenings_count = awakenings_count
        self.sleep_score = sleep_score
        self.source = source
        self.external_sync_id = external_sync_id
        self.created_at = created_at or datetime.now()

    def to_dict(self):
        return {
            "user_id": ObjectId(self.user_id),
            "sleep_date": self.sleep_date,
            "bedtime": self.bedtime,
            "wake_time": self.wake_time,
            "hours_slept": self.hours_slept,
            "sleep_quality": self.sleep_quality,
            "time_to_fall_asleep_minutes": self.time_to_fall_asleep_minutes,
            "awakenings_count": self.awakenings_count,
            "sleep_score": self.sleep_score,
            "source": self.source,
            "external_sync_id": self.external_sync_id,
            "created_at": self.created_at
        }

    @classmethod
    def from_dict(cls, data):
        if not data:
            return None
        return cls(
            user_id=data.get("user_id"),
            sleep_date=data.get("sleep_date"),
            bedtime=data.get("bedtime"),
            wake_time=data.get("wake_time"),
            hours_slept=data.get("hours_slept", 0.0),
            sleep_quality=data.get("sleep_quality", 3),
            time_to_fall_asleep_minutes=data.get("time_to_fall_asleep_minutes", 15),
            awakenings_count=data.get("awakenings_count", 0),
            sleep_score=data.get("sleep_score", 0),
            source=data.get("source", "manual"),
            external_sync_id=data.get("external_sync_id"),
            created_at=data.get("created_at"),
            _id=data.get("_id")
        )
