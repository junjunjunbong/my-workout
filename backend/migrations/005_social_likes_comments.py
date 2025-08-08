"""
Migration to add likes and comments tables.

Tables:
- likes(user_id, ref_id, created_at, UNIQUE(user_id, ref_id))
- comments(id, user_id, ref_id, content, created_at)
"""

def upgrade(connection):
    # likes table
    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS likes (
            user_id INTEGER NOT NULL,
            ref_id TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE (user_id, ref_id)
        );
        """
    )
    connection.execute("CREATE INDEX IF NOT EXISTS idx_likes_user_id ON likes(user_id);")
    connection.execute("CREATE INDEX IF NOT EXISTS idx_likes_ref_id ON likes(ref_id);")

    # comments table
    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS comments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            ref_id TEXT NOT NULL,
            content TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
    )
    connection.execute("CREATE INDEX IF NOT EXISTS idx_comments_ref_id ON comments(ref_id);")
    connection.execute("CREATE INDEX IF NOT EXISTS idx_comments_created_at ON comments(created_at);")
    connection.commit()


def downgrade(connection):
    connection.execute("DROP INDEX IF EXISTS idx_comments_created_at;")
    connection.execute("DROP INDEX IF EXISTS idx_comments_ref_id;")
    connection.execute("DROP TABLE IF EXISTS comments;")

    connection.execute("DROP INDEX IF EXISTS idx_likes_ref_id;")
    connection.execute("DROP INDEX IF EXISTS idx_likes_user_id;")
    connection.execute("DROP TABLE IF EXISTS likes;")
    connection.commit()


