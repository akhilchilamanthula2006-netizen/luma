class AudioPlayerService:
    """
    Provider-agnostic server interface for track metadata resolution
    and audio streaming configuration (HTML5 / Spotify / YouTube SDK readiness).
    """

    @staticmethod
    def resolve_audio_payload(track_dict):
        if not track_dict:
            return None

        source = track_dict.get("audio_source", {})
        provider = source.get("provider", "local")

        return {
            "track_id": track_dict.get("track_id"),
            "title": track_dict.get("title"),
            "artist": track_dict.get("artist"),
            "category": track_dict.get("category"),
            "duration_seconds": track_dict.get("duration_seconds"),
            "provider": provider,
            "stream_url": source.get("resource_url") if provider == "local" else None,
            "external_id": source.get("external_id") if provider != "local" else None
        }
