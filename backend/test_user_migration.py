"""
Unit tests for the user database schema migration.
"""

import unittest
import sqlite3
import os
import tempfile
from database import MigrationManager

class TestUserMigration(unittest.TestCase):
    def test_users_table_creation(self):
        """Test that the users table is created correctly."""
        # Create a temporary database for testing
        temp_fd, db_path = tempfile.mkstemp(suffix='.db')
        
        try:
            migration_manager = MigrationManager(db_path)
            
            # Run the migration
            migration_manager.run_migrations()
            
            # Connect to the database and verify the table exists
            with sqlite3.connect(db_path) as conn:
                cursor = conn.execute("""
                    SELECT name FROM sqlite_master 
                    WHERE type='table' AND name='users';
                """)
                result = cursor.fetchone()
                self.assertIsNotNone(result, "Users table should exist")
                self.assertEqual(result[0], 'users', "Table name should be 'users'")
                
                # Check table schema
                cursor = conn.execute("PRAGMA table_info(users);")
                columns = cursor.fetchall()
                
                # Verify column structure
                column_names = [col[1] for col in columns]
                expected_columns = ['id', 'email', 'password_hash', 'created_at', 'updated_at', 'avatar_url', 'bio', 'goal']
                self.assertEqual(sorted(column_names), sorted(expected_columns))
                
                # Verify primary key
                primary_keys = [col[1] for col in columns if col[5] > 0]  # col[5] is the pk flag
                self.assertEqual(primary_keys, ['id'])
                
                # Verify email is unique
                cursor = conn.execute("SELECT sql FROM sqlite_master WHERE name='users';")
                table_sql = cursor.fetchone()[0]
                self.assertIn('email TEXT UNIQUE NOT NULL', table_sql)
        finally:
            # Clean up
            try:
                os.close(temp_fd)
            except OSError:
                pass
            
            # Try to remove the database file, but don't fail if we can't
            try:
                if os.path.exists(db_path):
                    os.remove(db_path)
            except PermissionError:
                # On Windows, the file might still be locked by the database connection
                pass
    
    def test_migration_tracking(self):
        """Test that migrations are properly tracked."""
        # Create a temporary database for testing
        temp_fd, db_path = tempfile.mkstemp(suffix='.db')
        
        try:
            migration_manager = MigrationManager(db_path)
            
            # Initially no migrations should be applied
            applied = migration_manager.get_applied_migrations()
            self.assertEqual(len(applied), 0)
            
            # Run migrations
            migration_manager.run_migrations()
            
            # Now all migrations should be applied
            applied = migration_manager.get_applied_migrations()
            self.assertGreaterEqual(len(applied), 3)
            self.assertIn('001_create_users_table', applied)
            self.assertIn('002_add_user_profile_fields', applied)
            self.assertIn('003_seed_from_json', applied)
        finally:
            # Clean up
            try:
                os.close(temp_fd)
            except OSError:
                pass
            
            # Try to remove the database file, but don't fail if we can't
            try:
                if os.path.exists(db_path):
                    os.remove(db_path)
            except PermissionError:
                # On Windows, the file might still be locked by the database connection
                pass

if __name__ == '__main__':
    unittest.main()