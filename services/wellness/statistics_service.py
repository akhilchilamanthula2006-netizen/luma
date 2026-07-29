from datetime import datetime, timedelta
from bson import ObjectId
from services.mongo_service import MongoService

class StatisticsService:
    @staticmethod
    def _get_user_docs(col, user_id, query_extra=None):
        """Helper to fetch user documents matching user_id stored as ObjectId or str."""
        extra = query_extra or {}
        docs = []
        try:
            docs.extend(list(col.find({"user_id": ObjectId(user_id), **extra})))
        except Exception:
            pass
        docs.extend(list(col.find({"user_id": str(user_id), **extra})))
        
        # Deduplicate by document _id
        seen = set()
        unique_docs = []
        for d in docs:
            if d.get("_id") not in seen:
                seen.add(d.get("_id"))
                unique_docs.append(d)
        return unique_docs

    @staticmethod
    def _count_user_docs(col, user_id, query_extra=None):
        """Helper to count user documents matching user_id stored as ObjectId or str."""
        extra = query_extra or {}
        total = col.count_documents({"user_id": str(user_id), **extra})
        try:
            total += col.count_documents({"user_id": ObjectId(user_id), **extra})
        except Exception:
            pass
        return total

    @staticmethod
    def get_summary(user_id, date_str=None):
        db = MongoService.get_db()
        today = date_str or datetime.now().strftime("%Y-%m-%d")

        b_sessions = StatisticsService._get_user_docs(db.breathing_sessions, user_id)
        b_mins = sum(s.get("duration_seconds", 0) for s in b_sessions) // 60

        m_sessions = StatisticsService._get_user_docs(db.meditation_sessions, user_id)
        m_mins = sum(s.get("elapsed_seconds", 0) for s in m_sessions) // 60

        f_sessions = StatisticsService._get_user_docs(db.focus_sessions, user_id)
        f_mins = sum(s.get("total_focus_seconds", 0) for s in f_sessions) // 60

        music_logs = StatisticsService._get_user_docs(db.music_listening_history, user_id)
        music_mins = sum(m.get("listened_duration_seconds", 0) for m in music_logs) // 60

        act_count = StatisticsService._count_user_docs(db.activity_logs, user_id, {"date": today})

        sleep_docs = StatisticsService._get_user_docs(db.sleep_logs, user_id, {"sleep_date": today})
        sleep_doc = sleep_docs[0] if sleep_docs else None
        sleep_hours = sleep_doc.get("hours_slept", 7.5) if sleep_doc else 7.5
        sleep_score = sleep_doc.get("sleep_score", 80) if sleep_doc else 80

        active_dates = set()
        for s in b_sessions + m_sessions + f_sessions:
            created = s.get("created_at")
            if isinstance(created, datetime):
                active_dates.add(created.strftime("%Y-%m-%d"))
            elif isinstance(created, str):
                active_dates.add(created[:10])

        streak_count = min(30, max(1, len(active_dates) or 1))

        try:
            uid_obj = ObjectId(user_id)
        except Exception:
            uid_obj = str(user_id)

        summary_doc = {
            "user_id": uid_obj,
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
            {"user_id": uid_obj, "date": today},
            {"$set": summary_doc},
            upsert=True
        )

        return summary_doc

    @staticmethod
    def get_unified_timeline(user_id, limit=30):
        db = MongoService.get_db()
        timeline = []

        # 1. Breathing Sessions
        for doc in StatisticsService._get_user_docs(db.breathing_sessions, user_id):
            created = doc.get("created_at")
            ts = created.isoformat() if isinstance(created, datetime) else (str(created) if created else "")
            timeline.append({
                "timestamp": ts,
                "event_type": "breathing",
                "title": f"Completed {str(doc.get('pattern_type', 'Breathing')).capitalize()} Session",
                "duration_summary": f"{doc.get('duration_seconds', 0) // 60} min",
                "metadata": {"pattern": doc.get("pattern_type")}
            })

        # 2. Meditation Sessions
        for doc in StatisticsService._get_user_docs(db.meditation_sessions, user_id):
            created = doc.get("created_at")
            ts = created.isoformat() if isinstance(created, datetime) else (str(created) if created else "")
            timeline.append({
                "timestamp": ts,
                "event_type": "meditation",
                "title": f"Mindful Meditation ({doc.get('duration_minutes', 10)}m)",
                "duration_summary": f"{doc.get('duration_minutes', 10)} min",
                "metadata": {"guided": doc.get("guided", False)}
            })

        # 3. Focus Blocks
        for doc in StatisticsService._get_user_docs(db.focus_sessions, user_id):
            created = doc.get("created_at")
            ts = created.isoformat() if isinstance(created, datetime) else (str(created) if created else "")
            timeline.append({
                "timestamp": ts,
                "event_type": "focus",
                "title": f"Focus Block: {str(doc.get('session_type', 'Pomodoro')).capitalize()}",
                "duration_summary": f"{doc.get('total_focus_seconds', 0) // 60} min",
                "metadata": {"intervals": doc.get("completed_work_intervals", 1)}
            })

        # 4. Sleep Logs
        for doc in StatisticsService._get_user_docs(db.sleep_logs, user_id):
            created = doc.get("created_at")
            ts = created.isoformat() if isinstance(created, datetime) else (doc.get("sleep_date", "") if doc.get("sleep_date") else "")
            timeline.append({
                "timestamp": ts,
                "event_type": "sleep",
                "title": f"Sleep Log: {doc.get('hours_slept', 0)} hrs",
                "duration_summary": f"{doc.get('hours_slept', 0)} hrs",
                "metadata": {"score": doc.get("sleep_score", 0), "quality": doc.get("sleep_quality", 3)}
            })

        # 5. Reflection Journal Entries
        for doc in StatisticsService._get_user_docs(db.journal_entries, user_id, {"is_deleted": {"$ne": True}}):
            created = doc.get("created_at")
            ts = created.isoformat() if isinstance(created, datetime) else (str(created) if created else "")
            timeline.append({
                "timestamp": ts,
                "event_type": "journal",
                "title": f"Reflected: {doc.get('title', 'Untitled Reflection')}",
                "duration_summary": "Journal",
                "metadata": {"mood": doc.get("emotion_snapshot", {}).get("primary_mood") if doc.get("emotion_snapshot") else None}
            })

        # 6. Music Soundscapes History
        for doc in StatisticsService._get_user_docs(db.music_listening_history, user_id):
            started = doc.get("started_at")
            ts = started.isoformat() if isinstance(started, datetime) else (str(started) if started else "")
            timeline.append({
                "timestamp": ts,
                "event_type": "music",
                "title": f"Listened to {str(doc.get('category', 'Calm')).replace('_', ' ').capitalize()} Soundscape",
                "duration_summary": f"{doc.get('listened_duration_seconds', 0) // 60} min",
                "metadata": {"track_id": doc.get("track_id")}
            })

        # 7. Quick Habit Logs
        for doc in StatisticsService._get_user_docs(db.activity_logs, user_id):
            created = doc.get("created_at")
            ts = created.isoformat() if isinstance(created, datetime) else (str(created) if created else "")
            timeline.append({
                "timestamp": ts,
                "event_type": "activity",
                "title": f"Completed Habit: {str(doc.get('activity_type', 'Habit')).capitalize()}",
                "duration_summary": "Habit",
                "metadata": {"value": doc.get("value", 1)}
            })

        # Sort timeline by timestamp descending
        timeline.sort(key=lambda x: x["timestamp"], reverse=True)
        return timeline[:limit]

    @staticmethod
    def has_wellness_history(user_id):
        """
        Determines whether a user has logged any lifetime wellness activities in MongoDB.
        Supports both ObjectId and str user_id representations across all collections.
        """
        db = MongoService.get_db()
        if db is None or not user_id:
            return False

        total_records = (
            StatisticsService._count_user_docs(db.breathing_sessions, user_id) +
            StatisticsService._count_user_docs(db.meditation_sessions, user_id) +
            StatisticsService._count_user_docs(db.focus_sessions, user_id) +
            StatisticsService._count_user_docs(db.sleep_logs, user_id) +
            StatisticsService._count_user_docs(db.music_listening_history, user_id) +
            StatisticsService._count_user_docs(db.journal_entries, user_id, {"is_deleted": {"$ne": True}}) +
            StatisticsService._count_user_docs(db.activity_logs, user_id) +
            StatisticsService._count_user_docs(db.mood_logs, user_id)
        )
        return total_records > 0

    @staticmethod
    def get_7day_analytics(user_id):
        """
        Computes 7-day time series data, activity distributions, and mood counts
        strictly from MongoDB data.
        """
        db = MongoService.get_db()

        now = datetime.now()
        dates = [(now - timedelta(days=i)) for i in range(6, -1, -1)]
        day_labels = [d.strftime("%a") for d in dates]
        date_strs = [d.strftime("%Y-%m-%d") for d in dates]

        has_data = StatisticsService.has_wellness_history(user_id)
        if not has_data or db is None:
            return {
                "has_data": False,
                "is_demo": False,
                "day_labels": day_labels,
                "wellness_scores": [0, 0, 0, 0, 0, 0, 0],
                "sleep_hours": [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                "meditation_mins": [0, 0, 0, 0, 0, 0, 0],
                "breathing_mins": [0, 0, 0, 0, 0, 0, 0],
                "focus_mins": [0, 0, 0, 0, 0, 0, 0],
                "mood_counts": {},
                "activity_distribution": {},
                "total_weekly_activities": 0
            }

        # Fetch all records for the user across collections (handling both ObjectId and str user_id)
        b_all = StatisticsService._get_user_docs(db.breathing_sessions, user_id)
        m_all = StatisticsService._get_user_docs(db.meditation_sessions, user_id)
        f_all = StatisticsService._get_user_docs(db.focus_sessions, user_id)
        s_all = StatisticsService._get_user_docs(db.sleep_logs, user_id)
        mus_all = StatisticsService._get_user_docs(db.music_listening_history, user_id)
        j_all = StatisticsService._get_user_docs(db.journal_entries, user_id, {"is_deleted": {"$ne": True}})
        act_all = StatisticsService._get_user_docs(db.activity_logs, user_id)
        mood_all = StatisticsService._get_user_docs(db.mood_logs, user_id)

        def extract_date_str(doc):
            for field in ["created_at", "timestamp", "started_at", "sleep_date", "date"]:
                v = doc.get(field)
                if v:
                    if isinstance(v, datetime):
                        return v.strftime("%Y-%m-%d")
                    elif isinstance(v, str):
                        return v[:10]
            return None

        wellness_scores = []
        sleep_hours = []
        meditation_mins = []
        breathing_mins = []
        focus_mins = []

        for d_str in date_strs:
            # Sleep hours
            s_doc = next((s for s in s_all if extract_date_str(s) == d_str), None)
            s_hrs = s_doc.get("hours_slept", 0.0) if s_doc else 0.0
            sleep_hours.append(round(float(s_hrs), 1))

            # Breathing mins
            b_m = sum(b.get("duration_seconds", 0) for b in b_all if extract_date_str(b) == d_str) // 60
            breathing_mins.append(int(b_m))

            # Meditation mins
            m_m = sum(m.get("duration_minutes", 0) for m in m_all if extract_date_str(m) == d_str)
            meditation_mins.append(int(m_m))

            # Focus mins
            f_m = sum(f.get("total_focus_seconds", 0) for f in f_all if extract_date_str(f) == d_str) // 60
            focus_mins.append(int(f_m))

            # Score calculation
            if (s_hrs > 0 or b_m > 0 or m_m > 0 or f_m > 0):
                base_score = 60
                if s_hrs >= 7.0: base_score += 20
                elif s_hrs >= 6.0: base_score += 10
                if (b_m + m_m + f_m) > 0: base_score += 20
                wellness_scores.append(min(100, max(40, base_score)))
            else:
                wellness_scores.append(0)

        # Mood counts over past 7 days
        mood_counts = {}
        for m in mood_all:
            d = extract_date_str(m)
            if d in date_strs:
                lbl = m.get("mood_label") or m.get("mood")
                if lbl:
                    mood_counts[lbl] = mood_counts.get(lbl, 0) + 1

        # Also check journal entries for primary mood
        for j in j_all:
            d = extract_date_str(j)
            if d in date_strs:
                es = j.get("emotion_snapshot") or {}
                pm = es.get("primary_mood")
                if pm:
                    mood_counts[pm] = mood_counts.get(pm, 0) + 1

        # Activity Distribution over past 7 days
        b_count = sum(1 for b in b_all if extract_date_str(b) in date_strs)
        m_count = sum(1 for m in m_all if extract_date_str(m) in date_strs)
        f_count = sum(1 for f in f_all if extract_date_str(f) in date_strs)
        s_count = sum(1 for s in s_all if extract_date_str(s) in date_strs)
        mus_count = sum(1 for mus in mus_all if extract_date_str(mus) in date_strs)
        j_count = sum(1 for j in j_all if extract_date_str(j) in date_strs)
        act_logs_count = sum(1 for act in act_all if extract_date_str(act) in date_strs)

        total_weekly_activities = b_count + m_count + f_count + s_count + mus_count + j_count + act_logs_count

        activity_distribution = {}
        if b_count > 0: activity_distribution["Breathing"] = b_count
        if m_count > 0: activity_distribution["Meditation"] = m_count
        if f_count > 0: activity_distribution["Focus"] = f_count
        if s_count > 0: activity_distribution["Sleep"] = s_count
        if mus_count > 0: activity_distribution["Music"] = mus_count
        if j_count > 0: activity_distribution["Journal"] = j_count

        return {
            "has_data": True,
            "is_demo": False,
            "day_labels": day_labels,
            "wellness_scores": wellness_scores,
            "sleep_hours": sleep_hours,
            "meditation_mins": meditation_mins,
            "breathing_mins": breathing_mins,
            "focus_mins": focus_mins,
            "mood_counts": mood_counts,
            "activity_distribution": activity_distribution,
            "total_weekly_activities": total_weekly_activities
        }
