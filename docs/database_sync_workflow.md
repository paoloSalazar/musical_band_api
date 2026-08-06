# Database Sync Workflow

This document describes the workflow for syncing databases between machines when working on the Musical Band API project.

## Overview

When you work on different machines, the migration files may get out of sync with the local database. This workflow helps you:

1. **Backup data** from the current machine
2. **Clear and recreate** the database schema using migrations
3. **Restore data** from the backup

## Prerequisites

Ensure you have:
- PostgreSQL client tools installed (`pg_dump`, `psql`)
- Python environment with dependencies installed
- Access to the database

## Workflow Steps

### Step 1: Backup Data (on source machine)

Before switching machines, create a data backup:

```bash
# Using the provided script
python scripts/backup_data.py

# Or manually using pg_dump (data only, no schema)
pg_dump -U <username> -d musical_band_db --data-only --inserts > backup_data.sql
```

The backup file will contain INSERT statements for all your data.

### Step 2: Sync Migration Files

Ensure all migration files are synced between machines:
- Use git to pull the latest migration files
- Or manually copy the `alembic/versions/` directory

### Step 3: Clear Database (on target machine)

Clear all tables and reset the database:

```bash
python scripts/clear_database.py
```

This will:
- Drop all tables with CASCADE
- Drop custom enum types
- Clear the alembic version table

### Step 4: Run Migrations

Recreate the database schema using migrations:

```bash
python -m alembic upgrade head
```

### Step 5: Restore Data

Restore the data from the backup:

```bash
# Using the provided script
python scripts/restore_data.py

# Or manually using psql
psql -U <username> -d musical_band_db -f backup_data.sql
```

## Quick Reference Commands

| Task | Command |
|------|---------|
| Check current migration | `python -m alembic current` |
| View migration history | `python -m alembic history` |
| Create backup | `python scripts/backup_data.py` |
| Clear database | `python scripts/clear_database.py` |
| Run migrations | `python -m alembic upgrade head` |
| Restore data | `python scripts/restore_data.py` |

## Troubleshooting

### Foreign Key Constraint Errors

If you get foreign key errors during restore, the data must be restored in the correct order:
1. `user_roles` (no dependencies)
2. `users` (depends on user_roles)
3. `permissions` (no dependencies)
4. `role_permissions` (depends on user_roles, permissions)
5. `events` (no dependencies)

### Enum Type Errors

If you get errors about enum types not existing, ensure migrations ran successfully before restoring data.

### Revision Not Found

If alembic reports "Can't locate revision", it means the database has a migration version that doesn't exist in your local files. Sync the migration files first, then clear and recreate the database.
