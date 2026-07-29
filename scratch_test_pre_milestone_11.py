import sys
import os
from bson import ObjectId

# Add project root to sys.path
sys.path.insert(0, os.path.dirname(__file__))

from services.mongo_service import MongoService
from services.wellness.statistics_service import StatisticsService
from services.wellness.insights_service import InsightsService
from models.user_model import UserModel

def test_analytics_empty_state_and_avatar():
    print("--- 1. Testing Empty Analytics State for Dummy User ---")
    dummy_user_id = str(ObjectId())
    
    has_history = StatisticsService.has_wellness_history(dummy_user_id)
    print(f"has_wellness_history for new user: {has_history}")
    assert has_history == False, "New user should have has_wellness_history == False"

    analytics = StatisticsService.get_7day_analytics(dummy_user_id)
    print(f"analytics has_data: {analytics.get('has_data')}")
    print(f"analytics total_weekly_activities: {analytics.get('total_weekly_activities')}")
    print(f"analytics mood_counts: {analytics.get('mood_counts')}")
    print(f"analytics activity_distribution: {analytics.get('activity_distribution')}")
    assert analytics.get("has_data") == False, "Analytics has_data should be False for new user"
    assert analytics.get("is_demo") == False, "is_demo should be False"
    assert analytics.get("total_weekly_activities") == 0
    assert analytics.get("mood_counts") == {}
    assert analytics.get("activity_distribution") == {}

    ai_summary = InsightsService.generate_weekly_ai_summary(dummy_user_id)
    print(f"ai_summary has_data: {ai_summary.get('has_data')}")
    assert ai_summary.get("has_data") == False

    print("\n--- 2. Testing Avatar Storage & Retrieval ---")
    db = MongoService.get_db()
    test_user_doc = {
        "username": "test_avatar_user",
        "email": "avatar_test@luma.com",
        "avatar": "",
        "bio": "Testing avatar selection"
    }
    res = db.users.insert_one(test_user_doc)
    user_id_str = str(res.inserted_id)

    print("Initial user loaded:", UserModel.find_by_id(user_id_str).avatar)
    
    # Update profile avatar to relative path
    new_avatar_path = "/static/images/avatars/female_03.svg"
    UserModel.update_profile(user_id_str, name="test_avatar_user", bio="Updated bio", avatar=new_avatar_path)

    updated_user = UserModel.find_by_id(user_id_str)
    print("Updated user avatar in DB:", updated_user.avatar)
    assert updated_user.avatar == new_avatar_path, f"Expected {new_avatar_path}, got {updated_user.avatar}"

    # Cleanup test user
    db.users.delete_one({"_id": res.inserted_id})
    print("\n--- ALL PRE-MILESTONE 11 VERIFICATION TESTS PASSED SUCCESSFULLY! ---")

if __name__ == "__main__":
    test_analytics_empty_state_and_avatar()
