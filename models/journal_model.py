from datetime import datetime
from services.mongo_service import MongoService

class JournalModel:
    """
    Journal model mapping to entries in MongoDB.
    """
    def __init__(
        self,
        user_id: str,
        title: str,
        content: str,
        id: str = None,
        created_at: datetime = None,
        updated_at: datetime = None,
        deleted: bool = False,
        conversation_id: str = None,
        emotion_snapshot: dict = None,
    ):
        self.id = id
        self.user_id = user_id
        self.title = title
        self.content = content
        self.created_at = created_at or datetime.now()
        self.updated_at = updated_at or self.created_at
        self.deleted = deleted
        self.conversation_id = conversation_id
        self.emotion_snapshot = emotion_snapshot or {}

    def to_dict(self) -> dict:
        doc = {
            "user_id": self.user_id,
            "title": self.title,
            "content": self.content,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "deleted": self.deleted,
        }
        if self.conversation_id:
            doc["conversation_id"] = self.conversation_id
        if self.emotion_snapshot:
            doc["emotion_snapshot"] = self.emotion_snapshot
        return doc

    @classmethod
    def from_dict(cls, data: dict):
        if not data:
            return None
        return cls(
            id=str(data.get("_id")),
            user_id=data.get("user_id"),
            title=data.get("title", ""),
            content=data.get("content", ""),
            created_at=data.get("created_at"),
            updated_at=data.get("updated_at"),
            deleted=data.get("deleted", False),
            conversation_id=data.get("conversation_id"),
            emotion_snapshot=data.get("emotion_snapshot") or data.get("ai_analysis"),
        )

    @staticmethod
    def get_collection():
        db = MongoService.get_db()
        if db is None:
            raise RuntimeError("Database connection not initialized.")
        return db["journals"]
