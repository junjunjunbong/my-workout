import unittest
import os
import tempfile
from fastapi.testclient import TestClient

from main import app
from database import MigrationManager
import services.user_service as user_service
from services.auth_service import create_access_token

class TestUserProfile(unittest.TestCase):
    def setUp(self):
        self.temp_fd, self.db_path = tempfile.mkstemp(suffix='.db')
        user_service.DB_PATH = self.db_path
        MigrationManager(self.db_path).run_migrations()
        self.client = TestClient(app)
        # Create user
        self.email = "profile@example.com"
        self.password = "StrongPass1!"
        user = user_service.create_user(self.email, self.password)
        self.uid = user["id"]
        self.token = create_access_token(self.uid)

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

    def test_get_and_update_profile(self):
        # initial GET
        r1 = self.client.get("/api/users/me", headers={"Authorization": f"Bearer {self.token}"})
        self.assertEqual(r1.status_code, 200)
        data1 = r1.json()
        self.assertEqual(data1["id"], self.uid)
        self.assertEqual(data1["email"], self.email)
        self.assertIsNone(data1.get("avatar_url"))

        # update
        upd = {"avatar_url": "https://example.com/a.png", "bio": "hi", "goal": "bench 100"}
        r2 = self.client.patch("/api/users/me", json=upd, headers={"Authorization": f"Bearer {self.token}"})
        self.assertEqual(r2.status_code, 200)
        data2 = r2.json()
        self.assertEqual(data2["avatar_url"], upd["avatar_url"])
        self.assertEqual(data2["bio"], upd["bio"])
        self.assertEqual(data2["goal"], upd["goal"])