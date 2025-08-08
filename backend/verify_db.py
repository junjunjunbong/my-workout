```
"""
Script to verify the database schema.
"""

import sqlite3
import os

# Database path
db_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'workout.db')

# Connect to the database and check the schema
with sqlite3.connect(db_path) as conn:
    cursor = conn.execute("""
        SELECT name FROM sqlite_master 
        WHERE type='table' AND name='users';
    """)
    result = cursor.fetchone()
    
    if result:
        print(f"Table '{result[0]}' exists in the database.")
        
        # Check table schema
        cursor = conn.execute("PRAGMA table_info(users);")
        columns = cursor.fetchall()
        
        print("\nTable schema:")
        for col in columns:
            print(f"  {col[1]} ({col[2]}) {'PRIMARY KEY' if col[5] > 0 else ''} {'NOT NULL' if col[3] > 0 else ''}")
        
        # Check if email is unique
        cursor = conn.execute("SELECT sql FROM sqlite_master WHERE name='users';")
        table_sql = cursor.fetchone()[0]
        if 'email TEXT UNIQUE NOT NULL' in table_sql:
            print("\nEmail column is correctly set as UNIQUE and NOT NULL.")
        else:
            print("\nEmail column is NOT correctly set as UNIQUE and NOT NULL.")
    else:
        print("Users table does not exist in the database.")
```