"""
Database migration manager for handling schema changes.
"""

import sqlite3
import os
from typing import List

class MigrationManager:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.migrations_dir = os.path.join(os.path.dirname(__file__), 'migrations')
        self._ensure_migrations_table()
    
    def _ensure_migrations_table(self):
        """Create the migrations tracking table if it doesn't exist."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS schema_migrations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    version TEXT UNIQUE NOT NULL,
                    applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
            conn.commit()
    
    def get_applied_migrations(self) -> List[str]:
        """Get list of applied migrations."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("SELECT version FROM schema_migrations ORDER BY version;")
            return [row[0] for row in cursor.fetchall()]
    
    def mark_migration_applied(self, version: str):
        """Mark a migration as applied."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("INSERT INTO schema_migrations (version) VALUES (?);", (version,))
            conn.commit()
    
    def mark_migration_rolled_back(self, version: str):
        """Mark a migration as rolled back."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("DELETE FROM schema_migrations WHERE version = ?;", (version,))
            conn.commit()
    
    def get_available_migrations(self) -> List[str]:
        """Get list of available migrations from the migrations directory."""
        if not os.path.exists(self.migrations_dir):
            return []
        
        migrations = []
        for filename in sorted(os.listdir(self.migrations_dir)):
            if filename.endswith('.py') and filename != '__init__.py':
                migrations.append(filename[:-3])  # Remove .py extension
        return migrations
    
    def run_migrations(self):
        """Run all pending migrations."""
        applied = self.get_applied_migrations()
        available = self.get_available_migrations()
        
        pending = [m for m in available if m not in applied]
        
        if not pending:
            print("No pending migrations.")
            return
        
        print(f"Running {len(pending)} migration(s): {', '.join(pending)}")
        
        for migration_name in pending:
            self._run_migration(migration_name, 'upgrade')
            self.mark_migration_applied(migration_name)
            print(f"Applied migration: {migration_name}")
    
    def rollback_migration(self, migration_name: str):
        """Rollback a specific migration."""
        if migration_name not in self.get_applied_migrations():
            raise ValueError(f"Migration {migration_name} is not applied.")
        
        self._run_migration(migration_name, 'downgrade')
        self.mark_migration_rolled_back(migration_name)
        print(f"Rolled back migration: {migration_name}")
    
    def _run_migration(self, migration_name: str, direction: str):
        """Run a specific migration in the specified direction."""
        migration_module = __import__(f'migrations.{migration_name}', fromlist=[direction])
        migration_func = getattr(migration_module, direction)
        
        with sqlite3.connect(self.db_path) as conn:
            migration_func(conn)

if __name__ == "__main__":
    # Example usage
    db_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'workout.db')
    manager = MigrationManager(db_path)
    manager.run_migrations()