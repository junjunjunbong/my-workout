import unittest
import tempfile
from fastapi.testclient import TestClient

from main import app
import storage


class TestExerciseDetail(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        storage.DATA_DIR = self.tmpdir
        self.client = TestClient(app)

    def test_basic_series_and_filtering(self):
        # Seed workouts
        storage.write_json(
            "workouts",
            [
                {"id": "1", "date": "2025-01-01", "category": "Chest", "exercise": "Bench Press", "type": "strength", "sets": [{"weight_kg": 80, "reps": 5}, {"weight_kg": 85, "reps": 3}]},
                {"id": "2", "date": "2025-01-02", "category": "Chest", "exercise": "Bench Press", "type": "strength", "sets": [{"weight_kg": 90, "reps": 2}]},
                {"id": "3", "date": "2025-01-03", "category": "Back", "exercise": "Row", "type": "strength", "sets": [{"weight_kg": 60, "reps": 10}]},
            ],
        )

        r = self.client.get("/api/analytics/exercise-detail", params={"exercise": "Bench Press"})
        self.assertEqual(r.status_code, 200)
        data = r.json()
        # Only two dates for Bench Press
        self.assertEqual(len(data), 2)
        self.assertEqual([d["date"] for d in data], sorted([d["date"] for d in data]))
        # Check volume and top weight exist
        self.assertIn("volume", data[0])
        self.assertIn("top_weight", data[0])

    def test_date_range(self):
        storage.write_json(
            "workouts",
            [
                {"id": "1", "date": "2025-02-01", "category": "Chest", "exercise": "Bench Press", "type": "strength", "sets": [{"weight_kg": 70, "reps": 10}]},
                {"id": "2", "date": "2025-02-10", "category": "Chest", "exercise": "Bench Press", "type": "strength", "sets": [{"weight_kg": 80, "reps": 8}]},
                {"id": "3", "date": "2025-03-01", "category": "Chest", "exercise": "Bench Press", "type": "strength", "sets": [{"weight_kg": 85, "reps": 5}]},
            ],
        )
        r = self.client.get(
            "/api/analytics/exercise-detail",
            params={"exercise": "Bench Press", "start": "2025-02-01", "end": "2025-02-28"},
        )
        self.assertEqual(r.status_code, 200)
        data = r.json()
        self.assertTrue(all("2025-02-" in d["date"] for d in data))


