"""
routes/chat.py
==============
Chat blueprint — GET /chat/ and POST /chat/send.

This file contains **no AI logic**.  It only:
  1. Guards routes with session checks.
  2. Parses and validates the incoming request.
  3. Orchestrates service calls (ChatHistoryModel, MoodService, AIService).
  4. Returns the appropriate response (rendered template or JSON).
"""

import logging
from datetime import datetime, timezone

from flask import (
    Blueprint,
    jsonify,
    redirect,
    render_template,
    request,
    session,
    url_for,
)

from config import Config
from models.chat_history_model import ChatHistoryModel
from services.ai_service import AIService
from services.mood_service import MoodService

logger = logging.getLogger(__name__)

chat_bp = Blueprint("chat", __name__, url_prefix="/chat")


@chat_bp.route("/")
def index():
    """Render the chat page with the user's 20 most recent messages."""
    if "user_id" not in session:
        return redirect(url_for("auth.login"))

    user_id = session["user_id"]
    history = ChatHistoryModel.get_recent(user_id, limit=20)

    return render_template("chat/index.html", history=history)


@chat_bp.route("/send", methods=["POST"])
def send():
    """
    Receive a user message, call the AI, persist both sides, and return JSON.

    Response shape (200):
        { "reply": str, "timestamp": str }

    Error shape (4xx / 503):
        { "error": str }

    Ordering contract
    -----------------
    History is loaded *before* the user message is saved so that the message
    list sent to the AI does not contain the current user turn twice (it is
    appended explicitly inside AIService.chat()).
    """
    if "user_id" not in session:
        return jsonify({"error": "Not authenticated."}), 401

    user_id  = session["user_id"]
    username = session.get("username", "")

    data = request.get_json(silent=True) or {}
    user_message = (data.get("message") or "").strip()

    if not user_message:
        return jsonify({"error": "Message cannot be empty."}), 400

    # ── 1. Load context before saving the current message ────────────────────
    try:
        latest_mood = MoodService.get_latest_mood(user_id)
        mood_label  = latest_mood.mood if latest_mood else None
    except Exception as exc:
        logger.warning("Could not retrieve latest mood for user %s: %s", user_id, exc)
        mood_label = None

    try:
        history = ChatHistoryModel.get_recent(user_id, limit=20)
    except Exception as exc:
        logger.error("Failed to load chat history for user %s: %s", user_id, exc)
        history = []

    # ── 2. Persist the user's message ────────────────────────────────────────
    try:
        ChatHistoryModel.save(user_id, role="user", content=user_message)
    except Exception as exc:
        logger.error("Failed to save user message for %s: %s", user_id, exc)
        # Non-fatal — continue to call the AI even if persistence failed

    # ── 3. Call the AI service ────────────────────────────────────────────────
    reply, error = AIService.chat(username, mood_label, history, user_message)

    if error:
        logger.warning("AI service returned error for user %s: %s", user_id, error)
        return jsonify({"error": error}), 503

    # ── 4. Persist the assistant's reply (include model for audit trail) ─────
    try:
        ChatHistoryModel.save(
            user_id,
            role="assistant",
            content=reply,
            model=Config.GROQ_MODEL,
        )
    except Exception as exc:
        logger.error("Failed to save assistant reply for %s: %s", user_id, exc)

    timestamp = datetime.now(timezone.utc).strftime("%I:%M %p")
    return jsonify({"reply": reply, "timestamp": timestamp})
