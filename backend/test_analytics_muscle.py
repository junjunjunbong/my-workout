import unittest
import os
import tempfile
import json
from fastapi.testclient import TestClient

from main import app
import storage


class TestAnalyticsMuscleVolume(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        storage.DATA_DIR = self.tmpdir
        workouts = [
            {"id": "w1", "date": "2025-02-01", "category": "Chest", "exercise": "Bench Press", "type": "strength", "sets": [
                {"weight_kg": 80, "reps": 10}
            ]},
            {"id": "w2", "date": "2025-02-03", "category": "Back", "exercise": "Row", "type": "strength", "sets": [
                {"weight_kg": 60, "reps": 12}
            ]},
            {"id": "w3", "date": "2025-03-01", "category": "Chest", "exercise": "Bench Press", "type": "strength", "sets": [
                {"weight_kg": 70, "reps": 8}
            ]}
        ]
        os.makedirs(self.tmpdir, exist_ok=True)
        with open(os.path.join(self.tmpdir, 'workouts.json'), 'w', encoding='utf-8') as f:
            json.dump(workouts, f)
        self.client = TestClient(app)

    def test_muscle_volume_range(self):
        # Only February range
        resp = self.client.get("/api/analytics/muscle-volume-range", params={"start": "2025-02-01", "end": "2025-02-28"})
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        as_dict = {d["category"]: d["volume"] for d in data}
        # Chest: 80*10=800, Back: 60*12=720
        self.assertAlmostEqual(as_dict.get("Chest", 0), 800)
        self.assertAlmostEqual(as_dict.get("Back", 0), 720)


