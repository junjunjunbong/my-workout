import json
import os
from typing import List, Any

DATA_DIR = "data"

def ensure_data_dir():
    """Ensure the data directory exists"""
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)

def read_json(filename: str) -> List[Any]:
    """Read data from a JSON file"""
    ensure_data_dir()
    filepath = os.path.join(DATA_DIR, f"{filename}.json")
    if not os.path.exists(filepath):
        return []
    with open(filepath, 'r', encoding='utf-8') as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return []

def write_json(filename: str, data: List[Any]):
    """Write data to a JSON file"""
    ensure_data_dir()
    filepath = os.path.join(DATA_DIR, f"{filename}.json")
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def append_workouts(workouts: List[Any]):
    """Append workouts to the workouts file"""
    ensure_data_dir()
    filepath = os.path.join(DATA_DIR, "workouts.json")
    existing = read_json("workouts")
    existing.extend(workouts)
    write_json("workouts", existing)