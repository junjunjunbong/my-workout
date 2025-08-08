"""
Migration to add user profile fields to users table: avatar_url (TEXT), bio (TEXT), goal (TEXT).
"""

def upgrade(connection):
    connection.execute("ALTER TABLE users ADD COLUMN avatar_url TEXT;")
    connection.execute("ALTER TABLE users ADD COLUMN bio TEXT;")
    connection.execute("ALTER TABLE users ADD COLUMN goal TEXT;")
    connection.commit()


def downgrade(connection):
    # SQLite doesn't support DROP COLUMN directly; recreate table without columns
    cursor = connection.cursor()
    cursor.execute("PRAGMA foreign_keys=off;")
    cursor.execute("BEGIN TRANSACTION;")
    cursor.execute(
        """
        CREATE TABLE users_new (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
    )
    cursor.execute("INSERT INTO users_new (id, email, password_hash, created_at, updated_at) SELECT id, email, password_hash, created_at, updated_at FROM users;")
    cursor.execute("DROP TABLE users;")
    cursor.execute("ALTER TABLE users_new RENAME TO users;")
    cursor.execute("PRAGMA foreign_keys=on;")
    connection.commit()