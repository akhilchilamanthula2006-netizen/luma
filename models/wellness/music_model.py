from datetime import datetime
from bson import ObjectId

class MusicTrackModel:
    def __init__(self, track_id, title, duration_seconds, category, artist, description="", mood_tags=None, thumbnail_path="", audio_source=None, created_at=None, _id=None):
        self.id = str(_id) if _id else None
        self.track_id = track_id
        self.title = title
        self.duration_seconds = duration_seconds
        self.category = category
        self.artist = artist
        self.description = description
        self.mood_tags = mood_tags or []
        self.thumbnail_path = thumbnail_path
        self.audio_source = audio_source or {"provider": "local", "resource_url": "", "external_id": None}
        self.created_at = created_at or datetime.now()

    def to_dict(self):
        return {
            "track_id": self.track_id,
            "title": self.title,
            "duration_seconds": self.duration_seconds,
            "category": self.category,
            "artist": self.artist,
            "description": self.description,
            "mood_tags": self.mood_tags,
            "thumbnail_path": self.thumbnail_path,
            "audio_source": self.audio_source,
            "created_at": self.created_at
        }

    @classmethod
    def from_dict(cls, data):
        if not data:
            return None
        return cls(
            track_id=data.get("track_id"),
            title=data.get("title"),
            duration_seconds=data.get("duration_seconds", 0),
            category=data.get("category"),
            artist=data.get("artist"),
            description=data.get("description", ""),
            mood_tags=data.get("mood_tags", []),
            thumbnail_path=data.get("thumbnail_path", ""),
            audio_source=data.get("audio_source", {}),
            created_at=data.get("created_at"),
            _id=data.get("_id")
        )


class MusicListeningHistoryModel:
    def __init__(self, user_id, track_id, category, started_at, ended_at=None, listened_duration_seconds=0, completion_percentage=0.0, skipped=False, _id=None):
        self.id = str(_id) if _id else None
        self.user_id = str(user_id)
        self.track_id = track_id
        self.category = category
        self.started_at = started_at or datetime.now()
        self.ended_at = ended_at or datetime.now()
        self.listened_duration_seconds = listened_duration_seconds
        self.completion_percentage = completion_percentage
        self.skipped = skipped

    def to_dict(self):
        return {
            "user_id": ObjectId(self.user_id),
            "track_id": self.track_id,
            "category": self.category,
            "started_at": self.started_at,
            "ended_at": self.ended_at,
            "listened_duration_seconds": self.listened_duration_seconds,
            "completion_percentage": self.completion_percentage,
            "skipped": self.skipped
        }

    @classmethod
    def from_dict(cls, data):
        if not data:
            return None
        return cls(
            user_id=data.get("user_id"),
            track_id=data.get("track_id"),
            category=data.get("category"),
            started_at=data.get("started_at"),
            ended_at=data.get("ended_at"),
            listened_duration_seconds=data.get("listened_duration_seconds", 0),
            completion_percentage=data.get("completion_percentage", 0.0),
            skipped=data.get("skipped", False),
            _id=data.get("_id")
        )
