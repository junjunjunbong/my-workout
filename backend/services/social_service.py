"""
Social service utilities for activities.
"""
from typing import Optional
from .user_service import get_db_connection


def record_activity(user_id: int, activity_type: str, ref_id: Optional[str] = None) -> int:
    """
    Insert a generic activity for feed testing.
    Returns the inserted activity id.
    Uses the shared DB connection helper to honor dynamic DB_PATH during tests.
    """
    with get_db_connection() as conn:
        cur = conn.execute(
            "INSERT INTO activities (user_id, type, ref_id) VALUES (?,?,?)",
            (int(user_id), str(activity_type), ref_id if ref_id is not None else None),
        )
        conn.commit()
        return cur.lastrowid


