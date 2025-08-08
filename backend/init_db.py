"""
Script to initialize the database and run migrations.
"""

import os
import sys
from database import MigrationManager

def init_database():
    """Initialize the database and run all migrations."""
    # Add the backend directory to the Python path
    backend_dir = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, backend_dir)
    
    # Ensure the data directory exists
    data_dir = os.path.join(backend_dir, '..', 'data')
    os.makedirs(data_dir, exist_ok=True)
    
    # Database path
    db_path = os.path.join(data_dir, 'workout.db')
    
    # Run migrations
    migration_manager = MigrationManager(db_path)
    migration_manager.run_migrations()
    
    print(f"Database initialized at: {db_path}")

if __name__ == "__main__":
    init_database()