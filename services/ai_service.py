"""
services/ai_service.py
======================
Central AI service for all Groq API communication.

Architecture
------------
``_call_groq()`` is the single, reusable primitive that owns the Groq client,
handles every error class, and returns a plain (text, error) tuple.

All feature-specific methods — chat(), and future modules like
analyze_mood_journal(), generate_wellness_tip(), analyse_sentiment() —
compose their own message lists and delegate to ``_call_groq()``.
This keeps every caller free from duplicating client logic, timeout
handling, or error mapping.
"""

import logging
from config import Config

logger = logging.getLogger(__name__)


class AIService:
    """Groq-backed AI service for Luma's feature modules."""

    # ── Constants ────────────────────────────────────────────────────────────────

    # Maximum number of historical messages forwarded to the model.
    # Older messages beyond this limit are dropped to avoid hitting the
    # context window as conversations grow.
    MAX_CONTEXT_MESSAGES = 10

    # Reusable system prompt with {username} and {mood} placeholders.
    # Keeps the core persona in one place; only context is injected at call time.
    BASE_SYSTEM_PROMPT = (
        "You are Luma, an empathetic AI mental wellness companion. "
        "Your role is to listen with compassion, ask thoughtful questions, "
        "and help the user reflect on their emotions and experiences. "
        "You do not provide medical advice, clinical diagnoses, or treatment "
        "recommendations of any kind. "
        "Always encourage the user to seek professional support when topics "
        "feel serious or urgent. "
        "Keep your responses warm, concise (2–4 sentences unless more depth "
        "is genuinely needed), and grounded in what the user actually said — "
        "avoid generic platitudes. "
        "The user's name is {username}. "
        "Their most recently recorded mood is: {mood}."
    )

    _client = None  # Lazy-initialised Groq client (one instance per process)

    # ── Client ───────────────────────────────────────────────────────────────────

    @classmethod
    def _get_client(cls):
        """
        Lazily create the Groq client on first use.
        Importing groq here (not at module level) keeps the rest of the app
        importable even before ``pip install groq`` has been run.
        """
        if cls._client is None:
            from groq import Groq
            cls._client = Groq(api_key=Config.GROQ_API_KEY)
        return cls._client

    # ── Core primitive ───────────────────────────────────────────────────────────

    @classmethod
    def _call_groq(cls, messages: list, max_tokens: int = 512) -> tuple:
        """
        Send a fully-formed message list to Groq and return ``(reply, error)``.

        This is the **only** place in the codebase that calls the Groq API.
        All feature methods compose their message lists and delegate here.

        Returns
        -------
        (str, None)
            On success: the assistant's reply text and no error.
        ("", str)
            On failure: empty string and a user-friendly error message.
            Detailed context is always logged server-side.
        """
        # Import error classes inside the method for the same reason as _get_client
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
                max_tokens=max_tokens,
                temperature=0.7,
            )
            reply = completion.choices[0].message.content.strip()
            logger.info(
                "Groq call succeeded — model=%s tokens_in_prompt=%s",
                Config.GROQ_MODEL,
                len(messages),
            )
            return reply, None

        except AuthenticationError as exc:
            logger.error("Groq authentication error: %s", exc)
            return "", (
                "Luma is temporarily unavailable due to a configuration issue. "
                "Please contact support."
            )

        except RateLimitError as exc:
            logger.warning("Groq rate limit reached: %s", exc)
            return "", (
                "Luma is a little overwhelmed right now. "
                "Please try again in a moment."
            )

        except APITimeoutError as exc:
            logger.warning("Groq request timed out: %s", exc)
            return "", "Luma took too long to respond. Please try again."

        except APIConnectionError as exc:
            logger.error("Groq connection error: %s", exc)
            return "", (
                "Luma couldn't reach the AI service. "
                "Please check your connection and try again."
            )

        except APIStatusError as exc:
            logger.error(
                "Groq API status error %s: %s", exc.status_code, exc.message
            )
            return "", "Luma encountered an unexpected error. Please try again shortly."

        except Exception as exc:  # noqa: BLE001
            logger.exception("Unexpected error calling Groq: %s", exc)
            return "", "Something went wrong. Please try again."

    # ── System prompt ────────────────────────────────────────────────────────────

    @staticmethod
    def build_system_prompt(username: str, mood_label: str | None) -> str:
        """
        Inject ``username`` and ``mood_label`` into ``BASE_SYSTEM_PROMPT``.

        Falls back gracefully when either value is absent so the prompt
        is never left with unformatted placeholders.
        """
        return AIService.BASE_SYSTEM_PROMPT.format(
            username=username or "there",
            mood=mood_label or "not recorded yet",
        )

    # ── Chat feature ─────────────────────────────────────────────────────────────

    @classmethod
    def chat(
        cls,
        username: str,
        mood_label: str | None,
        history: list,
        user_message: str,
    ) -> tuple:
        """
        Build a Groq-format message list and call the AI.

        History is trimmed to the last ``MAX_CONTEXT_MESSAGES`` entries before
        sending so the context window stays bounded as conversations grow.
        The caller is responsible for loading history *before* persisting the
        current user message so it does not appear twice.

        Parameters
        ----------
        username:
            The logged-in user's display name.
        mood_label:
            Latest mood string (e.g. ``"Happy"``) or ``None``.
        history:
            List of dicts with ``role`` and ``content`` keys from MongoDB,
            already in chronological (oldest-first) order.
        user_message:
            The new message typed by the user.

        Returns
        -------
        (reply_text, None)  on success
        ("", error_string)  on failure
        """
        system_prompt = cls.build_system_prompt(username, mood_label)

        # Trim to avoid exceeding context limits on long conversations
        trimmed = (
            history[-cls.MAX_CONTEXT_MESSAGES :]
            if len(history) > cls.MAX_CONTEXT_MESSAGES
            else history
        )

        messages = [
            {"role": "system", "content": system_prompt},
            *[{"role": m["role"], "content": m["content"]} for m in trimmed],
            {"role": "user", "content": user_message},
        ]

        return cls._call_groq(messages, max_tokens=512)

    # ── Journal analysis stub ────────────────────────────────────────────────────

    @staticmethod
    def analyze_mood_journal(entry_text: str) -> dict:
        """
        Analyse a journal entry for sentiment and emotional content.

        Stub preserved for the Journal Integration milestone.
        When implemented, it will compose a structured prompt and call
        ``_call_groq()`` — no duplication of client logic required.
        """
        logger.info(
            "AI journal analysis requested for entry of length %d", len(entry_text)
        )
        return {
            "sentiment": "Neutral",
            "score": 0.5,
            "detected_emotions": ["calm"],
            "suggested_action": "Continue reflecting on your feelings.",
        }
