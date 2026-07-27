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
from models.conversation_model import ConversationModel
from services.intelligence_service import IntelligenceService
from services.mood_service import MoodService
from services.conversation_service import ConversationService

logger = logging.getLogger(__name__)

chat_bp = Blueprint("chat", __name__, url_prefix="/chat")


@chat_bp.route("/")
def index():
    """Render the chat page. If conversations exist, redirect to the most recent one."""
    if "user_id" not in session:
        return redirect(url_for("auth.login"))

    user_id = session["user_id"]

    # Pre-load conversations for the sidebar
    conversations_grouped = ConversationService.list_conversations(user_id)

    # If the user has conversations, redirect to the most recent one.
    most_recent_id = None
    if conversations_grouped["today"]:
        most_recent_id = conversations_grouped["today"][0]["id"]
    elif conversations_grouped["yesterday"]:
        most_recent_id = conversations_grouped["yesterday"][0]["id"]
    elif conversations_grouped["previous"]:
        most_recent_id = conversations_grouped["previous"][0]["id"]

    if most_recent_id:
        return redirect(url_for("chat.chat_conversation", conversation_id=most_recent_id))

    # Empty state
    return render_template(
        "chat/index.html",
        history=[],
        conversations=conversations_grouped,
        active_conversation_id=None
    )


@chat_bp.route("/<conversation_id>")
def chat_conversation(conversation_id):
    """Render a specific conversation."""
    if "user_id" not in session:
        return redirect(url_for("auth.login"))

    user_id = session["user_id"]

    # Verify ownership
    conv_metadata = ConversationService.load_conversation(conversation_id, user_id)
    if not conv_metadata:
        return redirect(url_for("chat.index"))

    conversations_grouped = ConversationService.list_conversations(user_id)
    history = ChatHistoryModel.get_by_conversation(conversation_id)

    return render_template(
        "chat/index.html",
        history=history,
        conversations=conversations_grouped,
        active_conversation_id=conversation_id
    )


@chat_bp.route("/send", methods=["POST"])
def send():
    """
    Receive a user message, run intelligence analysis, persist everything,
    and return JSON including the reply and emotion data for the frontend.

    Flow
    ----
    1. Validate auth + conversation ownership
    2. Load context (latest mood, chat history) BEFORE saving the new message
    3. Persist the user's message
    4. Call IntelligenceService.analyze() — single API call, returns reply + emotion
    5. Persist the assistant reply
    6. Log AI-detected mood (throttled via MoodService.log_mood_from_ai)
    7. Update conversation emotion metadata
    8. Auto-generate title on first exchange
    9. Return JSON with reply, emotion summary, and risk data for the frontend
    """
    if "user_id" not in session:
        return jsonify({"error": "Not authenticated."}), 401

    user_id  = session["user_id"]
    username = session.get("username", "")

    data            = request.get_json(silent=True) or {}
    user_message    = (data.get("message") or "").strip()
    conversation_id = (data.get("conversation_id") or "").strip()

    if not user_message:
        return jsonify({"error": "Message cannot be empty."}), 400

    if not conversation_id:
        return jsonify({"error": "No conversation selected."}), 400

    # ── 1. Verify conversation ownership ─────────────────────────────────────
    conv_metadata = ConversationService.load_conversation(conversation_id, user_id)
    if not conv_metadata:
        return jsonify({"error": "Conversation not found."}), 404

    # ── 2. Load context before saving the current message ────────────────────
    try:
        latest_mood = MoodService.get_latest_mood(user_id)
        mood_label  = latest_mood.mood if latest_mood else None
    except Exception as exc:
        logger.warning("Could not retrieve latest mood for user %s: %s", user_id, exc)
        mood_label = None

    try:
        history = ChatHistoryModel.get_by_conversation(conversation_id)
    except Exception as exc:
        logger.error("Failed to load chat history for conv %s: %s", conversation_id, exc)
        history = []

    # ── 3. Persist the user's message ────────────────────────────────────────
    try:
        ConversationService.record_message(user_id, conversation_id, "user", user_message)
    except Exception as exc:
        logger.error("Failed to save user message for %s: %s", user_id, exc)

    # ── 4. Intelligence analysis (reply + emotion in one API call) ────────────
    reply, emotion, error = IntelligenceService.analyze(
        username, mood_label, history, user_message
    )

    if error:
        logger.warning("IntelligenceService error for user %s: %s", user_id, error)
        return jsonify({"error": error}), 503

    # ── 5. Persist the assistant's reply ─────────────────────────────────────
    try:
        ConversationService.record_message(
            user_id,
            conversation_id,
            "assistant",
            reply,
            Config.GROQ_MODEL
        )
    except Exception as exc:
        logger.error("Failed to save assistant reply for %s: %s", user_id, exc)

    # ── 6. Log AI-detected mood (throttled) ───────────────────────────────────
    try:
        MoodService.log_mood_from_ai(user_id, emotion)
    except Exception as exc:
        logger.warning("Failed to log AI mood for user %s: %s", user_id, exc)

    # ── 7. Update conversation emotion metadata ───────────────────────────────
    try:
        ConversationModel.update_emotion_metadata(conversation_id, emotion)
    except Exception as exc:
        logger.warning("Failed to update conversation emotion metadata: %s", exc)

    # ── 8. Auto-generate title on first exchange ──────────────────────────────
    generated_title = None
    if conv_metadata.get("message_count", 0) == 0:
        generated_title = ConversationService.generate_title(user_message)
        ConversationModel.set_title(conversation_id, generated_title)

    # ── 9. Build response ─────────────────────────────────────────────────────
    timestamp = datetime.now(timezone.utc).strftime("%I:%M %p")

    response_data = {
        "reply":                reply,
        "timestamp":            timestamp,
        "last_message":         reply,
        # Emotion summary for the frontend (crisis detection, UI hints)
        "risk_level":           emotion["risk_level"],
        "recommendation_types": emotion["recommendation_types"],
        "primary_mood":         emotion["primary_mood"],
        "sentiment":            emotion["sentiment"],
    }
    if generated_title:
        response_data["title"] = generated_title

    return jsonify(response_data)
