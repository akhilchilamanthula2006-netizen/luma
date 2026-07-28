from datetime import datetime
from bson import ObjectId

class BreathingSessionModel:
    def __init__(self, user_id, pattern_type, config, target_cycles, completed_cycles, duration_seconds, completed=True, created_at=None, _id=None):
        self.id = str(_id) if _id else None
        self.user_id = str(user_id)
        self.pattern_type = pattern_type
        self.config = config or {}
        self.target_cycles = target_cycles
        self.completed_cycles = completed_cycles
        self.duration_seconds = duration_seconds
        self.completed = completed
        self.created_at = created_at or datetime.now()

    def to_dict(self):
        return {
            "user_id": ObjectId(self.user_id),
            "pattern_type": self.pattern_type,
            "config": self.config,
            "target_cycles": self.target_cycles,
            "completed_cycles": self.completed_cycles,
            "duration_seconds": self.duration_seconds,
            "completed": self.completed,
            "created_at": self.created_at
        }

    @classmethod
    def from_dict(cls, data):
        if not data:
            return None
        return cls(
            user_id=data.get("user_id"),
            pattern_type=data.get("pattern_type"),
            config=data.get("config", {}),
            target_cycles=data.get("target_cycles", 0),
            completed_cycles=data.get("completed_cycles", 0),
            duration_seconds=data.get("duration_seconds", 0),
            completed=data.get("completed", True),
            created_at=data.get("created_at"),
            _id=data.get("_id")
        )
