import unittest
import os
import tempfile
from fastapi.testclient import TestClient

from main import app
from database import MigrationManager
import services.user_service as user_service


class TestSocialLikes(unittest.TestCase):
    def setUp(self):
        self.temp_fd, self.db_path = tempfile.mkstemp(suffix='.db')
        user_service.DB_PATH = self.db_path
        MigrationManager(self.db_path).run_migrations()
        self.client = TestClient(app)

        # user
        self.u1 = user_service.create_user("like@example.com", "StrongPass1!")
        # login
        resp = self.client.post("/api/auth/login", json={"email": "like@example.com", "password": "StrongPass1!"})
        self.tok = resp.json()["token"]

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

    def test_like_unlike(self):
        # like
        r1 = self.client.post("/api/social/like", json={"ref_id": "r-1"}, headers={"Authorization": f"Bearer {self.tok}"})
        self.assertEqual(r1.status_code, 201)
        # duplicate
        rdup = self.client.post("/api/social/like", json={"ref_id": "r-1"}, headers={"Authorization": f"Bearer {self.tok}"})
        self.assertEqual(rdup.status_code, 409)
        # unlike
        r2 = self.client.request("DELETE", "/api/social/like", json={"ref_id": "r-1"}, headers={"Authorization": f"Bearer {self.tok}"})
        self.assertEqual(r2.status_code, 204)
        # unlike missing
        r404 = self.client.request("DELETE", "/api/social/like", json={"ref_id": "r-1"}, headers={"Authorization": f"Bearer {self.tok}"})
        self.assertEqual(r404.status_code, 404)


if __name__ == '__main__':
    unittest.main()


