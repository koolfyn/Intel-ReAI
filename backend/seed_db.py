#!/usr/bin/env python3
"""
Script to seed the database with fake data
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import init_db, SessionLocal
from app.data.seed_data import seed_database

def main():
    """Seed the database with fake data"""
    print("Initializing database...")
    init_db()

    print("Seeding database with fake data...")
    db = SessionLocal()
    try:
        seed_database(db)
        print("Database seeded successfully!")
    except Exception as e:
        print(f"Error seeding database: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    main()
