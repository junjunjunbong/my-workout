import unittest
import os
import tempfile
import json
from fastapi.testclient import TestClient

from main import app
import storage


class TestAnalyticsPR(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        storage.DATA_DIR = self.tmpdir
        # seed workouts.json
        workouts = [
            {"id": "w1", "date": "2025-01-01", "category": "Chest", "exercise": "Bench Press", "type": "strength", "sets": [
                {"weight_kg": 80, "reps": 5},
                {"weight_kg": 85, "reps": 3}
            ]},
            {"id": "w2", "date": "2025-01-05", "category": "Chest", "exercise": "Bench Press", "type": "strength", "sets": [
                {"weight_kg": 90, "reps": 2}
            ]},
            {"id": "w3", "date": "2025-01-10", "category": "Back", "exercise": "Deadlift", "type": "strength", "sets": [
                {"weight_kg": 140, "reps": 3}
            ]},
        ]
        os.makedirs(self.tmpdir, exist_ok=True)
        with open(os.path.join(self.tmpdir, 'workouts.json'), 'w', encoding='utf-8') as f:
            json.dump(workouts, f)
        self.client = TestClient(app)

    def test_pr_trend_range(self):
        resp = self.client.get("/api/analytics/pr-trend", params={"exercise": "Bench Press", "start": "2025-01-01", "end": "2025-01-07"})
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        # Expect two points: 2025-01-01 and 2025-01-05
        self.assertEqual(len(data), 2)
        dates = [p["date"] for p in data]
        self.assertEqual(dates, ["2025-01-01", "2025-01-05"])
        # Check monotonic non-decreasing (since PR could go up)
        vals = [p["one_rm"] for p in data]
        self.assertGreater(vals[1], vals[0])


