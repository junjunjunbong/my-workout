"""
Integration tests for GET /api/users/me protected endpoint.
"""
import unittest
import os
import tempfile
from fastapi.testclient import TestClient

from main import app
from database import MigrationManager
import services.user_service as user_service
from services.auth_service import create_access_token

class TestUserMe(unittest.TestCase):
    def setUp(self):
        self.temp_fd, self.db_path = tempfile.mkstemp(suffix='.db')
        user_service.DB_PATH = self.db_path
        MigrationManager(self.db_path).run_migrations()
        self.client = TestClient(app)
        self.email = "me@example.com"
        self.password = "StrongPass1!"
        user = user_service.create_user(self.email, self.password)
        self.user_id = user["id"]
        self.token = create_access_token(self.user_id)

    def tearDown(self):
        try:
            os.close(self.temp_fd)
        except OSError:
            pass
        try:
            if os.path.exists(self.db_path):
                os.remove(self.db_path)
        except PermissionError:
            pass

    def test_get_me(self):
        resp = self.client.get("/api/users/me", headers={"Authorization": f"Bearer {self.token}"})
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data["id"], self.user_id)
        self.assertEqual(data["email"], self.email)
        self.assertNotIn("password_hash", data)

if __name__ == '__main__':
    unittest.main()