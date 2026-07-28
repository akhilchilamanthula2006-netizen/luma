from datetime import datetime
from bson.objectid import ObjectId
from services.mongo_service import MongoService

class UserModel:
    """
    User model class outlining properties and helper methods for database operations.
    """
    def __init__(self, username: str, email: str, password_hash: str, id: str = None, created_at: datetime = None, 
                 bio: str = "", avatar: str = "", theme: str = "light", 
                 notifications_enabled: bool = True, ai_personalization_enabled: bool = True):
        self.id = id
        self.username = username
        self.email = email
        self.password_hash = password_hash
        self.created_at = created_at or datetime.utcnow()
        self.bio = bio
        self.avatar = avatar
        self.theme = theme
        self.notifications_enabled = notifications_enabled
        self.ai_personalization_enabled = ai_personalization_enabled

    def to_dict(self) -> dict:
        return {
            "username": self.username,
            "email": self.email,
            "password_hash": self.password_hash,
            "created_at": self.created_at,
            "bio": self.bio,
            "avatar": self.avatar,
            "theme": self.theme,
            "notifications_enabled": self.notifications_enabled,
            "ai_personalization_enabled": self.ai_personalization_enabled
        }

    @staticmethod
    def get_collection():
        db = MongoService.get_db()
        if db is None:
            raise RuntimeError("Database connection not initialized.")
        return db["users"]

    @classmethod
    def from_dict(cls, data: dict):
        if not data:
            return None
        return cls(
            id=str(data.get("_id")),
            username=data.get("username"),
            email=data.get("email"),
            password_hash=data.get("password_hash"),
            created_at=data.get("created_at"),
            bio=data.get("bio", ""),
            avatar=data.get("avatar", ""),
            theme=data.get("theme", "light"),
            notifications_enabled=data.get("notifications_enabled", True),
            ai_personalization_enabled=data.get("ai_personalization_enabled", True)
        )

    @classmethod
    def find_by_id(cls, user_id: str):
        collection = cls.get_collection()
        user_data = collection.find_one({"_id": ObjectId(user_id)})
        return cls.from_dict(user_data)

    @classmethod
    def find_by_email(cls, email: str):
        collection = cls.get_collection()
        user_data = collection.find_one({"email": email.lower().strip()})
        return cls.from_dict(user_data)

    @classmethod
    def find_by_username(cls, username: str):
        collection = cls.get_collection()
        user_data = collection.find_one({"username": username.strip()})
        return cls.from_dict(user_data)

    @classmethod
    def create(cls, username: str, email: str, password_hash: str):
        collection = cls.get_collection()
        user = cls(
            username=username.strip(),
            email=email.lower().strip(),
            password_hash=password_hash
        )
        result = collection.insert_one(user.to_dict())
        user.id = str(result.inserted_id)
        return user

    @classmethod
    def update_profile(cls, user_id: str, name: str, bio: str, avatar: str = None):
        collection = cls.get_collection()
        update_data = {"username": name, "bio": bio}
        if avatar is not None:
            update_data["avatar"] = avatar
        collection.update_one({"_id": ObjectId(user_id)}, {"$set": update_data})

    @classmethod
    def update_settings(cls, user_id: str, theme: str, notifications_enabled: bool, ai_personalization_enabled: bool):
        collection = cls.get_collection()
        update_data = {
            "theme": theme,
            "notifications_enabled": notifications_enabled,
            "ai_personalization_enabled": ai_personalization_enabled
        }
        collection.update_one({"_id": ObjectId(user_id)}, {"$set": update_data})

    @classmethod
    def update_password(cls, user_id: str, password_hash: str):
        collection = cls.get_collection()
        collection.update_one({"_id": ObjectId(user_id)}, {"$set": {"password_hash": password_hash}})

