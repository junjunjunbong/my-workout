"""
Integration tests for the login endpoint and JWT-protected route.
"""
import unittest
import os
import tempfile
import sqlite3
from fastapi.testclient import TestClient

from main import app
from database import MigrationManager
import services.user_service as user_service

class TestAuthLogin(unittest.TestCase):
    def setUp(self):
        self.temp_fd, self.db_path = tempfile.mkstemp(suffix='.db')
        # Point user_service to temp DB and run migrations
        user_service.DB_PATH = self.db_path
        MigrationManager(self.db_path).run_migrations()
        self.client = TestClient(app)

        # Create a test user directly via service
        self.email = "login@example.com"
        self.password = "StrongPass1!"
        user_service.create_user(self.email, self.password)

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

    def test_login_success_and_access_protected(self):
        # Login
        resp = self.client.post("/api/auth/login", json={"email": self.email, "password": self.password})
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertTrue(data.get("success"))
        token = data.get("token")
        self.assertIsNotNone(token)
        self.assertIsNotNone(data.get("user_id"))

        # Access protected route
        resp2 = self.client.get("/api/protected/ping", headers={"Authorization": f"Bearer {token}"})
        self.assertEqual(resp2.status_code, 200)
        pdata = resp2.json()
        self.assertEqual(pdata.get("message"), "pong")
        self.assertEqual(pdata.get("user_id"), data.get("user_id"))

    def test_login_wrong_password(self):
        resp = self.client.post("/api/auth/login", json={"email": self.email, "password": "WrongPass!"})
        self.assertEqual(resp.status_code, 401)

    def test_login_nonexistent_user(self):
        resp = self.client.post("/api/auth/login", json={"email": "nouser@example.com", "password": "Whatever1!"})
        self.assertEqual(resp.status_code, 401)

    def test_protected_requires_token(self):
        resp = self.client.get("/api/protected/ping")
        self.assertEqual(resp.status_code, 401)

    def test_protected_invalid_token(self):
        resp = self.client.get("/api/protected/ping", headers={"Authorization": "Bearer invalid.token.here"})
        self.assertEqual(resp.status_code, 401)

if __name__ == '__main__':
    unittest.main()