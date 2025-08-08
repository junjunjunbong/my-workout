import unittest
import os
import tempfile
import json
import sqlite3
from database import MigrationManager

class TestSeedFromJson(unittest.TestCase):
    def setUp(self):
        self.temp_fd, self.db_path = tempfile.mkstemp(suffix='.db')
        self.tmpdir = tempfile.mkdtemp()
        # Create minimal workouts.json and routines.json in a temp directory one level above backend
        # Our migration reads from backend/.. (project root). We'll emulate by writing to that path via cwd chdir in test.

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

    def test_seed(self):
        # Prepare JSON in a temp folder and run migrations with patched cwd
        workouts = [
            {"id":"w1","date":"2025-08-05","category":"가슴","exercise":"벤치프레스","type":"strength","sets":[{"weight_kg":60,"reps":10}],"notes":"테스트"}
        ]
        routines = [
            {"id":"r1","name":"루틴A","memo":"메모","items":[{"exercise":"벤치","category":"가슴","sets":3,"reps":"8-10"}]}
        ]
        # Write to project root relative path used by migration: backend/.. == project root
        proj_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
        wfp = os.path.join(proj_root, 'workouts.json')
        rfp = os.path.join(proj_root, 'routines.json')
        with open(wfp,'w',encoding='utf-8') as f: json.dump(workouts, f, ensure_ascii=False)
        with open(rfp,'w',encoding='utf-8') as f: json.dump(routines, f, ensure_ascii=False)

        try:
            mgr = MigrationManager(self.db_path)
            mgr.run_migrations()
            with sqlite3.connect(self.db_path) as conn:
                c1 = conn.execute("SELECT count(*) FROM workouts").fetchone()[0]
                self.assertEqual(c1, 1)
                c2 = conn.execute("SELECT count(*) FROM workout_sets").fetchone()[0]
                self.assertEqual(c2, 1)
                c3 = conn.execute("SELECT count(*) FROM routines").fetchone()[0]
                self.assertEqual(c3, 1)
                c4 = conn.execute("SELECT count(*) FROM routine_items").fetchone()[0]
                self.assertEqual(c4, 1)
        finally:
            # cleanup created jsons
            for p in (wfp, rfp):
                try:
                    if os.path.exists(p):
                        os.remove(p)
                except PermissionError:
                    pass

if __name__ == '__main__':
    unittest.main()