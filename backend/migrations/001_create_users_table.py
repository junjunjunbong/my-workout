"""
Migration script to create the users table.
"""

def upgrade(connection):
    """
    Create the users table with the following schema:
    - id: Primary key, auto-incrementing integer
    - email: Unique, indexed string
    - password_hash: String (length 255)
    - created_at: Timestamp
    - updated_at: Timestamp
    """
    create_table_sql = """
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """
    
    create_index_sql = """
    CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
    """
    
    connection.execute(create_table_sql)
    connection.execute(create_index_sql)
    connection.commit()

def downgrade(connection):
    """
    Drop the users table and associated index.
    """
    drop_index_sql = "DROP INDEX IF EXISTS idx_users_email;"
    drop_table_sql = "DROP TABLE IF EXISTS users;"
    
    connection.execute(drop_index_sql)
    connection.execute(drop_table_sql)
    connection.commit()