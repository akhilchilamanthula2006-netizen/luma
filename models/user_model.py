from datetime import datetime
from services.mongo_service import MongoService

class UserModel:
    """
    User model class outlining properties and helper methods for database operations.
    """
    def __init__(self, username: str, email: str, password_hash: str, id: str = None, created_at: datetime = None):
        self.id = id
        self.username = username
        self.email = email
        self.password_hash = password_hash
        self.created_at = created_at or datetime.utcnow()

    def to_dict(self) -> dict:
        return {
            "username": self.username,
            "email": self.email,
            "password_hash": self.password_hash,
            "created_at": self.created_at
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
            created_at=data.get("created_at")
        )

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

