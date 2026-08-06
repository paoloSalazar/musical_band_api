# Supabase Backup Upload Plan

## Overview
Create a script to upload database backup files to a Supabase bucket for automated backups and disaster recovery.

## Current State
- `scripts/backup_data.py` creates PostgreSQL dumps with INSERT statements
- Backups stored locally with timestamp format: `backup_data_YYYYMMDD_HHMMSS.sql`
- No automated backup upload mechanism

## Implementation Plan

### 1. Add Supabase Configuration
**File: `.env` (or `.env.docker`)**
```env
# Supabase Configuration
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key
SUPABASE_BUCKET=database-backups
```

### 2. Create Upload Script
**File: `scripts/upload_backup_to_supabase.py`**

Key dependencies:
- `supabase-py` - Supabase Python SDK
- Existing `backup_data.py` for backup creation

### 3. Script Logic
```bash
# Usage
python scripts/upload_backup_to_supabase.py [--file backup.sql]
python scripts/upload_backup_to_supabase.py --auto-backup  # Creates backup then uploads
```

### 4. File Structure
```
scripts/
├── backup_data.py              # existing - creates backup
├── upload_backup_to_supabase.py # new - uploads to Supabase
└── sync_database.py            # existing - imports backup
```

### 5. Environment Variables Required
```env
SUPABASE_URL=https://...
SUPABASE_SERVICE_ROLE_KEY=...
SUPABASE_BUCKET=database-backups
```

### 6. Implementation Steps

1. Install Supabase SDK: `pip install supabase`
2. Create `scripts/upload_backup_to_supabase.py`
3. Add Supabase config to environment files
4. Test upload functionality
5. Update docker-compose with Supabase secrets

### 7. Supabase Setup Required
- Create Supabase project
- Get Service Role Key (with `service_role` level)
- Create bucket: `database-backups`
- Configure bucket permissions

### 8. Script Features
- Upload with date-stamped filename
- Optional: automatic backup creation before upload
- Progress reporting
- Error handling
- Retention policy support (optional)

### 9. Security Considerations
- Service role key is sensitive - use env vars, never commit
- Consider using scheduled deployments for automated backups
- Bucket should have restricted access

### 10. Usage Examples
```bash
# Upload existing backup
python scripts/upload_backup_to_supabase.py --file scripts/backup_data_20260629_InitialState.sql

# Create backup and upload
python scripts/upload_backup_to_supabase.py --auto-backup

# List existing backups
python scripts/upload_backup_to_supabase.py --list
```

### 11. Docker Integration
Add to `build/docker-compose.yml`:
```yaml
services:
  backup-cron:
    image: python:3.11-slim
    env_file:
      - .env
    volumes:
      - ./scripts:/app/scripts
    command: ["python", "scripts/upload_backup_to_supabase.py", "--auto-backup"]
    networks:
      - musical_band_network
```

Or use cron in a separate container for scheduled backups.

## Files to Create
1. `scripts/upload_backup_to_supabase.py` - Main upload script
2. Update `.env` with Supabase credentials (not committed)