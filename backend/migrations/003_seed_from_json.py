"""
One-off migration to seed workouts and routines from JSON storage into SQLite tables.
Creates basic tables if not present and copies data from storage JSON files.
"""
import os
import json

def _ensure_tables(conn):
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS workouts (
            id TEXT PRIMARY KEY,
            date TEXT,
            category TEXT,
            exercise TEXT,
            type TEXT,
            notes TEXT
        );
        """
    )
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS workout_sets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            workout_id TEXT,
            weight_kg REAL,
            reps INTEGER
        );
        """
    )
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS routines (
            id TEXT PRIMARY KEY,
            name TEXT,
            memo TEXT
        );
        """
    )
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS routine_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            routine_id TEXT,
            exercise TEXT,
            category TEXT,
            sets INTEGER,
            reps TEXT
        );
        """
    )
    conn.commit()


def upgrade(connection):
    # Load JSON files located relative to backend/storage helpers
    root = os.path.dirname(os.path.dirname(__file__))
    json_dir = os.path.join(root, '..')
    def _read_json(name):
        fp = os.path.join(json_dir, f"{name}.json")
        if not os.path.exists(fp):
            return []
        with open(fp, 'r', encoding='utf-8') as f:
            try:
                return json.load(f)
            except Exception:
                return []

    _ensure_tables(connection)

    # Seed workouts
    workouts = _read_json('workouts')
    for w in workouts:
        connection.execute(
            "INSERT OR IGNORE INTO workouts (id, date, category, exercise, type, notes) VALUES (?,?,?,?,?,?)",
            (w.get('id'), w.get('date'), w.get('category'), w.get('exercise'), w.get('type'), w.get('notes'))
        )
        for s in (w.get('sets') or []):
            connection.execute(
                "INSERT INTO workout_sets (workout_id, weight_kg, reps) VALUES (?,?,?)",
                (w.get('id'), float(s.get('weight_kg', 0) or 0), int(s.get('reps', 0) or 0))
            )
    # Seed routines
    routines = _read_json('routines')
    for r in routines:
        connection.execute(
            "INSERT OR IGNORE INTO routines (id, name, memo) VALUES (?,?,?)",
            (r.get('id'), r.get('name'), r.get('memo'))
        )
        for item in (r.get('items') or []):
            connection.execute(
                "INSERT INTO routine_items (routine_id, exercise, category, sets, reps) VALUES (?,?,?,?,?)",
                (r.get('id'), item.get('exercise'), item.get('category'), int(item.get('sets') or 0), str(item.get('reps') or ''))
            )
    connection.commit()


def downgrade(connection):
    # No-op: data destructive rollback omitted
    pass