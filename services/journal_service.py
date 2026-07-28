from datetime import datetime
from bson import ObjectId
import logging

from models.journal_model import JournalModel
from services.intelligence_service import IntelligenceService
from utils.constants import DEFAULT_EMOTION

logger = logging.getLogger(__name__)

class JournalService:
    """
    Service for managing reflection journal entries.
    """

    @staticmethod
    def list_entries(user_id: str) -> list:
        """
        Retrieves all active (non-deleted) journal entries for a given user.
        Sorted by created_at descending.
        """
        try:
            collection = JournalModel.get_collection()
            cursor = collection.find({"user_id": user_id, "deleted": False}).sort("created_at", -1)
            return [JournalModel.from_dict(doc) for doc in cursor]
        except Exception as e:
            logger.error("Error listing journal entries for user %s: %s", user_id, e)
            return []

    @staticmethod
    def get_entry(entry_id: str, user_id: str) -> JournalModel | None:
        """
        Retrieves a single journal entry by ID, verifying ownership and active status.
        """
        if not entry_id:
            return None
        try:
            obj_id = ObjectId(entry_id)
        except Exception:
            logger.warning("Invalid ObjectId format for entry_id: %s", entry_id)
            return None

        try:
            collection = JournalModel.get_collection()
            doc = collection.find_one({"_id": obj_id, "user_id": user_id, "deleted": False})
            return JournalModel.from_dict(doc) if doc else None
        except Exception as e:
            logger.error("Error retrieving journal entry %s for user %s: %s", entry_id, user_id, e)
            return None

    @staticmethod
    def save_entry(
        user_id: str,
        username: str,
        title: str,
        content: str,
        entry_id: str = None,
        conversation_id: str = None
    ) -> JournalModel | None:
        """
        Saves a new journal entry or updates an existing one.
        Triggers AI analysis via IntelligenceService if content is new or changed.
        """
        collection = JournalModel.get_collection()
        now = datetime.now()

        # Check if updating an existing entry
        existing_entry = None
        if entry_id:
            existing_entry = JournalService.get_entry(entry_id, user_id)

        # Decide whether we need to call the AI Wellness Engine
        if existing_entry:
            # If the content is identical, skip LLM calls and reuse the snapshot
            if existing_entry.content.strip() == content.strip():
                logger.info("Content unchanged for entry %s. Reusing existing emotion snapshot.", entry_id)
                emotion_snapshot = existing_entry.emotion_snapshot
            else:
                logger.info("Content changed for entry %s. Triggering AI re-analysis.", entry_id)
                reply, emotion_snapshot, error = IntelligenceService.analyze(
                    username=username,
                    mood_label=None,
                    history=[],
                    user_message=content
                )
                if error:
                    logger.warning("AI analysis failed during update: %s. Using default emotion snapshot.", error)

            # Update database
            try:
                collection.update_one(
                    {"_id": ObjectId(entry_id)},
                    {"$set": {
                        "title": title.strip(),
                        "content": content.strip(),
                        "emotion_snapshot": emotion_snapshot,
                        "updated_at": now
                    }}
                )
                # Fetch and return updated model
                return JournalService.get_entry(entry_id, user_id)
            except Exception as e:
                logger.error("Failed to update journal entry %s: %s", entry_id, e)
                return None
        else:
            # Create flow: always call AI Wellness Engine
            logger.info("Creating new journal entry for user %s. Triggering AI analysis.", user_id)
            reply, emotion_snapshot, error = IntelligenceService.analyze(
                username=username,
                mood_label=None,
                history=[],
                user_message=content
            )
            if error:
                logger.warning("AI analysis failed during creation: %s. Using default emotion snapshot.", error)

            try:
                new_model = JournalModel(
                    user_id=user_id,
                    title=title.strip() if title.strip() else "Untitled Reflection",
                    content=content.strip(),
                    created_at=now,
                    updated_at=now,
                    deleted=False,
                    conversation_id=conversation_id,
                    emotion_snapshot=emotion_snapshot
                )
                res = collection.insert_one(new_model.to_dict())
                new_model.id = str(res.inserted_id)
                return new_model
            except Exception as e:
                logger.error("Failed to create new journal entry: %s", e)
                return None

    @staticmethod
    def delete_entry(entry_id: str, user_id: str) -> bool:
        """
        Soft-deletes a journal entry by setting its deleted flag to True.
        """
        if not entry_id:
            return False
        try:
            obj_id = ObjectId(entry_id)
        except Exception:
            return False

        try:
            collection = JournalModel.get_collection()
            res = collection.update_one(
                {"_id": obj_id, "user_id": user_id, "deleted": False},
                {"$set": {"deleted": True, "updated_at": datetime.now()}}
            )
            return res.modified_count > 0
        except Exception as e:
            logger.error("Error soft-deleting journal entry %s: %s", entry_id, e)
            return False
