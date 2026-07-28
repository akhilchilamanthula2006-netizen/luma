"""
services/intelligence_service.py
=================================
AI Wellness Intelligence Engine — the single intelligence layer for Luma.

Architecture
------------
Every user chat message is processed here in one Groq API call that returns
BOTH a conversational reply AND structured emotion data in a JSON object.

Groq's ``response_format={"type": "json_object"}`` is used so the model is
constrained to valid JSON output — no delimiter hacks, no regex parsing.

The system prompt embeds a strict JSON schema that the model must follow.
The reply to the user lives inside the JSON as the ``"reply"`` field.

All other services (MoodService, future Analytics, future Journal) consume
the emotion dict returned here — no duplicate analysis logic anywhere else.

Usage
-----
    reply, emotion, error = IntelligenceService.analyze(
        username, mood_label, history, user_message
    )

    score = IntelligenceService.compute_wellness_score(emotion["primary_mood"])
    label = IntelligenceService.wellness_label(score)
"""

import json
import logging

from config import Config
from utils.constants import (
    ALLOWED_MOODS,
    DEFAULT_EMOTION,
    MOOD_WELLNESS_SCORES,
    RECOMMENDATION_TYPES,
    RISK_LEVELS,
    SENTIMENT_VALUES,
    WELLNESS_LABEL_THRESHOLDS,
)

logger = logging.getLogger(__name__)

# Number of historical messages forwarded to the model.
MAX_CONTEXT_MESSAGES = 10

# ── System Prompt ─────────────────────────────────────────────────────────────

_SYSTEM_PROMPT_TEMPLATE = """\
You are Luma, an empathetic AI mental wellness companion.
Your role is to listen with compassion, ask thoughtful follow-up questions, \
and help the user reflect on their emotions and experiences.
You do NOT provide medical advice, clinical diagnoses, or treatment \
recommendations of any kind.
Always encourage the user to seek professional support when topics feel \
serious or urgent.
Keep your replies warm, concise (2–4 sentences unless more depth is genuinely \
needed), and grounded in what the user actually said — avoid generic platitudes.

The user's name is {username}.
Their most recently recorded mood is: {mood}.
Unified Wellness Signals: {wellness_signals}

──────────────────────────────────────────────────────────
IMPORTANT — OUTPUT FORMAT
──────────────────────────────────────────────────────────
You MUST respond with a single valid JSON object and nothing else.
Do NOT include markdown fences, explanations, or any text outside the JSON.

Required schema (all fields mandatory):

{{
  "reply": "<your warm, conversational response to the user>",
  "primary_mood": "<one of: Happy | Calm | Neutral | Sad | Stressed | Anxious | Angry | Lonely>",
  "confidence": <float 0.0–1.0>,
  "stress_level": <integer 1–10>,
  "sentiment": "<Positive | Neutral | Negative>",
  "keywords": ["<word1>", "<word2>"],
  "risk_level": "<low | medium | high>",
  "recommendation_types": ["<one or more of: breathing | meditation | music | journal | focus | sleep | gratitude>"],
  "dominant_topic": "<short phrase describing the main topic, e.g. 'work stress' or 'relationship conflict'>",
  "emotion_reason": "<one sentence explaining why you assigned this primary_mood>"
}}

Use risk_level "high" ONLY when the user expresses thoughts of self-harm, \
suicide, or severe crisis. In that case still provide a warm, supportive reply \
field — do NOT refuse to engage.
"""



