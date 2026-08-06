"""
Database utility scripts for the Musical Band API.

This package contains scripts for managing database backups and migrations:

- backup_data.py: Create data-only backups
- clear_database.py: Drop all tables and reset database
- restore_data.py: Restore data from backup
- sync_database.py: Complete workflow (clear + migrate + restore)

Usage:
    # Create a backup
    python scripts/backup_data.py

    # Clear database
    python scripts/clear_database.py

    # Run migrations
    python -m alembic upgrade head

    # Restore data
    python scripts/restore_data.py backup_data.sql

    # Or do everything in one command
    python scripts/sync_database.py backup_data.sql
"""
