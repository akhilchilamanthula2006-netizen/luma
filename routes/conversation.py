import logging
from flask import Blueprint, jsonify, session
from services.conversation_service import ConversationService

logger = logging.getLogger(__name__)

conversation_bp = Blueprint("conversation", __name__, url_prefix="/conversations")

@conversation_bp.route("/", methods=["POST"])
def create():
    """Create a new conversation."""
    if "user_id" not in session:
        return jsonify({"error": "Not authenticated."}), 401

    user_id = session["user_id"]
    
    try:
        conv_id = ConversationService.create_conversation(user_id)
        return jsonify({"id": conv_id, "title": "New Chat"})
    except Exception as exc:
        logger.error("Failed to create conversation for user %s: %s", user_id, exc)
        return jsonify({"error": "Failed to create conversation."}), 500

@conversation_bp.route("/", methods=["GET"])
def list_conversations():
    """List all conversations for the logged-in user."""
    if "user_id" not in session:
        return jsonify({"error": "Not authenticated."}), 401

    user_id = session["user_id"]
    
    try:
        grouped = ConversationService.list_conversations(user_id)
        return jsonify(grouped)
    except Exception as exc:
        logger.error("Failed to list conversations for user %s: %s", user_id, exc)
        return jsonify({"error": "Failed to load conversations."}), 500

@conversation_bp.route("/<conversation_id>", methods=["DELETE"])
def delete_conversation(conversation_id):
    """Delete a conversation."""
    if "user_id" not in session:
        return jsonify({"error": "Not authenticated."}), 401

    user_id = session["user_id"]
    
    try:
        success = ConversationService.delete_conversation(conversation_id, user_id)
        if success:
            return jsonify({"success": True})
        else:
            return jsonify({"error": "Conversation not found or access denied."}), 404
    except Exception as exc:
        logger.error("Failed to delete conversation %s for user %s: %s", conversation_id, user_id, exc)
        return jsonify({"error": "Failed to delete conversation."}), 500
