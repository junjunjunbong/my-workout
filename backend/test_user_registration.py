"""
Unit tests for the user registration API endpoint.
"""

import unittest
import sqlite3
import os
import tempfile
import json
from fastapi.testclient import TestClient
from database import MigrationManager
from main import app

class TestUserRegistration(unittest.TestCase):
    def setUp(self):
        """Set up test environment with a temporary database."""
        # Create a temporary database for testing
        self.temp_fd, self.db_path = tempfile.mkstemp(suffix='.db')
        
        # Set the database path in the app
        # We need to modify the app to use our test database
        import services.user_service
        services.user_service.DB_PATH = self.db_path
        
        # Run migrations
        migration_manager = MigrationManager(self.db_path)
        migration_manager.run_migrations()
        
        # Create test client
        self.client = TestClient(app)
    
    def tearDown(self):
        """Clean up test environment."""
        try:
            os.close(self.temp_fd)
        except OSError:
            pass
            
        # Try to remove the database file, but don't fail if we can't
        try:
            if os.path.exists(self.db_path):
                os.remove(self.db_path)
        except PermissionError:
            # On Windows, the file might still be locked by the database connection
            pass
    
    def test_successful_registration(self):
        """Test successful user registration."""
        response = self.client.post("/api/auth/register", json={
            "email": "test@example.com",
            "password": "TestPass123!"
        })
        
        # Check response status
        self.assertEqual(response.status_code, 201)
        
        # Check response content
        data = response.json()
        self.assertTrue(data["success"])
        self.assertEqual(data["message"], "User registered successfully")
        self.assertIsNotNone(data["user_id"])
        
        # Verify user was actually created in database
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("SELECT id, email FROM users WHERE email = ?", ("test@example.com",))
            user = cursor.fetchone()
            self.assertIsNotNone(user)
            self.assertEqual(user[1], "test@example.com")
    
    def test_duplicate_email_registration(self):
        """Test registration with duplicate email."""
        # First registration
        response1 = self.client.post("/api/auth/register", json={
            "email": "test@example.com",
            "password": "TestPass123!"
        })
        self.assertEqual(response1.status_code, 201)
        
        # Second registration with same email
        response2 = self.client.post("/api/auth/register", json={
            "email": "test@example.com",
            "password": "AnotherPass456@"
        })
        
        # Check response status
        self.assertEqual(response2.status_code, 409)
        
        # Check response content
        data = response2.json()
        self.assertIn("detail", data)
        self.assertEqual(data["detail"], "User with this email already exists")
    
    def test_invalid_email_format(self):
        """Test registration with invalid email format."""
        response = self.client.post("/api/auth/register", json={
            "email": "invalid-email",
            "password": "TestPass123!"
        })
        
        # Check response status
        self.assertEqual(response.status_code, 422)
        
        # Check response content
        data = response.json()
        self.assertIn("detail", data)
    
    def test_weak_password(self):
        """Test registration with weak password."""
        response = self.client.post("/api/auth/register", json={
            "email": "test@example.com",
            "password": "weak"
        })
        
        # Check response status
        self.assertEqual(response.status_code, 422)
        
        # Check response content
        data = response.json()
        self.assertIn("detail", data)
    
    def test_missing_fields(self):
        """Test registration with missing fields."""
        response = self.client.post("/api/auth/register", json={
            "email": "test@example.com"
            # Missing password
        })
        
        # Check response status
        self.assertEqual(response.status_code, 422)
        
        # Check response content
        data = response.json()
        self.assertIn("detail", data)

if __name__ == '__main__':
    unittest.main()