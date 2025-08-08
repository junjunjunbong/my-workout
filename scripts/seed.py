import os
import sqlite3
from datetime import datetime, timedelta

DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'backend', 'data', 'workout.db')
DB_PATH = os.path.normpath(DB_PATH)

def seed_users(conn):
    users = [
        ('demo1@example.com', '$2b$12$TtHn3v2m7j1JwQ8C7b1t9uYv3Qb2qT0Hn0y7o5m2xJ5HkG8Yt2G1a'),  # Demo1234!
        ('demo2@example.com', '$2b$12$TtHn3v2m7j1JwQ8C7b1t9uYv3Qb2qT0Hn0y7o5m2xJ5HkG8Yt2G1a'),
    ]
    for email, pw in users:
        try:
            conn.execute("INSERT INTO users (email, password_hash) VALUES (?, ?)", (email, pw))
        except sqlite3.IntegrityError:
            pass

def seed_follows(conn):
    # user1 follows user2
    conn.execute("INSERT OR IGNORE INTO follows (follower_id, followee_id) VALUES (1, 2)")

def seed_activities(conn):
    now = datetime.utcnow()
    for i in range(5):
        ts = (now - timedelta(days=i)).isoformat(timespec='seconds')
        conn.execute("INSERT INTO activities (user_id, type, ref_id, created_at) VALUES (?,?,?,?)",
                     (2, 'workout', f'demo-{i+1}', ts))

def seed_workouts_json():
    # keep JSON demo data minimal; backend reads from backend/data/*.json
    base = os.path.join(os.path.dirname(__file__), '..', 'backend', 'data')
    os.makedirs(base, exist_ok=True)
    import json
    workouts = [
        {"id": "w1", "date": (datetime.utcnow()-timedelta(days=2)).date().isoformat(), "category": "상체", "exercise": "벤치프레스", "type": "strength", "sets": [{"weight_kg": 60, "reps": 10}]},
        {"id": "w2", "date": (datetime.utcnow()-timedelta(days=1)).date().isoformat(), "category": "하체", "exercise": "스쿼트", "type": "strength", "sets": [{"weight_kg": 80, "reps": 8}]},
    ]
    with open(os.path.join(base, 'workouts.json'), 'w', encoding='utf-8') as f:
        json.dump(workouts, f, ensure_ascii=False, indent=2)

def main():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    try:
        seed_users(conn)
        seed_follows(conn)
        seed_activities(conn)
        conn.commit()
    finally:
        conn.close()
    seed_workouts_json()
    print('Seed complete. Demo users: demo1@example.com / demo2@example.com (password: Demo1234!)')

if __name__ == '__main__':
    main()


