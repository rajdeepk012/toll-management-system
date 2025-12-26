"""
Create Database Tables

This script creates all tables in the MySQL database.
Run this ONCE to initialize the database schema.

Usage:
    python3 database/create_tables.py
"""

from database.config import engine, Base
from database.db_models import TollDB, VehicleDB, TollPassDB, TransactionDB, TollBoothDB


def create_tables():
    """Create all tables in the database"""
    print("\n" + "="*80)
    print("  Creating Database Tables...")
    print("="*80 + "\n")

    # This creates all tables defined in our models
    Base.metadata.create_all(bind=engine)

    print("✓ Tables created successfully!")
    print("\nTables created:")
    print("  - tolls")
    print("  - vehicles")
    print("  - toll_passes")
    print("  - transactions")
    print("  - toll_booths")
    print("\n" + "="*80 + "\n")


if __name__ == "__main__":
    create_tables()
