"""
models/mood_model.py
====================
Represents a single entry in the ``mood_logs`` MongoDB collection.

Schema per document
-------------------
Required (all entries):
    user_id     (str)      – owner of the log entry
    mood        (str)      – primary mood label (one of ALLOWED_MOODS)
    score       (int)      – legacy 1-5 scale (for backward compat)
    source      (str)      – "manual" | "ai_chat"
    notes       (str)      – free text; emotion_reason for AI entries
    timestamp   (datetime) – server local time of insertion

Optional (AI-detected entries only — stored for future analytics):
    confidence          (float)  – 0.0–1.0 model confidence
    stress_level        (int)    – 1–10
    sentiment           (str)    – Positive | Neutral | Negative
    keywords            (list)   – emotional/context keywords
    risk_level          (str)    – low | medium | high
    recommendation_types(list)   – e.g. ["breathing", "meditation"]
    dominant_topic      (str)    – short topic phrase
    emotion_reason      (str)    – one-sentence explanation

Old manual-check-in documents that lack the optional fields are still
fully readable via ``from_dict()`` — all new fields default safely.
"""

from datetime import datetime
from services.mongo_service import MongoService


class MoodModel:
    """Mood log entry. Supports both manual and AI-chat sources."""

    def __init__(
        self,
        user_id: str,
        mood: str,
        score: int,
        source: str = "manual",
        notes: str = "",
        timestamp: datetime = None,
        id: str = None,
        # Extended AI emotion fields (optional)
        confidence: float = None,
        stress_level: int = None,
        sentiment: str = None,
        keywords: list = None,
        risk_level: str = None,
        recommendation_types: list = None,
        dominant_topic: str = None,
        emotion_reason: str = None,
    ):
        self.id                   = id
        self.user_id              = user_id
        self.mood                 = mood
        self.score                = score
        self.source               = source
        self.notes                = notes
        self.timestamp            = timestamp or datetime.now()

        # Extended fields — only populated for ai_chat entries
        self.confidence           = confidence
        self.stress_level         = stress_level
        self.sentiment            = sentiment
        self.keywords             = keywords or []
        self.risk_level           = risk_level
        self.recommendation_types = recommendation_types or []
        self.dominant_topic       = dominant_topic
        self.emotion_reason       = emotion_reason

    def to_dict(self) -> dict:
        """
        Serialise to a MongoDB document dict.

        Core fields are always included.
        Extended fields are included only when they are not None so that
        manual-check-in documents remain lean.
        """
        doc = {
            "user_id":   self.user_id,
            "mood":      self.mood,
            "score":     self.score,
            "source":    self.source,
            "notes":     self.notes,
            "timestamp": self.timestamp,
        }

        # Append extended fields only when present
        if self.confidence is not None:
            doc["confidence"] = self.confidence
        if self.stress_level is not None:
            doc["stress_level"] = self.stress_level
        if self.sentiment is not None:
            doc["sentiment"] = self.sentiment
        if self.keywords:
            doc["keywords"] = self.keywords
        if self.risk_level is not None:
            doc["risk_level"] = self.risk_level
        if self.recommendation_types:
            doc["recommendation_types"] = self.recommendation_types
        if self.dominant_topic is not None:
            doc["dominant_topic"] = self.dominant_topic
        if self.emotion_reason is not None:
            doc["emotion_reason"] = self.emotion_reason

        return doc

    @classmethod
    def from_dict(cls, data: dict):
        """
        Deserialise from a MongoDB document.

        Handles both legacy manual-check-in documents (no extended fields)
        and new AI-chat documents (with extended fields) safely.
        """
        if not data:
            return None
        return cls(
            id=str(data.get("_id")),
            user_id=data.get("user_id"),
            mood=data.get("mood"),
            score=data.get("score"),
            source=data.get("source", "manual"),
            notes=data.get("notes", ""),
            timestamp=data.get("timestamp"),
            # Extended fields — default to None if absent (old documents)
            confidence=data.get("confidence"),
            stress_level=data.get("stress_level"),
            sentiment=data.get("sentiment"),
            keywords=data.get("keywords", []),
            risk_level=data.get("risk_level"),
            recommendation_types=data.get("recommendation_types", []),
            dominant_topic=data.get("dominant_topic"),
            emotion_reason=data.get("emotion_reason"),
        )

    @staticmethod
    def get_collection():
        db = MongoService.get_db()
        if db is None:
            raise RuntimeError("Database connection not initialized.")
        return db["mood_logs"]
