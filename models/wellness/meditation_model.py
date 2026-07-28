from datetime import datetime
from bson import ObjectId

class MeditationSessionModel:
    def __init__(self, user_id, duration_minutes, elapsed_seconds, completed=True, guided=False, ambient_sound=None, created_at=None, _id=None):
        self.id = str(_id) if _id else None
        self.user_id = str(user_id)
        self.duration_minutes = duration_minutes
        self.elapsed_seconds = elapsed_seconds
        self.completed = completed
        self.guided = guided
        self.ambient_sound = ambient_sound
        self.created_at = created_at or datetime.now()

    def to_dict(self):
        return {
            "user_id": ObjectId(self.user_id),
            "duration_minutes": self.duration_minutes,
            "elapsed_seconds": self.elapsed_seconds,
            "completed": self.completed,
            "guided": self.guided,
            "ambient_sound": self.ambient_sound,
            "created_at": self.created_at
        }

    @classmethod
    def from_dict(cls, data):
        if not data:
            return None
        return cls(
            user_id=data.get("user_id"),
            duration_minutes=data.get("duration_minutes", 0),
            elapsed_seconds=data.get("elapsed_seconds", 0),
            completed=data.get("completed", True),
            guided=data.get("guided", False),
            ambient_sound=data.get("ambient_sound"),
            created_at=data.get("created_at"),
            _id=data.get("_id")
        )
