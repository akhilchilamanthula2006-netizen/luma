import unittest
import sys
import os
from datetime import datetime, timedelta
from bson import ObjectId

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from app import create_app
from services.mongo_service import MongoService
from services.wellness_service import WellnessService
from services.wellness.statistics_service import StatisticsService
from services.wellness.insights_service import InsightsService

class TestMilestone9Analytics(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.app = create_app('development')
        cls.app_context = cls.app.app_context()
        cls.app_context.push()

        cls.client = cls.app.test_client()
        cls.test_user_id = str(ObjectId())
        cls.username = "AnalyticsTestUser"

        db = MongoService.get_db()
        uid = ObjectId(cls.test_user_id)

        # Seed test data across past 7 days
        for i in range(7):
            d_date = datetime.now() - timedelta(days=i)
            d_str = d_date.strftime("%Y-%m-%d")

            # Sleep log
            db.sleep_logs.insert_one({
                "user_id": uid,
                "sleep_date": d_str,
                "hours_slept": 7.5 + (i * 0.1),
                "sleep_quality": 4,
                "sleep_score": 80 + i,
                "created_at": d_date
            })

            # Breathing session
            db.breathing_sessions.insert_one({
                "user_id": uid,
                "pattern_type": "box",
                "duration_seconds": 240,
                "completed_cycles": 10,
                "created_at": d_date
            })

            # Meditation session
            db.meditation_sessions.insert_one({
                "user_id": uid,
                "duration_minutes": 10,
                "guided": True,
                "created_at": d_date
            })

            # Focus session
            db.focus_sessions.insert_one({
                "user_id": uid,
                "session_type": "pomodoro",
                "total_focus_seconds": 1500,
                "completed_work_intervals": 1,
                "created_at": d_date
            })

            # Mood log
            db.mood_logs.insert_one({
                "user_id": uid,
                "mood": "Calm" if i % 2 == 0 else "Happy",
                "mood_label": "Calm" if i % 2 == 0 else "Happy",
                "score": 85,
                "timestamp": d_date
            })

            # Journal entry
            db.journal_entries.insert_one({
                "user_id": uid,
                "title": f"Reflection Day {i}",
                "content": "Grateful for steady progress and peace.",
                "emotion_snapshot": {"primary_mood": "Calm"},
                "created_at": d_date,
                "is_deleted": False
            })

            # Music history
            db.music_listening_history.insert_one({
                "user_id": uid,
                "track_id": "trk_ocean_01",
                "category": "stress_relief",
                "listened_duration_seconds": 300,
                "started_at": d_date
            })

    @classmethod
    def tearDownClass(cls):
        db = MongoService.get_db()
        uid = ObjectId(cls.test_user_id)
        db.sleep_logs.delete_many({"user_id": uid})
        db.breathing_sessions.delete_many({"user_id": uid})
        db.meditation_sessions.delete_many({"user_id": uid})
        db.focus_sessions.delete_many({"user_id": uid})
        db.mood_logs.delete_many({"user_id": uid})
        db.journal_entries.delete_many({"user_id": uid})
        db.music_listening_history.delete_many({"user_id": uid})
        db.wellness_daily_summaries.delete_many({"user_id": uid})
        cls.app_context.pop()

    def test_01_7day_analytics_service(self):
        data = StatisticsService.get_7day_analytics(self.test_user_id)
        self.assertEqual(len(data["day_labels"]), 7)
        self.assertEqual(len(data["wellness_scores"]), 7)
        self.assertEqual(len(data["sleep_hours"]), 7)
        self.assertGreaterEqual(data["total_weekly_activities"], 7)
        self.assertIn("Breathing", data["activity_distribution"])

    def test_02_weekly_ai_summary_service(self):
        ai_summary = InsightsService.generate_weekly_ai_summary(self.test_user_id)
        self.assertIn("overall_progress", ai_summary)
        self.assertIsInstance(ai_summary["positive_habits"], list)
        self.assertIsInstance(ai_summary["areas_for_attention"], list)
        self.assertIsInstance(ai_summary["recommendations"], list)
        self.assertGreater(len(ai_summary["positive_habits"]), 0)

    def test_03_analytics_routes(self):
        with self.client.session_transaction() as sess:
            sess['user_id'] = self.test_user_id
            sess['username'] = self.username

        res_page = self.client.get('/analytics/')
        self.assertEqual(res_page.status_code, 200)
        self.assertIn(b'Analytics', res_page.data)


        res_api = self.client.get('/analytics/api/data')
        self.assertEqual(res_api.status_code, 200)
        json_data = res_api.json
        self.assertTrue(json_data["success"])
        self.assertIn("summary", json_data["data"])
        self.assertIn("analytics", json_data["data"])
        self.assertIn("ai_summary", json_data["data"])
        self.assertIn("timeline", json_data["data"])

if __name__ == '__main__':
    unittest.main()
