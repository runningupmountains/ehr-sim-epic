"""
Create all tables in the EHR simulator database.

Usage:
    python scripts/init_db.py
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db import Base, engine
import app.models  # noqa: F401 — registers all ORM models with Base


def main():
    print("Creating EHR simulator tables...")
    Base.metadata.create_all(bind=engine)
    print("Done. Tables created:")
    for table in Base.metadata.sorted_tables:
        print(f"  - {table.name}")


if __name__ == "__main__":
    main()
