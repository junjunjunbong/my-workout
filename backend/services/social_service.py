"""
Social service utilities for activities, follows, likes, and comments.
"""
import sqlite3
from typing import Optional, List
from fastapi import HTTPException
from .user_service import get_db_connection


def record_activity(user_id: int, activity_type: str, ref_id: Optional[str] = None) -> int:
    """
    Insert a generic activity.
    """
    with get_db_connection() as conn:
        cur = conn.execute(
            "INSERT INTO activities (user_id, type, ref_id) VALUES (?,?,?)",
            (int(user_id), str(activity_type), ref_id if ref_id is not None else None),
        )
        conn.commit()
        return cur.lastrowid


def follow_user(follower_id: int, followee_id: int):
    if follower_id == followee_id:
        raise HTTPException(status_code=400, detail="Cannot follow yourself")
    with get_db_connection() as conn:
        row = conn.execute("SELECT id FROM users WHERE id = ?", (followee_id,)).fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Target user not found")
        try:
            conn.execute(
                "INSERT INTO follows (follower_id, followee_id) VALUES (?, ?)",
                (follower_id, followee_id),
            )
            conn.commit()
        except sqlite3.IntegrityError:
            raise HTTPException(status_code=409, detail="Already following")


def unfollow_user(follower_id: int, followee_id: int):
    with get_db_connection() as conn:
        cur = conn.execute(
            "DELETE FROM follows WHERE follower_id = ? AND followee_id = ?",
            (follower_id, followee_id),
        )
        conn.commit()
        if cur.rowcount == 0:
            raise HTTPException(status_code=404, detail="Not following")


def get_feed(user_id: int, limit: int, cursor: Optional[str] = None) -> dict:
    limit = min(limit, 50) if limit > 0 else 20
    cursor_ts, cursor_id = None, None
    if cursor:
        try:
            parts = cursor.split("|")
            if len(parts) != 2:
                raise ValueError("Invalid cursor format")
            cursor_ts, cursor_id = parts[0], int(parts[1])
        except (ValueError, IndexError):
            raise HTTPException(status_code=400, detail="Invalid cursor")

    with get_db_connection() as conn:
        params = [user_id]
        sql = (
            "SELECT a.id, a.user_id, a.type, a.ref_id, a.created_at "
            "FROM activities a "
            "WHERE a.user_id IN (SELECT followee_id FROM follows WHERE follower_id = ?)"
        )
        if cursor_ts is not None:
            sql += " AND (a.created_at < ? OR (a.created_at = ? AND a.id < ?))"
            params.extend([cursor_ts, cursor_ts, cursor_id])
        sql += " ORDER BY a.created_at DESC, a.id DESC LIMIT ?"
        params.append(limit)
        rows = conn.execute(sql, tuple(params)).fetchall()

    items = [dict(row) for row in rows]
    next_cursor = None
    if len(items) == limit:
        last = items[-1]
        next_cursor = f"{last['created_at']}|{last['id']}"
    return {"items": items, "nextCursor": next_cursor}


def like_item(user_id: int, ref_id: str):
    if not ref_id or not ref_id.strip():
        raise HTTPException(status_code=400, detail="ref_id required")
    with get_db_connection() as conn:
        try:
            conn.execute("INSERT INTO likes (user_id, ref_id) VALUES (?,?)", (user_id, ref_id))
            conn.commit()
        except sqlite3.IntegrityError:
            raise HTTPException(status_code=409, detail="Already liked")


def unlike_item(user_id: int, ref_id: str):
    if not ref_id or not ref_id.strip():
        raise HTTPException(status_code=400, detail="ref_id required")
    with get_db_connection() as conn:
        cur = conn.execute("DELETE FROM likes WHERE user_id = ? AND ref_id = ?", (user_id, ref_id))
        conn.commit()
        if cur.rowcount == 0:
            raise HTTPException(status_code=404, detail="Like not found")


def create_comment(user_id: int, ref_id: str, content: str) -> dict:
    content = (content or "").strip()
    if not content:
        raise HTTPException(status_code=400, detail="content required")
    if len(content) > 500:
        raise HTTPException(status_code=400, detail="content too long")
    with get_db_connection() as conn:
        cur = conn.execute(
            "INSERT INTO comments (user_id, ref_id, content) VALUES (?,?,?)",
            (user_id, ref_id, content),
        )
        conn.commit()
        cid = cur.lastrowid
        row = conn.execute(
            "SELECT id, user_id, ref_id, content, created_at FROM comments WHERE id = ?",
            (cid,),
        ).fetchone()
        return dict(row)


def get_comments(ref_id: str) -> List[dict]:
    if not ref_id or not ref_id.strip():
        raise HTTPException(status_code=400, detail="ref_id required")
    with get_db_connection() as conn:
        rows = conn.execute(
            "SELECT id, user_id, ref_id, content, created_at FROM comments WHERE ref_id = ? ORDER BY created_at ASC, id ASC",
            (ref_id,),
        ).fetchall()
    return [dict(row) for row in rows]


def delete_comment(comment_id: int, user_id: int):
    with get_db_connection() as conn:
        cur = conn.execute(
            "DELETE FROM comments WHERE id = ? AND user_id = ?",
            (comment_id, user_id),
        )
        conn.commit()
        if cur.rowcount == 0:
            raise HTTPException(status_code=404, detail="Comment not found")
