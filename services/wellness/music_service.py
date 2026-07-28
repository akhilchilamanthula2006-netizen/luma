from bson import ObjectId
from services.mongo_service import MongoService
from models.wellness.music_model import MusicTrackModel, MusicListeningHistoryModel
from utils.wellness_constants import MUSIC_CATEGORIES

# All tracks use the Web Audio API (provider="webapi") — no files required,
# no copyright issues, plays instantly in every browser.
DEFAULT_TRACKS = [
    {
        "track_id": "trk_ocean_01",
        "title": "Deep Ocean Waves",
        "duration_seconds": 600,
        "category": "stress_relief",
        "artist": "Luma Soundscapes",
        "description": "Pink noise shaped into slow ocean wave cycles — calms the nervous system within minutes.",
        "mood_tags": ["water", "calm", "stress-relief"],
        "thumbnail_path": "/static/images/music/ocean.jpg",
        "audio_source": {
            "provider": "webapi",
            "webapi_type": "ocean",
            "resource_url": None,
            "external_id": None
        }
    },
    {
        "track_id": "trk_rain_02",
        "title": "Gentle Rainfall",
        "duration_seconds": 480,
        "category": "calm",
        "artist": "Luma Nature",
        "description": "Continuous brown noise filtered to sound like soft rain on forest leaves.",
        "mood_tags": ["rain", "nature", "sleep"],
        "thumbnail_path": "/static/images/music/rain.jpg",
        "audio_source": {
            "provider": "webapi",
            "webapi_type": "rain",
            "resource_url": None,
            "external_id": None
        }
    },
    {
        "track_id": "trk_focus_03",
        "title": "Alpha Binaural Beats",
        "duration_seconds": 600,
        "category": "focus",
        "artist": "Luma Mind Engine",
        "description": "10Hz binaural beat (200Hz / 210Hz) layered with light white noise for deep focus and flow state.",
        "mood_tags": ["focus", "binaural", "work", "alpha"],
        "thumbnail_path": "/static/images/music/focus.jpg",
        "audio_source": {
            "provider": "webapi",
            "webapi_type": "binaural",
            "resource_url": None,
            "external_id": None
        }
    },
    {
        "track_id": "trk_forest_04",
        "title": "Forest Ambience",
        "duration_seconds": 540,
        "category": "nature",
        "artist": "Luma Nature",
        "description": "Layered filtered noise evoking wind through trees and gentle birdsong patterns.",
        "mood_tags": ["forest", "wind", "nature", "grounding"],
        "thumbnail_path": "/static/images/music/forest.jpg",
        "audio_source": {
            "provider": "webapi",
            "webapi_type": "forest",
            "resource_url": None,
            "external_id": None
        }
    },
    {
        "track_id": "trk_morning_05",
        "title": "Sunrise Energy",
        "duration_seconds": 420,
        "category": "morning_energy",
        "artist": "Luma Soundscapes",
        "description": "Warm ascending tones with soft pink noise — energises and clears morning mental fog.",
        "mood_tags": ["morning", "energy", "uplifting", "clarity"],
        "thumbnail_path": "/static/images/music/morning.jpg",
        "audio_source": {
            "provider": "webapi",
            "webapi_type": "morning",
            "resource_url": None,
            "external_id": None
        }
    }
]

class MusicService:
    @staticmethod
    def get_categories():
        return MUSIC_CATEGORIES

    @staticmethod
    def get_tracks(category=None):
        db = MongoService.get_db()

        # Re-seed if collection is empty OR if tracks are missing webapi_type
        needs_seed = db.music_tracks.count_documents({}) == 0
        if not needs_seed:
            # Check if existing tracks have the new webapi provider
            sample = db.music_tracks.find_one({"audio_source.provider": {"$ne": "webapi"}})
            if sample:
                db.music_tracks.drop()
                needs_seed = True

        if needs_seed:
            db.music_tracks.insert_many(DEFAULT_TRACKS)

        query = {}
        if category and category in MUSIC_CATEGORIES:
            query["category"] = category

        cursor = db.music_tracks.find(query)
        tracks = list(cursor)
        for t in tracks:
            t["_id"] = str(t["_id"]) if "_id" in t else None
        return tracks

    @staticmethod
    def log_listening_history(user_id, track_id, category, started_at, ended_at,
                               listened_duration_seconds, completion_percentage, skipped=False):
        db = MongoService.get_db()
        history = MusicListeningHistoryModel(
            user_id=user_id,
            track_id=track_id,
            category=category,
            started_at=started_at,
            ended_at=ended_at,
            listened_duration_seconds=listened_duration_seconds,
            completion_percentage=completion_percentage,
            skipped=skipped
        )
        res = db.music_listening_history.insert_one(history.to_dict())
        history.id = str(res.inserted_id)
        return history.to_dict()
