"""
Migration to add social follows and activities (feed) tables.

Tables:
- follows(follower_id, followee_id, created_at, UNIQUE(follower_id, followee_id))
- activities(id, user_id, type, ref_id, created_at)
"""

def upgrade(connection):
    # Create follows table
    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS follows (
            follower_id INTEGER NOT NULL,
            followee_id INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE (follower_id, followee_id)
        );
        """
    )
    # Helpful indexes for follower/followee lookups
    connection.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_follows_follower_id ON follows(follower_id);
        """
    )
    connection.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_follows_followee_id ON follows(followee_id);
        """
    )

    # Create activities table
    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS activities (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            type TEXT NOT NULL,
            ref_id TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
    )
    # Helpful indexes for feed queries
    connection.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_activities_user_id ON activities(user_id);
        """
    )
    connection.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_activities_created_at ON activities(created_at);
        """
    )
    connection.commit()


def downgrade(connection):
    # Drop indexes then tables (SQLite allows DROP INDEX IF EXISTS)
    connection.execute("DROP INDEX IF EXISTS idx_activities_created_at;")
    connection.execute("DROP INDEX IF EXISTS idx_activities_user_id;")
    connection.execute("DROP TABLE IF EXISTS activities;")

    connection.execute("DROP INDEX IF EXISTS idx_follows_followee_id;")
    connection.execute("DROP INDEX IF EXISTS idx_follows_follower_id;")
    connection.execute("DROP TABLE IF EXISTS follows;")
    connection.commit()


