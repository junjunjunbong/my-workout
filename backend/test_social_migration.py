import unittest
import os
import tempfile
import sqlite3
from database import MigrationManager


class TestSocialMigration(unittest.TestCase):
    def test_social_tables_created(self):
        temp_fd, db_path = tempfile.mkstemp(suffix='.db')
        try:
            mgr = MigrationManager(db_path)
            mgr.run_migrations()

            with sqlite3.connect(db_path) as conn:
                # follows table exists
                t1 = conn.execute("""
                    SELECT name FROM sqlite_master
                    WHERE type='table' AND name='follows';
                """).fetchone()
                self.assertIsNotNone(t1)

                # activities table exists
                t2 = conn.execute("""
                    SELECT name FROM sqlite_master
                    WHERE type='table' AND name='activities';
                """).fetchone()
                self.assertIsNotNone(t2)

                # unique constraint simulated by index on follows
                idx_unique = conn.execute("""
                    SELECT name FROM sqlite_master
                    WHERE type='index' AND name LIKE 'sqlite_autoindex_follows%';
                """).fetchone()
                self.assertIsNotNone(idx_unique)

                # indexes present
                idx1 = conn.execute("SELECT name FROM sqlite_master WHERE type='index' AND name='idx_follows_follower_id';").fetchone()
                idx2 = conn.execute("SELECT name FROM sqlite_master WHERE type='index' AND name='idx_follows_followee_id';").fetchone()
                self.assertIsNotNone(idx1)
                self.assertIsNotNone(idx2)

                idx3 = conn.execute("SELECT name FROM sqlite_master WHERE type='index' AND name='idx_activities_user_id';").fetchone()
                idx4 = conn.execute("SELECT name FROM sqlite_master WHERE type='index' AND name='idx_activities_created_at';").fetchone()
                self.assertIsNotNone(idx3)
                self.assertIsNotNone(idx4)
        finally:
            try:
                os.close(temp_fd)
            except OSError:
                pass
            try:
                if os.path.exists(db_path):
                    os.remove(db_path)
            except PermissionError:
                pass


if __name__ == '__main__':
    unittest.main()


