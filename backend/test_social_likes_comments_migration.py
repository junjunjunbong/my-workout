import unittest
import os
import tempfile
import sqlite3
from database import MigrationManager


class TestLikesCommentsMigration(unittest.TestCase):
    def test_tables_created(self):
        temp_fd, db_path = tempfile.mkstemp(suffix='.db')
        try:
            MigrationManager(db_path).run_migrations()
            with sqlite3.connect(db_path) as conn:
                t1 = conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='likes';").fetchone()
                t2 = conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='comments';").fetchone()
                self.assertIsNotNone(t1)
                self.assertIsNotNone(t2)

                i1 = conn.execute("SELECT name FROM sqlite_master WHERE type='index' AND name='idx_likes_user_id';").fetchone()
                i2 = conn.execute("SELECT name FROM sqlite_master WHERE type='index' AND name='idx_likes_ref_id';").fetchone()
                self.assertIsNotNone(i1)
                self.assertIsNotNone(i2)

                i3 = conn.execute("SELECT name FROM sqlite_master WHERE type='index' AND name='idx_comments_ref_id';").fetchone()
                i4 = conn.execute("SELECT name FROM sqlite_master WHERE type='index' AND name='idx_comments_created_at';").fetchone()
                self.assertIsNotNone(i3)
                self.assertIsNotNone(i4)
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


