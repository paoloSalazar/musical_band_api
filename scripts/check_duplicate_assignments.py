"""
Check for duplicate assignments in event_musicians table.

This is needed before adding the unique constraint on (event_id, musician_id).
"""

import os
import sys
from sqlalchemy import text

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.database import engine


def check_duplicate_assignments():
    """
    Check for duplicate musician assignments to the same event.
    """
    print("CHECKING FOR DUPLICATE ASSIGNMENTS")
    print("=" * 50)

    with engine.connect() as conn:
        # Query for duplicates
        duplicate_query = text("""
            SELECT event_id, musician_id, COUNT(*) as count
            FROM event_musicians
            GROUP BY event_id, musician_id
            HAVING COUNT(*) > 1
            ORDER BY event_id, musician_id;
        """)

        duplicates = conn.execute(duplicate_query).fetchall()

        if duplicates:
            print(f"Found {len(duplicates)} duplicate assignment(s):")
            print("-" * 60)
            for dup in duplicates:
                print(f"Event ID: {dup[0]}, Musician ID: {dup[1]}, Count: {dup[2]}")
            print("-" * 60)
            return len(duplicates)
        else:
            print("No duplicate assignments found.")
            return 0


if __name__ == '__main__':
    duplicates = check_duplicate_assignments()
    if duplicates > 0:
        print(f"\nERROR: {duplicates} duplicate assignment(s) found!")
        print("Cannot add unique constraint until duplicates are resolved.")
        sys.exit(1)
    else:
        print("\nSUCCESS: No duplicates found. Safe to add unique constraint.")