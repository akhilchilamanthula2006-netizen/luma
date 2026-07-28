from flask import jsonify
from services.wellness_service import WellnessService
from services.wellness import (
    BreathingService,
    MeditationService,
    FocusService,
    MusicService,
    SleepService,
    ActivityService,
    StatisticsService,
    InsightsService
)

class WellnessController:
    """
    Orchestration layer between Flask routes and Wellness services.
    Extracts HTTP params, validates payloads, and formats standardized JSON responses.
    """

    @staticmethod
    def success_response(data, status_code=200):
        return jsonify({"success": True, "data": data, "error": None}), status_code

    @staticmethod
    def error_response(message, status_code=400):
        return jsonify({"success": False, "data": None, "error": message}), status_code

    # ── Hub & Dashboard Summaries ──
    @classmethod
    def get_dashboard_summary(cls, user_id):
        data = WellnessService.get_dashboard_summary(user_id)
        return cls.success_response(data)

    # ── Breathing ──
    @classmethod
    def get_breathing_configs(cls):
        patterns = BreathingService.get_patterns()
        return cls.success_response(patterns)

    @classmethod
    def log_breathing_session(cls, user_id, payload):
        if not payload:
            return cls.error_response("Missing JSON payload")
        pattern_type = payload.get("pattern_type", "box")
        config = payload.get("config")
        target_cycles = payload.get("target_cycles", 10)
        completed_cycles = payload.get("completed_cycles", 10)
        duration_seconds = payload.get("duration_seconds", 300)
        completed = payload.get("completed", True)

        doc = BreathingService.log_session(user_id, pattern_type, config, target_cycles, completed_cycles, duration_seconds, completed)
        return cls.success_response(doc, 201)

    # ── Meditation ──
    @classmethod
    def log_meditation_session(cls, user_id, payload):
        if not payload:
            return cls.error_response("Missing JSON payload")
        duration_minutes = payload.get("duration_minutes", 10)
        elapsed_seconds = payload.get("elapsed_seconds", 600)
        completed = payload.get("completed", True)
        guided = payload.get("guided", False)
        ambient_sound = payload.get("ambient_sound")

        doc = MeditationService.log_session(user_id, duration_minutes, elapsed_seconds, completed, guided, ambient_sound)
        return cls.success_response(doc, 201)

    # ── Focus ──
    @classmethod
    def get_focus_presets(cls):
        presets = FocusService.get_presets()
        return cls.success_response(presets)

    @classmethod
    def log_focus_session(cls, user_id, payload):
        if not payload:
            return cls.error_response("Missing JSON payload")
        session_type = payload.get("session_type", "pomodoro")
        work_duration_minutes = payload.get("work_duration_minutes", 25)
        break_duration_minutes = payload.get("break_duration_minutes", 5)
        completed_work_intervals = payload.get("completed_work_intervals", 1)
        total_focus_seconds = payload.get("total_focus_seconds", 1500)
        interrupted = payload.get("interrupted", False)

        doc = FocusService.log_session(user_id, session_type, work_duration_minutes, break_duration_minutes, completed_work_intervals, total_focus_seconds, interrupted)
        return cls.success_response(doc, 201)

    # ── Music ──
    @classmethod
    def get_music_catalog(cls, category=None):
        tracks = MusicService.get_tracks(category)
        categories = MusicService.get_categories()
        return cls.success_response({"tracks": tracks, "categories": categories})

    @classmethod
    def log_music_history(cls, user_id, payload):
        if not payload or "track_id" not in payload:
            return cls.error_response("Track ID required")
        track_id = payload.get("track_id")
        category = payload.get("category", "calm")
        started_at = payload.get("started_at")
        ended_at = payload.get("ended_at")
        duration = payload.get("listened_duration_seconds", 0)
        pct = payload.get("completion_percentage", 0.0)
        skipped = payload.get("skipped", False)

        doc = MusicService.log_listening_history(user_id, track_id, category, started_at, ended_at, duration, pct, skipped)
        return cls.success_response(doc, 201)

    # ── Sleep ──
    @classmethod
    def log_sleep(cls, user_id, payload):
        if not payload or "hours_slept" not in payload or "sleep_date" not in payload:
            return cls.error_response("Sleep date and hours_slept required")
        sleep_date = payload.get("sleep_date")
        bedtime = payload.get("bedtime")
        wake_time = payload.get("wake_time")
        hours_slept = float(payload.get("hours_slept", 7.5))
        quality = int(payload.get("sleep_quality", 3))
        latency = int(payload.get("time_to_fall_asleep_minutes", 15))
        awakenings = int(payload.get("awakenings_count", 0))
        source = payload.get("source", "manual")

        doc = SleepService.log_sleep(user_id, sleep_date, bedtime, wake_time, hours_slept, quality, latency, awakenings, source)
        doc["_id"] = str(doc["_id"])
        doc["user_id"] = str(doc["user_id"])
        return cls.success_response(doc, 201)

    @classmethod
    def get_sleep_history(cls, user_id, days=30):
        history = SleepService.get_sleep_history(user_id, days)
        return cls.success_response(history)

    # ── Activities ──
    @classmethod
    def log_activity(cls, user_id, payload):
        if not payload or "activity_type" not in payload:
            return cls.error_response("Activity type required")
        act_type = payload.get("activity_type")
        date_str = payload.get("date")
        val = payload.get("value", 1)
        unit = payload.get("unit", "count")

        doc = ActivityService.log_activity(user_id, act_type, date_str, val, unit)
        return cls.success_response(doc, 201)

    # ── Timeline & Feedback ──
    @classmethod
    def get_timeline(cls, user_id, limit=30):
        timeline = StatisticsService.get_unified_timeline(user_id, limit)
        return cls.success_response(timeline)

    @classmethod
    def log_recommendation_feedback(cls, user_id, payload):
        if not payload or "recommendation_id" not in payload:
            return cls.error_response("Recommendation ID required")
        rec_id = payload.get("recommendation_id")
        rec_type = payload.get("recommendation_type", "general")
        accepted = payload.get("accepted", False)
        dismissed = payload.get("dismissed", False)
        helpful = payload.get("helpful", False)
        not_helpful = payload.get("not_helpful", False)

        doc = InsightsService.log_recommendation_feedback(user_id, rec_id, rec_type, accepted, dismissed, helpful, not_helpful)
        return cls.success_response(doc, 201)
