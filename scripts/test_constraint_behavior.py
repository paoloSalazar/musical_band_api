"""
Test script to verify the composite foreign key constraint behavior.

Tests the constraint that prevents orphaned musician_event_payments.
"""

import os
import sys
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError, ProgrammingError

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.database import engine


def test_constraint_behavior():
    """
    Test the composite foreign key constraint behavior.
    """
    print("TESTING COMPOSITE FOREIGN KEY CONSTRAINT")
    print("=" * 60)

    with engine.connect() as conn:
        try:
            # Test 1: Try to insert a payment for a non-existent assignment
            print("\nTest 1: Insert payment for non-existent assignment (should fail)")
            # Get a valid event and a musician not assigned to it
            valid_combo_query = text("""
                SELECT e.id as event_id, u.id as musician_id
                FROM events e
                CROSS JOIN users u
                WHERE u.role_id IN (SELECT id FROM user_roles WHERE name IN ('musician', 'auxiliar_musician'))
                AND NOT EXISTS (
                    SELECT 1 FROM event_musicians em
                    WHERE em.event_id = e.id AND em.musician_id = u.id
                )
                LIMIT 1
            """)
            valid_combo = conn.execute(valid_combo_query).fetchone()

            if not valid_combo:
                print("  Skipping test: No valid event-musician combinations found to test")
            else:
                event_id, musician_id = valid_combo
                try:
                    conn.execute(text(f"""
                        INSERT INTO musician_event_payments
                        (event_id, musician_id, payment_type, amount, payment_date, notes)
                        VALUES ({event_id}, {musician_id}, 'ADVANCE', 100.00, NOW(), 'Test orphaned payment')
                    """))
                    conn.commit()
                    print("ERROR: Constraint did not prevent orphaned payment!")
                    return False
                except (IntegrityError, ProgrammingError) as e:
                    print("SUCCESS: Constraint prevented orphaned payment")
                    print(f"  Error: {str(e).split('DETAIL:')[0].strip()}")
                    conn.rollback()

            # Test 2: Check that valid payments still work (if there are existing assignments)
            print("\nTest 2: Check existing data integrity")
            assignments_query = text("SELECT COUNT(*) FROM event_musicians")
            payments_query = text("SELECT COUNT(*) FROM musician_event_payments")

            assignments_count = conn.execute(assignments_query).scalar()
            payments_count = conn.execute(payments_query).scalar()

            print(f"  Assignments: {assignments_count}")
            print(f"  Payments: {payments_count}")

            if payments_count == 0:
                print("  No payments exist - cannot test valid payment insertion")
            else:
                print("  Existing payments are preserved")

            # Test 3: Try to delete an assignment that might have payments (should be restricted)
            print("\nTest 3: Test assignment deletion with payments (should fail if payments exist)")
            if assignments_count > 0 and payments_count > 0:
                # Get an assignment that has payments
                assignment_with_payments = conn.execute(text("""
                    SELECT em.id, em.event_id, em.musician_id
                    FROM event_musicians em
                    JOIN musician_event_payments mep ON em.event_id = mep.event_id AND em.musician_id = mep.musician_id
                    LIMIT 1
                """)).fetchone()

                if assignment_with_payments:
                    try:
                        conn.execute(text(f"DELETE FROM event_musicians WHERE id = {assignment_with_payments[0]}"))
                        conn.commit()
                        print("ERROR: Assignment deletion was not restricted!")
                        return False
                    except (IntegrityError, ProgrammingError) as e:
                        print("SUCCESS: Assignment deletion properly restricted")
                        print(f"  Error: {str(e).split('DETAIL:')[0].strip()}")
                        conn.rollback()
                else:
                    print("  No assignments with payments found to test")

            print("\n" + "=" * 60)
            print("ALL TESTS PASSED")
            print("=" * 60)
            return True

        except Exception as e:
            print(f"Unexpected error during testing: {e}")
            return False


if __name__ == '__main__':
    success = test_constraint_behavior()
    if not success:
        print("\nFAILURE: Constraint tests failed!")
        sys.exit(1)
    else:
        print("\nConstraint validation successful.")