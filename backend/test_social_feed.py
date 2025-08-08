import unittest
import os
import tempfile
from fastapi.testclient import TestClient

from main import app
from database import MigrationManager
import services.user_service as user_service
from services.social_service import record_activity


class TestSocialFeed(unittest.TestCase):
    def setUp(self):
        self.temp_fd, self.db_path = tempfile.mkstemp(suffix='.db')
        user_service.DB_PATH = self.db_path
        MigrationManager(self.db_path).run_migrations()
        self.client = TestClient(app)

        # users
        self.u1 = user_service.create_user("a@example.com", "StrongPass1!")
        self.u2 = user_service.create_user("b@example.com", "StrongPass1!")
        self.u3 = user_service.create_user("c@example.com", "StrongPass1!")

        # login u1
        resp = self.client.post("/api/auth/login", json={"email": "a@example.com", "password": "StrongPass1!"})
        self.tok1 = resp.json()["token"]

        # u1 follows u2 and u3
        self.client.post("/api/social/follow", json={"user_id": self.u2["id"]}, headers={"Authorization": f"Bearer {self.tok1}"})
        self.client.post("/api/social/follow", json={"user_id": self.u3["id"]}, headers={"Authorization": f"Bearer {self.tok1}"})

        # create activities for u2 and u3
        record_activity(self.u2["id"], "workout", "w-1")
        record_activity(self.u3["id"], "routine", "r-1")
        record_activity(self.u2["id"], "workout", "w-2")

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

    def test_feed_pagination(self):
        r1 = self.client.get("/api/social/feed?limit=2", headers={"Authorization": f"Bearer {self.tok1}"})
        self.assertEqual(r1.status_code, 200)
        data1 = r1.json()
        self.assertEqual(len(data1["items"]), 2)
        self.assertTrue(data1.get("nextCursor") is not None)

        # next page
        r2 = self.client.get(f"/api/social/feed?limit=2&cursor={data1['nextCursor']}", headers={"Authorization": f"Bearer {self.tok1}"})
        self.assertEqual(r2.status_code, 200)
        data2 = r2.json()
        # remaining 1 item
        self.assertEqual(len(data2["items"]), 1)


if __name__ == '__main__':
    unittest.main()


