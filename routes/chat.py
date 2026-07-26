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
from services.ai_service import AIService
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
    Receive a user message, call the AI, persist both sides, and return JSON.
    """
    if "user_id" not in session:
        return jsonify({"error": "Not authenticated."}), 401

    user_id  = session["user_id"]
    username = session.get("username", "")

    data = request.get_json(silent=True) or {}
    user_message = (data.get("message") or "").strip()
    conversation_id = (data.get("conversation_id") or "").strip()

    if not user_message:
        return jsonify({"error": "Message cannot be empty."}), 400
        
    if not conversation_id:
        return jsonify({"error": "No conversation selected."}), 400
        
    # Verify ownership of conversation
    conv_metadata = ConversationService.load_conversation(conversation_id, user_id)
    if not conv_metadata:
        return jsonify({"error": "Conversation not found."}), 404

    # ── 1. Load context before saving the current message ────────────────────
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

    # ── 2. Persist the user's message ────────────────────────────────────────
    try:
        ConversationService.record_message(user_id, conversation_id, "user", user_message)
    except Exception as exc:
        logger.error("Failed to save user message for %s: %s", user_id, exc)

    # ── 3. Call the AI service ────────────────────────────────────────────────
    reply, error = AIService.chat(username, mood_label, history, user_message)

    if error:
        logger.warning("AI service returned error for user %s: %s", user_id, error)
        return jsonify({"error": error}), 503

    # ── 4. Persist the assistant's reply ──────────────────────────────────────
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
        
    # ── 5. Auto-generate title if this is the first exchange ──────────────────
    generated_title = None
    if conv_metadata.get("message_count", 0) == 0:
        generated_title = ConversationService.generate_title(user_message)
        ConversationModel.set_title(conversation_id, generated_title)

    timestamp = datetime.now(timezone.utc).strftime("%I:%M %p")
    
    response_data = {
        "reply": reply, 
        "timestamp": timestamp,
        "last_message": reply
    }
    if generated_title:
        response_data["title"] = generated_title

    return jsonify(response_data)
