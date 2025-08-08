import unittest
import os
import tempfile
from fastapi.testclient import TestClient

from main import app
from database import MigrationManager
import services.user_service as user_service


class TestSocialComments(unittest.TestCase):
    def setUp(self):
        self.temp_fd, self.db_path = tempfile.mkstemp(suffix='.db')
        user_service.DB_PATH = self.db_path
        MigrationManager(self.db_path).run_migrations()
        self.client = TestClient(app)

        # users
        self.u1 = user_service.create_user("c1@example.com", "StrongPass1!")
        self.u2 = user_service.create_user("c2@example.com", "StrongPass1!")
        # login as u1
        resp = self.client.post("/api/auth/login", json={"email": "c1@example.com", "password": "StrongPass1!"})
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

    def test_comment_crud(self):
        # create comment
        r1 = self.client.post(
            "/api/social/comment",
            json={"ref_id": "r-123", "content": "hello"},
            headers={"Authorization": f"Bearer {self.tok1}"},
        )
        self.assertEqual(r1.status_code, 201)
        cid = r1.json()["id"]

        # list comments
        r2 = self.client.get(
            "/api/social/comments",
            params={"ref_id": "r-123"},
            headers={"Authorization": f"Bearer {self.tok1}"},
        )
        self.assertEqual(r2.status_code, 200)
        self.assertEqual(len(r2.json()), 1)

        # delete own comment
        r3 = self.client.delete(
            f"/api/social/comment/{cid}",
            headers={"Authorization": f"Bearer {self.tok1}"},
        )
        self.assertEqual(r3.status_code, 204)

        # delete again -> 404
        r4 = self.client.delete(
            f"/api/social/comment/{cid}",
            headers={"Authorization": f"Bearer {self.tok1}"},
        )
        self.assertEqual(r4.status_code, 404)


if __name__ == '__main__':
    unittest.main()


