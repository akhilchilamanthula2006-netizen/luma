import logging
from pymongo import MongoClient
from config import Config

logger = logging.getLogger(__name__)

class MongoService:
    """
    Service to manage MongoDB connections and database client access.
    MongoDB connection is currently deferred to avoid initial runtime dependency.
    """
    _client = None
    _db = None

    @classmethod
    def get_db(cls):
        """
        Lazily initializes and returns the database instance.
        Currently returns None or mocks behavior until MongoDB integration is activated.
        """
        if cls._db is None:
            try:
                cls._client = MongoClient(Config.MONGO_URI)
                # Get db name from URI or default to 'luma_db'
                # If URI has query params (e.g. ?authSource=admin), split before that or search path
                path = Config.MONGO_URI.split('/')[-1]
                db_name = path.split('?')[0] or 'luma_db'
                cls._db = cls._client[db_name]
                logger.info(f"Successfully connected to MongoDB database: {db_name}")
            except Exception as e:
                logger.error(f"Failed to connect to MongoDB: {e}")
                raise e
        return cls._db
