import unittest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__) + '/..'))

from app import create_app
from models.user_model import UserModel
from werkzeug.security import generate_password_hash

class TestProfileSettings(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = create_app('development')
        cls.client = cls.app.test_client()
        cls.app_context = cls.app.app_context()
        cls.app_context.push()
        
        # Ensure a test user exists
        user = UserModel.find_by_email("test_profile@example.com")
        if not user:
            user = UserModel.create(
                username="profileuser",
                email="test_profile@example.com",
                password_hash=generate_password_hash("password123")
            )
        cls.user_id = str(user.id)

    def login(self):
        with self.client.session_transaction() as sess:
            sess['user_id'] = self.user_id
            sess['username'] = "profileuser"

    def test_profile_page(self):
        self.login()
        res = self.client.get('/profile/')
        self.assertEqual(res.status_code, 200)
        self.assertIn(b'My Profile', res.data)
        self.assertIn(b'profileuser', res.data)

    def test_update_profile(self):
        self.login()
        res = self.client.post('/profile/update', data={
            'name': 'Updated Profile User',
            'bio': 'A wellness lover',
            'avatar': 'https://example.com/me.png'
        }, follow_redirects=True)
        self.assertEqual(res.status_code, 200)
        self.assertIn(b'Profile updated successfully.', res.data)
        
        updated_user = UserModel.find_by_id(self.user_id)
        self.assertEqual(updated_user.username, 'Updated Profile User')
        self.assertEqual(updated_user.bio, 'A wellness lover')

    def test_settings_page(self):
        self.login()
        res = self.client.get('/settings/')
        self.assertEqual(res.status_code, 200)
        self.assertIn(b'Preferences & Appearance', res.data)

    def test_update_settings(self):
        self.login()
        res = self.client.post('/settings/update', data={
            'theme': 'dark',
            'notifications': 'on'
        }, follow_redirects=True)
        self.assertEqual(res.status_code, 200)
        self.assertIn(b'Settings updated successfully.', res.data)
        
        updated_user = UserModel.find_by_id(self.user_id)
        self.assertEqual(updated_user.theme, 'dark')
        self.assertTrue(updated_user.notifications_enabled)
        self.assertFalse(updated_user.ai_personalization_enabled)

    def test_change_password(self):
        self.login()
        res = self.client.post('/settings/password', data={
            'current_password': 'password123',
            'new_password': 'newpassword123',
            'confirm_password': 'newpassword123'
        }, follow_redirects=True)
        self.assertEqual(res.status_code, 200)
        self.assertIn(b'Password updated successfully.', res.data)

if __name__ == '__main__':
    unittest.main()
