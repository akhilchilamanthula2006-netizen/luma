from datetime import datetime
from bson import ObjectId

class ActivityLogModel:
    def __init__(self, user_id, date, activity_type, value=1, unit="count", created_at=None, _id=None):
        self.id = str(_id) if _id else None
        self.user_id = str(user_id)
        self.date = date  # YYYY-MM-DD
        self.activity_type = activity_type
        self.value = value
        self.unit = unit
        self.created_at = created_at or datetime.now()

    def to_dict(self):
        return {
            "user_id": ObjectId(self.user_id),
            "date": self.date,
            "activity_type": self.activity_type,
            "value": self.value,
            "unit": self.unit,
            "created_at": self.created_at
        }

    @classmethod
    def from_dict(cls, data):
        if not data:
            return None
        return cls(
            user_id=data.get("user_id"),
            date=data.get("date"),
            activity_type=data.get("activity_type"),
            value=data.get("value", 1),
            unit=data.get("unit", "count"),
            created_at=data.get("created_at"),
            _id=data.get("_id")
        )
