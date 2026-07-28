from datetime import datetime
from bson import ObjectId

class FocusSessionModel:
    def __init__(self, user_id, session_type, work_duration_minutes, break_duration_minutes, completed_work_intervals, total_focus_seconds, interrupted=False, created_at=None, _id=None):
        self.id = str(_id) if _id else None
        self.user_id = str(user_id)
        self.session_type = session_type
        self.work_duration_minutes = work_duration_minutes
        self.break_duration_minutes = break_duration_minutes
        self.completed_work_intervals = completed_work_intervals
        self.total_focus_seconds = total_focus_seconds
        self.interrupted = interrupted
        self.created_at = created_at or datetime.now()

    def to_dict(self):
        return {
            "user_id": ObjectId(self.user_id),
            "session_type": self.session_type,
            "work_duration_minutes": self.work_duration_minutes,
            "break_duration_minutes": self.break_duration_minutes,
            "completed_work_intervals": self.completed_work_intervals,
            "total_focus_seconds": self.total_focus_seconds,
            "interrupted": self.interrupted,
            "created_at": self.created_at
        }

    @classmethod
    def from_dict(cls, data):
        if not data:
            return None
        return cls(
            user_id=data.get("user_id"),
            session_type=data.get("session_type", "pomodoro"),
            work_duration_minutes=data.get("work_duration_minutes", 25),
            break_duration_minutes=data.get("break_duration_minutes", 5),
            completed_work_intervals=data.get("completed_work_intervals", 0),
            total_focus_seconds=data.get("total_focus_seconds", 0),
            interrupted=data.get("interrupted", False),
            created_at=data.get("created_at"),
            _id=data.get("_id")
        )
