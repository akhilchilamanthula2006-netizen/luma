"""
services/mood_service.py
========================
Service for managing mood tracking data.

Handles both manual check-ins (always written, source='manual') and
AI-detected moods (throttled, source='ai_chat').

All score constants are sourced from utils.constants so there is no
duplication between this service and the intelligence engine.
"""

import logging
from datetime import datetime, timedelta

import pymongo

from models.mood_model import MoodModel
from utils.constants import (
    ALLOWED_MOODS,
    MOOD_LEGACY_SCORES,
    MOOD_LOG_MIN_INTERVAL_MINUTES,
)

logger = logging.getLogger(__name__)


class MoodService:
    """
    Service for managing mood tracking data and mapping scores.

    Manual check-ins
    ----------------
    Handled by ``log_mood()``. Always writes (upserts today's entry).
    Source tag: ``"manual"``.

    AI-detected moods
    -----------------
    Handled by ``log_mood_from_ai()``. Uses throttle logic to avoid flooding
    the collection with identical entries. A new document is written only when:
        - No prior log exists, OR
        - Detected mood differs from the last logged mood, OR
        - Last log is older than MOOD_LOG_MIN_INTERVAL_MINUTES, OR
        - risk_level is "high" (always logs crisis states).
    Source tag: ``"ai_chat"``.
    """

    # ── Legacy score map (1-5 scale, kept for manual check-in backward compat) ──

    MOOD_SCORE_MAP = MOOD_LEGACY_SCORES

    # ── Helpers ───────────────────────────────────────────────────────────────

    @classmethod
    def get_score_for_mood(cls, mood: str) -> int:
        """Return the legacy 1-5 score for a mood (manual check-in scale)."""
        return cls.MOOD_SCORE_MAP.get(mood, 3)

    # ── Manual check-in ───────────────────────────────────────────────────────

    @classmethod
    def log_mood(cls, user_id: str, mood: str, notes: str = "") -> dict:
        """
        Log a mood from an explicit manual user check-in.

        Checks if a mood log already exists for today (server local time)
        and updates it; otherwise inserts a new record.

        This method always writes — no throttling — because the user made
        a deliberate choice. Manual entries use source='manual'.

        Parameters
        ----------
        user_id : str
        mood    : str  — must be one of ALLOWED_MOODS
        notes   : str  — optional free-text note

        Returns
        -------
        {"status": "success", "action": "created"|"updated", "mood": str}
        """
        if mood not in ALLOWED_MOODS:
            logger.warning("MoodService.log_mood: unknown mood '%s', defaulting to Neutral", mood)
            mood = "Neutral"

        score = cls.get_score_for_mood(mood)
        collection = MoodModel.get_collection()

        now = datetime.now()
        start_of_day = now.replace(hour=0, minute=0, second=0, microsecond=0)
        end_of_day = now.replace(hour=23, minute=59, second=59, microsecond=999999)

        existing_log = collection.find_one({
            "user_id": user_id,
            "source": "manual",
            "timestamp": {"$gte": start_of_day, "$lte": end_of_day}
        })

        if existing_log:
            collection.update_one(
                {"_id": existing_log["_id"]},
                {"$set": {
                    "mood":      mood,
                    "score":     score,
                    "notes":     notes,
                    "timestamp": now,
                }}
            )
            action = "updated"
        else:
            new_log = MoodModel(
                user_id=user_id,
                mood=mood,
                score=score,
                source="manual",
                notes=notes,
                timestamp=now,
            )
            collection.insert_one(new_log.to_dict())
            action = "created"

        logger.info("MoodService.log_mood: %s manual mood '%s' for user %s", action, mood, user_id)
        return {"status": "success", "action": action, "mood": mood}

    # ── AI-detected mood ──────────────────────────────────────────────────────

    @classmethod
    def log_mood_from_ai(cls, user_id: str, emotion: dict) -> dict:
        """
        Log a mood detected by IntelligenceService, applying throttle logic.

        A new document is written only if:
            1. No prior log exists at all, OR
            2. Detected mood differs from the last logged mood, OR
            3. Last log is older than MOOD_LOG_MIN_INTERVAL_MINUTES, OR
            4. risk_level == "high" (always record crisis events).

        All extended emotion fields (confidence, stress_level, etc.) are
        stored so future analytics can reuse them without schema migration.

        Parameters
        ----------
        user_id : str
        emotion : dict — validated emotion dict from IntelligenceService

        Returns
        -------
        {"status": "skipped"|"created", "reason": str}
        """
        primary_mood  = emotion.get("primary_mood", "Neutral")
        risk_level    = emotion.get("risk_level", "low")
        collection    = MoodModel.get_collection()

        # Fetch the most recent log for this user (any source)
        last = collection.find_one(
            {"user_id": user_id},
            sort=[("timestamp", pymongo.DESCENDING)]
        )

        should_log, reason = cls._should_log_ai_mood(last, primary_mood, risk_level)

        if not should_log:
            logger.debug(
                "MoodService.log_mood_from_ai: skipped for user %s — %s", user_id, reason
            )
            return {"status": "skipped", "reason": reason}

        score = cls.get_score_for_mood(primary_mood)
        now   = datetime.now()

        doc = MoodModel(
            user_id=user_id,
            mood=primary_mood,
            score=score,
            source="ai_chat",
            notes=emotion.get("emotion_reason", ""),
            timestamp=now,
        ).to_dict()

        # Extend with full emotion payload for future analytics
        doc.update({
            "confidence":           emotion.get("confidence", 0.5),
            "stress_level":         emotion.get("stress_level", 5),
            "sentiment":            emotion.get("sentiment", "Neutral"),
            "keywords":             emotion.get("keywords", []),
            "risk_level":           risk_level,
            "recommendation_types": emotion.get("recommendation_types", []),
            "dominant_topic":       emotion.get("dominant_topic", ""),
            "emotion_reason":       emotion.get("emotion_reason", ""),
        })

        collection.insert_one(doc)
        logger.info(
            "MoodService.log_mood_from_ai: created ai_chat mood '%s' for user %s (reason: %s)",
            primary_mood, user_id, reason,
        )
        return {"status": "created", "reason": reason}

    # ── Throttle decision ─────────────────────────────────────────────────────

    @staticmethod
    def _should_log_ai_mood(last_doc: dict | None, detected_mood: str, risk_level: str) -> tuple:
        """
        Decide whether a new AI mood log entry should be written.

        Returns (should_log: bool, reason: str).
        """
        if last_doc is None:
            return True, "no prior log exists"

        if risk_level == "high":
            return True, "risk_level is high"

        if last_doc.get("mood") != detected_mood:
            return True, f"mood changed from '{last_doc.get('mood')}' to '{detected_mood}'"

        last_ts = last_doc.get("timestamp")
        if last_ts:
            elapsed = (datetime.now() - last_ts).total_seconds() / 60
            if elapsed >= MOOD_LOG_MIN_INTERVAL_MINUTES:
                return True, f"{elapsed:.0f} minutes elapsed since last log"

        return False, "mood unchanged and within throttle window"

    # ── Queries ───────────────────────────────────────────────────────────────

    @classmethod
    def get_latest_mood(cls, user_id: str) -> MoodModel:
        """Retrieve the most recent mood log for a user (any source)."""
        collection = MoodModel.get_collection()
        latest = collection.find_one(
            {"user_id": user_id},
            sort=[("timestamp", pymongo.DESCENDING)]
        )
        return MoodModel.from_dict(latest) if latest else None

    @classmethod
    def get_recent_moods(cls, user_id: str, limit: int = 7) -> list:
        """
        Return the last ``limit`` mood log entries for a user.

        Useful for the weekly mood path chart and future analytics.
        Documents are returned in chronological order (oldest first).
        """
        collection = MoodModel.get_collection()
        cursor = (
            collection
            .find({"user_id": user_id})
            .sort("timestamp", pymongo.DESCENDING)
            .limit(limit)
        )
        docs = list(cursor)
        docs.reverse()
        return [MoodModel.from_dict(d) for d in docs]
