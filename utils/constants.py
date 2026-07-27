"""
utils/constants.py
==================
Single source of truth for all Luma domain constants.

All services, models, and routes must import from here instead of
defining their own local mappings. This ensures consistent behaviour
across the intelligence engine, mood service, and future analytics modules.
"""

# ── Moods ────────────────────────────────────────────────────────────────────

ALLOWED_MOODS = [
    "Happy",
    "Calm",
    "Neutral",
    "Sad",
    "Stressed",
    "Anxious",
    "Angry",
    "Lonely",
]

# Wellness delta scores per mood.
# Used by IntelligenceService.compute_wellness_score() and dashboard.
MOOD_WELLNESS_SCORES = {
    "Happy":   2,
    "Calm":    1,
    "Neutral": 0,
    "Sad":    -2,
    "Stressed": -2,
    "Anxious": -3,
    "Angry":  -2,
    "Lonely": -2,
}

# Legacy 1-5 scale kept for backward compatibility with manual check-ins.
# New AI-detected entries use MOOD_WELLNESS_SCORES directly.
MOOD_LEGACY_SCORES = {
    "Happy":    5,
    "Calm":     4,
    "Neutral":  3,
    "Sad":      2,
    "Stressed": 1,
    "Anxious":  1,
    "Angry":    1,
    "Lonely":   2,
}

# ── Wellness Labels ───────────────────────────────────────────────────────────

# Maps wellness score thresholds to human-readable wellness language.
# Used by IntelligenceService.wellness_label() and dashboard route.
# Evaluated top-to-bottom: first matching threshold wins.
WELLNESS_LABEL_THRESHOLDS = [
    (2,   "Thriving"),
    (1,   "Stable"),
    (0,   "Recovering"),
    (None, "Needs Attention"),   # catch-all for any score < 0
]

# ── Recommendation Types ──────────────────────────────────────────────────────

RECOMMENDATION_TYPES = [
    "breathing",
    "meditation",
    "music",
    "journal",
    "focus",
    "sleep",
    "gratitude",
]

# ── Sentiment Values ──────────────────────────────────────────────────────────

SENTIMENT_VALUES = ["Positive", "Neutral", "Negative"]

# ── Risk Levels ───────────────────────────────────────────────────────────────

RISK_LEVELS = ["low", "medium", "high"]

# ── Mood Log Throttling ───────────────────────────────────────────────────────

# Minimum elapsed time (in minutes) before a new AI mood log entry is created
# for the same mood.  High-risk or mood-change events always bypass this limit.
MOOD_LOG_MIN_INTERVAL_MINUTES = 30

# ── Emotion Analysis Defaults ─────────────────────────────────────────────────

# Returned when Groq fails or returns malformed JSON, so the app never crashes.
DEFAULT_EMOTION = {
    "primary_mood":         "Neutral",
    "confidence":           0.5,
    "stress_level":         5,
    "sentiment":            "Neutral",
    "keywords":             [],
    "risk_level":           "low",
    "recommendation_types": ["meditation"],
    "dominant_topic":       "general",
    "emotion_reason":       "Unable to analyse emotion at this time.",
}