class IntelligenceService:
    """
    Core AI intelligence engine for Luma.

    Responsibilities
    ----------------
    - Produce a dual-output AI response: conversational reply + emotion analysis.
    - Validate and sanitise the emotion payload against known constants.
    - Compute wellness scores and labels for the dashboard.
    - Expose clean, reusable class methods for the dashboard, analytics,
      journal, and wellness hub to consume without duplicating logic.
    """

    _client = None  # Lazy-initialised Groq client (one per process)

    # ── Client ────────────────────────────────────────────────────────────────

    @classmethod
    def _get_client(cls):
        """Lazily create the Groq client on first use."""
        if cls._client is None:
            from groq import Groq
            cls._client = Groq(api_key=Config.GROQ_API_KEY)
        return cls._client

    # ── Main entry point ──────────────────────────────────────────────────────

    @classmethod
    def analyze(
        cls,
        username: str,
        mood_label: str | None,
        history: list,
        user_message: str,
        user_id: str | None = None,
    ) -> tuple:
        wellness_str = "No recent signals"
        if user_id:
            try:
                from services.wellness.insights_service import InsightsService
                ctx = InsightsService.get_unified_wellness_context(user_id)
                score = ctx.get("score", {}).get("current", 80)
                sleep_hrs = ctx.get("summary", {}).get("sleep_hours", 7.5)
                heuristics = ", ".join(ctx.get("heuristics", [])) or "Balanced"
                wellness_str = f"Wellness Score: {score}/100, Sleep: {sleep_hrs} hrs, Heuristics: [{heuristics}]"
            except Exception as exc:
                logger.warning("Could not fetch wellness signals for user %s: %s", user_id, exc)

        system_prompt = _SYSTEM_PROMPT_TEMPLATE.format(
            username=username or "there",
            mood=mood_label or "not recorded yet",
            wellness_signals=wellness_str
        )


        trimmed_history = (
            history[-MAX_CONTEXT_MESSAGES:]
            if len(history) > MAX_CONTEXT_MESSAGES
            else history
        )

        messages = [
            {"role": "system", "content": system_prompt},
            *[{"role": m["role"], "content": m["content"]} for m in trimmed_history],
            {"role": "user", "content": user_message},
        ]

        raw_json, error = cls._call_groq_json(messages)

        if error:
            return "", dict(DEFAULT_EMOTION), error

        reply, emotion = cls._parse_response(raw_json)
        return reply, emotion, None

    # ── Groq JSON call ────────────────────────────────────────────────────────

    @classmethod
    def _call_groq_json(cls, messages: list) -> tuple:
        """
        Call Groq with JSON mode enabled and return (raw_dict, error).

        Uses response_format={"type": "json_object"} so the API guarantees
        a parseable JSON string — no delimiter splitting required.

        Returns
        -------
        (dict, None)  on success
        (None, str)   on any failure (error is a user-friendly message)
        """
        from groq import (
            AuthenticationError,
            RateLimitError,
            APITimeoutError,
            APIConnectionError,
            APIStatusError,
        )

        try:
            client = cls._get_client()
            completion = client.chat.completions.create(
                model=Config.GROQ_MODEL,
                messages=messages,
                max_tokens=768,
                temperature=0.65,
                response_format={"type": "json_object"},
            )
            raw_text = completion.choices[0].message.content.strip()
            logger.info(
                "IntelligenceService: Groq JSON call succeeded — model=%s",
                Config.GROQ_MODEL,
            )
            try:
                return json.loads(raw_text), None
            except json.JSONDecodeError as exc:
                logger.error("IntelligenceService: JSON decode failed: %s", exc)
                return None, "Luma had trouble understanding the response. Please try again."

        except AuthenticationError as exc:
            logger.error("IntelligenceService: Auth error: %s", exc)
            return None, (
                "Luma is temporarily unavailable due to a configuration issue. "
                "Please contact support."
            )
        except RateLimitError as exc:
            logger.warning("IntelligenceService: Rate limit: %s", exc)
            return None, "Luma is a little overwhelmed right now. Please try again in a moment."
        except APITimeoutError as exc:
            logger.warning("IntelligenceService: Timeout: %s", exc)
            return None, "Luma took too long to respond. Please try again."
        except APIConnectionError as exc:
            logger.error("IntelligenceService: Connection error: %s", exc)
            return None, (
                "Luma couldn't reach the AI service. "
                "Please check your connection and try again."
            )
        except APIStatusError as exc:
            logger.error(
                "IntelligenceService: API status %s: %s", exc.status_code, exc.message
            )
            return None, "Luma encountered an unexpected error. Please try again shortly."
        except Exception as exc:  # noqa: BLE001
            logger.exception("IntelligenceService: Unexpected error: %s", exc)
            return None, "Something went wrong. Please try again."

    # ── Response parsing & validation ─────────────────────────────────────────

    @classmethod
    def _parse_response(cls, raw: dict) -> tuple:
        """
        Extract and validate the reply + emotion fields from the raw JSON dict.

        Any missing or invalid field is replaced with a safe default from
        DEFAULT_EMOTION so the application never crashes on a partial response.

        Returns
        -------
        (reply: str, emotion: dict)
        """
        reply = str(raw.get("reply", "")).strip()
        if not reply:
            reply = "I'm here for you. Could you tell me a little more about how you're feeling?"

        def _str_field(key, allowed, default):
            val = raw.get(key, default)
            return val if val in allowed else default

        def _float_field(key, lo, hi, default):
            try:
                val = float(raw.get(key, default))
                return max(lo, min(hi, val))
            except (TypeError, ValueError):
                return default

        def _int_field(key, lo, hi, default):
            try:
                val = int(raw.get(key, default))
                return max(lo, min(hi, val))
            except (TypeError, ValueError):
                return default

        def _list_field(key, allowed, default):
            raw_val = raw.get(key, [])
            if not isinstance(raw_val, list):
                return default
            filtered = [v for v in raw_val if v in allowed]
            return filtered if filtered else default

        emotion = {
            "primary_mood":         _str_field("primary_mood", ALLOWED_MOODS, DEFAULT_EMOTION["primary_mood"]),
            "confidence":           _float_field("confidence", 0.0, 1.0, DEFAULT_EMOTION["confidence"]),
            "stress_level":         _int_field("stress_level", 1, 10, DEFAULT_EMOTION["stress_level"]),
            "sentiment":            _str_field("sentiment", SENTIMENT_VALUES, DEFAULT_EMOTION["sentiment"]),
            "keywords":             raw.get("keywords", []) if isinstance(raw.get("keywords"), list) else [],
            "risk_level":           _str_field("risk_level", RISK_LEVELS, DEFAULT_EMOTION["risk_level"]),
            "recommendation_types": _list_field("recommendation_types", RECOMMENDATION_TYPES, DEFAULT_EMOTION["recommendation_types"]),
            "dominant_topic":       str(raw.get("dominant_topic", DEFAULT_EMOTION["dominant_topic"])).strip() or DEFAULT_EMOTION["dominant_topic"],
            "emotion_reason":       str(raw.get("emotion_reason", DEFAULT_EMOTION["emotion_reason"])).strip() or DEFAULT_EMOTION["emotion_reason"],
        }

        return reply, emotion

    # ── Wellness helpers ──────────────────────────────────────────────────────

    @staticmethod
    def compute_wellness_score(mood: str) -> int:
        """
        Return the wellness delta score for a given mood string.

        Uses MOOD_WELLNESS_SCORES from constants.
        Falls back to 0 (Neutral) for unknown moods.
        """
        return MOOD_WELLNESS_SCORES.get(mood, 0)

    @staticmethod
    def wellness_label(score: int) -> str:
        """
        Map a numeric wellness score to a wellness-language label.

        Thresholds (evaluated top-to-bottom, first match wins):
            score >= 2  → Thriving
            score >= 1  → Stable
            score >= 0  → Recovering
            score <  0  → Needs Attention
        """
        for threshold, label in WELLNESS_LABEL_THRESHOLDS:
            if threshold is None or score >= threshold:
                return label
        return "Needs Attention"  # unreachable safety net
