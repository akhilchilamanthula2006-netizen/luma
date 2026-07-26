from datetime import datetime
import pymongo
from services.mongo_service import MongoService


class ChatHistoryModel:
    """
    Represents the chat_history MongoDB collection.

    Schema per document:
        conversation_id (str)      – ties message to a conversation
        user_id         (str)      – the logged-in user's ID
        role            (str)      – "user" | "assistant"
        content         (str)      – raw message text
        timestamp       (datetime) – UTC time of insertion
        model           (str|None) – Groq model name; only present on assistant messages
    """

    COLLECTION_NAME = "chat_history"

    @staticmethod
    def get_collection():
        db = MongoService.get_db()
        if db is None:
            raise RuntimeError("Database connection not initialized.")
        return db[ChatHistoryModel.COLLECTION_NAME]

    @staticmethod
    def save(user_id: str, conversation_id: str, role: str, content: str, model: str = None) -> None:
        """
        Persist a single message tied to a specific conversation.
        """
        doc = {
            "conversation_id": conversation_id,
            "user_id":   user_id,
            "role":      role,
            "content":   content,
            "timestamp": datetime.utcnow(),
        }
        if model:
            doc["model"] = model
        ChatHistoryModel.get_collection().insert_one(doc)

    @staticmethod
    def get_by_conversation(conversation_id: str) -> list:
        """
        Return all messages for a specific conversation in chronological order.
        """
        cursor = (
            ChatHistoryModel.get_collection()
            .find(
                {"conversation_id": conversation_id},
                {"_id": 0, "role": 1, "content": 1, "timestamp": 1, "model": 1},
            )
            .sort("timestamp", pymongo.ASCENDING)
        )
        return list(cursor)

    @staticmethod
    def delete_by_conversation(conversation_id: str) -> None:
        """
        Delete all messages belonging to a conversation.
        """
        ChatHistoryModel.get_collection().delete_many({"conversation_id": conversation_id})

    @staticmethod
    def get_recent(user_id: str, limit: int = 20) -> list:
        """
        (Legacy) Return the latest `limit` messages for the user.
        Kept for backward compatibility during transition.
        """
        cursor = (
            ChatHistoryModel.get_collection()
            .find(
                {"user_id": user_id},
                {"_id": 0, "role": 1, "content": 1, "timestamp": 1, "model": 1},
            )
            .sort("timestamp", pymongo.DESCENDING)
            .limit(limit)
        )
        messages = list(cursor)
        messages.reverse()
        return messages
