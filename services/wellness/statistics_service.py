from datetime import datetime, timedelta
from bson import ObjectId
from services.mongo_service import MongoService

class StatisticsService:
    @staticmethod
    def get_summary(user_id, date_str=None):
        db = MongoService.get_db()
        today = date_str or datetime.now().strftime("%Y-%m-%d")

        # Sum breathing
        b_sessions = list(db.breathing_sessions.find({"user_id": ObjectId(user_id)}))
        b_mins = sum(s.get("duration_seconds", 0) for s in b_sessions) // 60

        # Sum meditation
        m_sessions = list(db.meditation_sessions.find({"user_id": ObjectId(user_id)}))
        m_mins = sum(s.get("elapsed_seconds", 0) for s in m_sessions) // 60

        # Sum focus
        f_sessions = list(db.focus_sessions.find({"user_id": ObjectId(user_id)}))
        f_mins = sum(s.get("total_focus_seconds", 0) for s in f_sessions) // 60

        # Sum music
        music_logs = list(db.music_listening_history.find({"user_id": ObjectId(user_id)}))
        music_mins = sum(m.get("listened_duration_seconds", 0) for m in music_logs) // 60

        # Activities today
        act_count = db.activity_logs.count_documents({"user_id": ObjectId(user_id), "date": today})

        # Latest sleep
        sleep_doc = db.sleep_logs.find_one({"user_id": ObjectId(user_id), "sleep_date": today})
        sleep_hours = sleep_doc.get("hours_slept", 7.5) if sleep_doc else 7.5
        sleep_score = sleep_doc.get("sleep_score", 80) if sleep_doc else 80

        # Streak calculation (simple active days count)
        streak_count = min(30, max(1, len(set(s.get("created_at", datetime.now()).strftime("%Y-%m-%d") for s in b_sessions + m_sessions + f_sessions)) or 1))

        summary_doc = {
            "user_id": ObjectId(user_id),
            "date": today,
            "breathing_minutes": b_mins,
            "meditation_minutes": m_mins,
            "focus_minutes": f_mins,
            "music_minutes": music_mins,
            "activities_completed": act_count,
            "sleep_hours": sleep_hours,
            "sleep_score": sleep_score,
            "streak_count": streak_count,
            "updated_at": datetime.now()
        }

        db.wellness_daily_summaries.update_one(
            {"user_id": ObjectId(user_id), "date": today},
            {"$set": summary_doc},
            upsert=True
        )

        return summary_doc

    @staticmethod
    def get_unified_timeline(user_id, limit=30):
        db = MongoService.get_db()
        uid = ObjectId(user_id)
        timeline = []

        # 1. Breathing Sessions
        for doc in db.breathing_sessions.find({"user_id": uid}).sort("created_at", -1).limit(10):
            timeline.append({
                "timestamp": doc.get("created_at").isoformat() if doc.get("created_at") else "",
                "event_type": "breathing",
                "title": f"Completed {str(doc.get('pattern_type', 'Breathing')).capitalize()} Session",
                "duration_summary": f"{doc.get('duration_seconds', 0) // 60} min",
                "metadata": {"pattern": doc.get("pattern_type")}
            })

        # 2. Meditation Sessions
        for doc in db.meditation_sessions.find({"user_id": uid}).sort("created_at", -1).limit(10):
            timeline.append({
                "timestamp": doc.get("created_at").isoformat() if doc.get("created_at") else "",
                "event_type": "meditation",
                "title": f"Mindful Meditation ({doc.get('duration_minutes', 10)}m)",
                "duration_summary": f"{doc.get('duration_minutes', 10)} min",
                "metadata": {"guided": doc.get("guided", False)}
            })

        # 3. Focus Blocks
        for doc in db.focus_sessions.find({"user_id": uid}).sort("created_at", -1).limit(10):
            timeline.append({
                "timestamp": doc.get("created_at").isoformat() if doc.get("created_at") else "",
                "event_type": "focus",
                "title": f"Focus Block: {str(doc.get('session_type', 'Pomodoro')).capitalize()}",
                "duration_summary": f"{doc.get('total_focus_seconds', 0) // 60} min",
                "metadata": {"intervals": doc.get("completed_work_intervals", 1)}
            })

        # 4. Sleep Logs
        for doc in db.sleep_logs.find({"user_id": uid}).sort("created_at", -1).limit(5):
            timeline.append({
                "timestamp": doc.get("created_at").isoformat() if doc.get("created_at") else "",
                "event_type": "sleep",
                "title": f"Sleep Log: {doc.get('hours_slept', 0)} hrs",
                "duration_summary": f"{doc.get('hours_slept', 0)} hrs",
                "metadata": {"score": doc.get("sleep_score", 0), "quality": doc.get("sleep_quality", 3)}
            })

        # 5. Reflection Journal Entries
        for doc in db.journal_entries.find({"user_id": uid, "is_deleted": {"$ne": True}}).sort("created_at", -1).limit(10):
            timeline.append({
                "timestamp": doc.get("created_at").isoformat() if doc.get("created_at") else "",
                "event_type": "journal",
                "title": f"Reflected: {doc.get('title', 'Untitled Reflection')}",
                "duration_summary": "Journal",
                "metadata": {"mood": doc.get("emotion_snapshot", {}).get("primary_mood") if doc.get("emotion_snapshot") else None}
            })

        # 6. Music Soundscapes History
        for doc in db.music_listening_history.find({"user_id": uid}).sort("started_at", -1).limit(10):
            timeline.append({
                "timestamp": doc.get("started_at").isoformat() if doc.get("started_at") else "",
                "event_type": "music",
                "title": f"Listened to {str(doc.get('category', 'Calm')).replace('_', ' ').capitalize()} Soundscape",
                "duration_summary": f"{doc.get('listened_duration_seconds', 0) // 60} min",
                "metadata": {"track_id": doc.get("track_id")}
            })

        # 7. Quick Habit Logs
        for doc in db.activity_logs.find({"user_id": uid}).sort("created_at", -1).limit(10):
            timeline.append({
                "timestamp": doc.get("created_at").isoformat() if doc.get("created_at") else "",
                "event_type": "activity",
                "title": f"Completed Habit: {str(doc.get('activity_type', 'Habit')).capitalize()}",
                "duration_summary": "Habit",
                "metadata": {"value": doc.get("value", 1)}
            })

        # Sort timeline by timestamp descending
        timeline.sort(key=lambda x: x["timestamp"], reverse=True)
        return timeline[:limit]

