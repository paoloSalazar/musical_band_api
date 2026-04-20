"""
Database audit script for orphaned payment records.

Checks for musician_event_payments that don't have corresponding event_musicians records.
This is part of Phase 1 of the database integrity fix for orphaned payment records.

Usage:
    python scripts/audit_orphaned_payments.py
"""

import os
import sys
from sqlalchemy import text

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.database import engine


def audit_orphaned_payments():
    """
    Audit for orphaned payment records in musician_event_payments table.

    Returns:
        dict: Audit results with counts and details
    """
    print("AUDITING ORPHANED PAYMENT RECORDS")
    print("=" * 50)

    with engine.connect() as conn:
        # Query 1: Get count of orphaned payments
        print("\n1. Counting orphaned payment records...")
        count_query = text("""
            SELECT COUNT(*) as orphaned_payments
            FROM musician_event_payments p
            LEFT JOIN event_musicians em ON p.event_id = em.event_id AND p.musician_id = em.musician_id
            WHERE em.id IS NULL;
        """)

        result = conn.execute(count_query).fetchone()
        orphaned_count = result[0] if result else 0

        print(f"   Found {orphaned_count} orphaned payment record(s)")

        # Query 2: Get detailed orphaned records if any exist
        if orphaned_count > 0:
            print("\n2. Detailed orphaned payment records:")
            detail_query = text("""
                SELECT
                    p.id,
                    p.event_id,
                    p.musician_id,
                    p.amount,
                    p.payment_date,
                    p.notes
                FROM musician_event_payments p
                LEFT JOIN event_musicians em ON p.event_id = em.event_id AND p.musician_id = em.musician_id
                WHERE em.id IS NULL
                ORDER BY p.event_id, p.musician_id, p.payment_date;
            """)

            orphaned_records = conn.execute(detail_query).fetchall()

            print("<10")
            print("-" * 80)
            for record in orphaned_records:
                print(f"Payment ID: {record[0]}")
                print(f"  Event ID: {record[1]}, Musician ID: {record[2]}")
                print(".2f")
                print(f"  Payment Date: {record[4]}")
                print(f"  Notes: {record[5] or 'N/A'}")
                print()

        # Query 3: Get business impact summary
        print("\n3. Business impact summary:")
        impact_query = text("""
            SELECT
                COUNT(DISTINCT p.event_id) as affected_events,
                COUNT(DISTINCT p.musician_id) as affected_musicians,
                SUM(p.amount) as total_orphaned_amount
            FROM musician_event_payments p
            LEFT JOIN event_musicians em ON p.event_id = em.event_id AND p.musician_id = em.musician_id
            WHERE em.id IS NULL;
        """)

        impact_result = conn.execute(impact_query).fetchone()
        affected_events = 0
        affected_musicians = 0
        total_amount = 0

        if impact_result:
            affected_events = impact_result[0] or 0
            affected_musicians = impact_result[1] or 0
            total_amount = impact_result[2] or 0

            print(f"   Affected Events: {affected_events}")
            print(f"   Affected Musicians: {affected_musicians}")
            print(f"   Total Orphaned Amount: ${total_amount:.2f}")

        # Query 4: Check if event_musicians table exists and has data
        print("\n4. Reference table status:")
        em_count_query = text("SELECT COUNT(*) FROM event_musicians;")
        em_result = conn.execute(em_count_query).fetchone()
        em_count = em_result[0] if em_result else 0
        print(f"   Total event-musician assignments: {em_count}")

        payments_count_query = text("SELECT COUNT(*) FROM musician_event_payments;")
        payments_result = conn.execute(payments_count_query).fetchone()
        payments_count = payments_result[0] if payments_result else 0
        print(f"   Total musician payment records: {payments_count}")

    print("\n" + "=" * 50)
    print("AUDIT COMPLETE")
    print("=" * 50)

    return {
        'orphaned_count': orphaned_count,
        'affected_events': affected_events if 'affected_events' in locals() else 0,
        'affected_musicians': affected_musicians if 'affected_musicians' in locals() else 0,
        'total_orphaned_amount': total_amount if 'total_amount' in locals() else 0,
        'total_assignments': em_count,
        'total_payments': payments_count
    }


def main():
    """Main entry point."""
    try:
        results = audit_orphaned_payments()

        # Summary output
        print("\nSUMMARY:")
        print(f"Orphaned payments: {results['orphaned_count']}")
        print(f"Affected events: {results['affected_events']}")
        print(f"Affected musicians: {results['affected_musicians']}")
        print(f"Total orphaned amount: ${results['total_orphaned_amount']:.2f}")
        print(f"Total assignments: {results['total_assignments']}")
        print(f"Total payments: {results['total_payments']}")

        if results['orphaned_count'] > 0:
            print("\nACTION REQUIRED: Orphaned records found!")
            print("   Proceed to Phase 3: Data Cleanup before adding constraint.")
        else:
            print("\nGOOD NEWS: No orphaned records found!")
            print("   Proceed to Phase 2: Migration Creation.")

    except Exception as e:
        print(f"Error during audit: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()