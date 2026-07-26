from datetime import datetime, timezone
import re
from models.conversation_model import ConversationModel
from models.chat_history_model import ChatHistoryModel

class ConversationService:
    """Service layer for conversation management."""

    @staticmethod
    def create_conversation(user_id: str) -> str:
        """Creates a new conversation and returns its ID."""
        return ConversationModel.create(user_id)

    @staticmethod
    def list_conversations(user_id: str) -> dict:
        """
        Lists all conversations for a user, grouped by date.
        Returns: { "today": [...], "yesterday": [...], "previous": [...] }
        """
        conversations = ConversationModel.get_all_for_user(user_id)
        
        now = datetime.utcnow().date()
        
        grouped = {
            "today": [],
            "yesterday": [],
            "previous": []
        }

        for conv in conversations:
            updated_date = conv.get("updated_at").date() if conv.get("updated_at") else now
            
            delta = (now - updated_date).days
            
            if delta == 0:
                grouped["today"].append(conv)
            elif delta == 1:
                grouped["yesterday"].append(conv)
            else:
                grouped["previous"].append(conv)
                
        return grouped

    @staticmethod
    def load_conversation(conversation_id: str, user_id: str) -> dict:
        """Returns conversation metadata if owned by user, else None."""
        return ConversationModel.get_by_id(conversation_id, user_id)

    @staticmethod
    def delete_conversation(conversation_id: str, user_id: str) -> bool:
        """Deletes conversation and its messages. Returns True on success."""
        # 1. Verify ownership
        conv = ConversationModel.get_by_id(conversation_id, user_id)
        if not conv:
            return False
            
        # 2. Delete messages
        ChatHistoryModel.delete_by_conversation(conversation_id)
        
        # 3. Delete conversation document
        return ConversationModel.delete(conversation_id, user_id)

    @staticmethod
    def generate_title(first_message: str) -> str:
        """
        Generates a concise title from the first message.
        """
        if not first_message:
            return "New Chat"

        # 1. Get first sentence
        sentence = re.split(r'[.!?]', first_message)[0].strip()

        # 2. Lowercase for checking prefixes
        lower_sentence = sentence.lower()

        # 3. Remove filler prefixes
        fillers = [
            "i'm ", "i am ", "i need ", "i can't ", "tell me ", 
            "please ", "can you ", "could you "
        ]
        
        for filler in fillers:
            if lower_sentence.startswith(filler):
                sentence = sentence[len(filler):].strip()
                break # Only remove the first matching filler

        # 4. Title case
        # Avoid titlecasing empty string
        if not sentence:
            title = "New Chat"
        else:
            title = sentence.title()

        # 5. Truncate
        if len(title) > 40:
            title = title[:39] + "…"

        return title

    @staticmethod
    def record_message(user_id: str, conversation_id: str, role: str, content: str, model: str = None):
        """
        Saves a message to chat_history and updates the conversation's last_message and updated_at.
        """
        ChatHistoryModel.save(user_id, conversation_id, role, content, model)
        ConversationModel.update_last_message(conversation_id, content)
