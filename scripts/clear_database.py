"""
Database clear script.

Drops all tables, enum types, and clears the alembic version table.
Use this to reset the database before running migrations.

Usage:
    python scripts/clear_database.py [--force]
"""

import os
import sys

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import text
from config.database import engine


def clear_database(force: bool = False) -> None:
    """
    Clear all tables and enum types from the database.
    
    Args:
        force: If True, skip confirmation prompt.
    """
    if not force:
        print("WARNING: This will delete all data in the database!")
        response = input("Are you sure you want to continue? (yes/no): ")
        if response.lower() != 'yes':
            print("Aborted.")
            return
    
    conn = engine.connect()
    
    # Get all tables in public schema
    tables = conn.execute(
        text("SELECT tablename FROM pg_tables WHERE schemaname = 'public'")
    ).fetchall()
    
    if tables:
        print(f"Dropping {len(tables)} table(s)...")
        # Drop each table with CASCADE
        for table in tables:
            table_name = table[0]
            print(f"  - Dropping table: {table_name}")
            conn.execute(text(f"DROP TABLE IF EXISTS {table_name} CASCADE"))
    else:
        print("No tables found.")
    
    # Get custom enum types
    enums = conn.execute(
        text("SELECT typname FROM pg_type WHERE typtype = 'e'")
    ).fetchall()
    
    if enums:
        print(f"Dropping {len(enums)} enum type(s)...")
        for enum in enums:
            enum_name = enum[0]
            print(f"  - Dropping enum: {enum_name}")
            conn.execute(text(f"DROP TYPE IF EXISTS {enum_name} CASCADE"))
    else:
        print("No enum types found.")
    
    # Get custom sequences (excluding auto-generated ones)
    sequences = conn.execute(
        text("SELECT sequencename FROM pg_sequences WHERE schemaname = 'public'")
    ).fetchall()
    
    if sequences:
        print(f"Dropping {len(sequences)} sequence(s)...")
        for seq in sequences:
            seq_name = seq[0]
            print(f"  - Dropping sequence: {seq_name}")
            conn.execute(text(f"DROP SEQUENCE IF EXISTS {seq_name} CASCADE"))
    
    conn.commit()
    print("\nDatabase cleared successfully!")


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Clear database (drop all tables)')
    parser.add_argument('--force', '-f', action='store_true', 
                        help='Skip confirmation prompt')
    
    args = parser.parse_args()
    
    clear_database(args.force)


if __name__ == '__main__':
    main()
