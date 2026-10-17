"""Script to initialize SQLite database tables, indexes, and schema versions."""

import sys
from pathlib import Path

# Add src to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from signalpost.database import db
from signalpost.config import settings

def main():
    print(f"Initializing Signalpost SQLite Database at: {settings.get_db_path()}")
    db.init_db()
    print("✓ Schema initialized successfully.")
    print("✓ Created tables: schema_versions, companies, sources, facts, snapshots, changes, research_runs.")

if __name__ == "__main__":
    main()
