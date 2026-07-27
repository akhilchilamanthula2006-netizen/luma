from datetime import datetime
from bson import ObjectId
import pymongo
from services.mongo_service import MongoService

class ConversationModel:
    """
    Represents the conversations MongoDB collection.

    Schema:
        user_id       (str)      - owner (from session)
        title         (str)      - auto-generated after first message
        last_message  (str)      - preview of the latest message
        message_count (int)      - total number of messages
        created_at    (datetime) - UTC time of creation
        updated_at    (datetime) - UTC time of last message
        is_archived   (bool)     - archive status (default: False)
    """
    COLLECTION_NAME = "conversations"

    @staticmethod
    def get_collection():
        db = MongoService.get_db()
        if db is None:
            raise RuntimeError("Database connection not initialized.")
        return db[ConversationModel.COLLECTION_NAME]

    @staticmethod
    def create(user_id: str) -> str:
        """Creates a new conversation and returns its ID as a string."""
        now = datetime.utcnow()
        doc = {
            "user_id": user_id,
            "title": "New Chat",
            "last_message": "",
            "message_count": 0,
            "created_at": now,
            "updated_at": now,
            "is_archived": False
        }
        result = ConversationModel.get_collection().insert_one(doc)
        return str(result.inserted_id)

    @staticmethod
    def get_all_for_user(user_id: str) -> list:
        """Returns non-archived conversations sorted by updated_at DESC."""
        cursor = (
            ConversationModel.get_collection()
            .find({"user_id": user_id, "is_archived": False})
            .sort("updated_at", pymongo.DESCENDING)
        )
        
        results = []
        for doc in cursor:
            results.append({
                "id": str(doc["_id"]),
                "title": doc.get("title", "New Chat"),
                "last_message": doc.get("last_message", ""),
                "updated_at": doc.get("updated_at")
            })
        return results

    @staticmethod
    def get_by_id(conversation_id: str, user_id: str) -> dict:
        """Fetch a single conversation for ownership verification."""
        try:
            obj_id = ObjectId(conversation_id)
        except Exception:
            return None

        doc = ConversationModel.get_collection().find_one({
            "_id": obj_id,
            "user_id": user_id
        })
        if doc:
            return {
                "id": str(doc["_id"]),
                "title": doc.get("title", "New Chat"),
                "last_message": doc.get("last_message", ""),
                "message_count": doc.get("message_count", 0),
                "created_at": doc.get("created_at"),
                "updated_at": doc.get("updated_at"),
                "is_archived": doc.get("is_archived", False)
            }
        return None

    @staticmethod
    def set_title(conversation_id: str, title: str) -> None:
        """Updates the conversation title."""
        try:
            obj_id = ObjectId(conversation_id)
        except Exception:
            return

        ConversationModel.get_collection().update_one(
            {"_id": obj_id},
            {"$set": {"title": title}}
        )

    @staticmethod
    def update_last_message(conversation_id: str, content: str) -> None:
        """Updates last_message, increments message_count, and sets updated_at."""
        try:
            obj_id = ObjectId(conversation_id)
        except Exception:
            return

        ConversationModel.get_collection().update_one(
            {"_id": obj_id},
            {
                "$set": {
                    "last_message": content,
                    "updated_at": datetime.utcnow()
                },
                "$inc": {"message_count": 1}
            }
        )

    @staticmethod
    def update_emotion_metadata(conversation_id: str, emotion: dict) -> None:
        """
        Persist emotion analysis results onto the conversation document.

        Called after every successful AI analysis so the conversation always
        carries its latest emotional context. This allows the dashboard,
        analytics, and sidebar to surface mood information without querying
        mood_logs separately.

        Fields written:
            last_detected_mood  (str)      – primary_mood from analysis
            dominant_mood       (str)      – same as primary_mood for now;
                                            reserved for future aggregation
            risk_level          (str)      – low | medium | high
            updated_at          (datetime) – UTC timestamp of this update
        """
        try:
            obj_id = ObjectId(conversation_id)
        except Exception:
            return

        ConversationModel.get_collection().update_one(
            {"_id": obj_id},
            {"$set": {
                "last_detected_mood": emotion.get("primary_mood", "Neutral"),
                "dominant_mood":      emotion.get("primary_mood", "Neutral"),
                "risk_level":         emotion.get("risk_level", "low"),
                "updated_at":         datetime.utcnow(),
            }}
        )

    @staticmethod
    def delete(conversation_id: str, user_id: str) -> bool:
        """Deletes the conversation if user_id matches."""
        try:
            obj_id = ObjectId(conversation_id)
        except Exception:
            return False

        result = ConversationModel.get_collection().delete_one({
            "_id": obj_id,
            "user_id": user_id
        })
        return result.deleted_count > 0
