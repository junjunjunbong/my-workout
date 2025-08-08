import unittest
import os
import tempfile
import sqlite3
from fastapi.testclient import TestClient

from main import app
from database import MigrationManager
import services.user_service as user_service


class TestSocialFollow(unittest.TestCase):
    def setUp(self):
        self.temp_fd, self.db_path = tempfile.mkstemp(suffix='.db')
        user_service.DB_PATH = self.db_path
        MigrationManager(self.db_path).run_migrations()
        self.client = TestClient(app)

        # create two users
        self.u1 = user_service.create_user("u1@example.com", "StrongPass1!")
        self.u2 = user_service.create_user("u2@example.com", "StrongPass1!")

        # login as u1
        resp = self.client.post("/api/auth/login", json={"email": "u1@example.com", "password": "StrongPass1!"})
        self.assertEqual(resp.status_code, 200)
        self.tok1 = resp.json()["token"]

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

    def test_follow_and_unfollow(self):
        # follow
        r1 = self.client.post("/api/social/follow", json={"user_id": self.u2["id"]}, headers={"Authorization": f"Bearer {self.tok1}"})
        self.assertEqual(r1.status_code, 201)

        # duplicate follow -> 409
        rdup = self.client.post("/api/social/follow", json={"user_id": self.u2["id"]}, headers={"Authorization": f"Bearer {self.tok1}"})
        self.assertEqual(rdup.status_code, 409)

        # cannot follow self
        rself = self.client.post("/api/social/follow", json={"user_id": self.u1["id"]}, headers={"Authorization": f"Bearer {self.tok1}"})
        self.assertEqual(rself.status_code, 400)

        # unfollow
        r2 = self.client.request("DELETE", "/api/social/follow", json={"user_id": self.u2["id"]}, headers={"Authorization": f"Bearer {self.tok1}"})
        self.assertEqual(r2.status_code, 204)

        # unfollow non-existent -> 404
        r404 = self.client.request("DELETE", "/api/social/follow", json={"user_id": self.u2["id"]}, headers={"Authorization": f"Bearer {self.tok1}"})
        self.assertEqual(r404.status_code, 404)


if __name__ == '__main__':
    unittest.main()


