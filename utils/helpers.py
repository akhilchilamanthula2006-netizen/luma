from datetime import datetime

def format_date(dt: datetime, fmt: str = "%b %d, %Y") -> str:
    """Formats a datetime object to a friendly string."""
    if not dt:
        return ""
    return dt.strftime(fmt)

def get_mood_emoji(score: int) -> str:
    """Returns corresponding emoji representing mood score (1-5)."""
    emojis = {
        1: "😢", # Very low
        2: "🙁", # Low
        3: "😐", # Neutral
        4: "🙂", # Good
        5: "😊"  # Very Good
    }
    return emojis.get(score, "😐")
