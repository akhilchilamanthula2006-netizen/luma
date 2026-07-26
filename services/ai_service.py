import logging
from config import Config

logger = logging.getLogger(__name__)

class AIService:
    """
    Service for future Groq (Llama) integration.
    Currently prepared with skeleton helper functions.
    """
    @staticmethod
    def generate_chat_response(prompt: str, chat_history: list = None) -> str:
        """
        Generates an AI response based on a prompt and historical conversation.
        To be implemented in the AI Integration milestone.
        """
        logger.info(f"AI chat response requested for prompt: '{prompt[:30]}...'")
        # Mock/placeholder response
        return "Hi, I am Luma, your mental wellness companion. This is a placeholder response."

    @staticmethod
    def analyze_mood_journal(entry_text: str) -> dict:
        """
        Analyzes a journal entry to extract sentiment, primary emotions, and insights.
        To be implemented in the AI Integration milestone.
        """
        logger.info(f"AI analysis requested for journal entry of length {len(entry_text)}")
        return {
            "sentiment": "Neutral",
            "score": 0.5,
            "detected_emotions": ["calm"],
            "suggested_action": "Continue reflecting on your feelings."
        }
