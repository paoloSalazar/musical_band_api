"""
Database restore script.

Restores data from a backup SQL file to the database.
The backup file should contain INSERT statements (created by backup_data.py).

Usage:
    python scripts/restore_data.py backup_data.sql
"""

import os
import sys
import subprocess
from dotenv import load_dotenv

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.database import DATABASE_URL_SQLALCHEMY


def parse_database_url(url: str) -> dict:
    """Parse SQLAlchemy database URL into components."""
    # Expected format: postgresql+pg8000://user:password@host:port/database
    # or postgresql://user:password@host:port/database
    
    # Remove the driver part
    if '+' in url:
        url = url.replace('+pg8000', '').replace('+psycopg2', '')
    
    # Remove postgresql:// prefix
    if url.startswith('postgresql://'):
        url = url[len('postgresql://'):]
    
    # Split into user:password@host:port/database
    auth, host_db = url.split('@')
    user, password = auth.split(':')
    
    # Split host:port/database
    if '/' in host_db:
        host_port, database = host_db.rsplit('/', 1)
        if ':' in host_port:
            host, port = host_port.split(':')
        else:
            host = host_port
            port = '5432'
    else:
        host = host_db
        port = '5432'
        database = ''
    
    return {
        'user': user,
        'password': password,
        'host': host,
        'port': port,
        'database': database
    }


def restore_data(backup_file: str) -> None:
    """
    Restore data from a backup SQL file.
    
    Args:
        backup_file: Path to the backup SQL file.
    """
    load_dotenv()
    
    # Check if backup file exists
    if not os.path.exists(backup_file):
        print(f"Error: Backup file not found: {backup_file}")
        sys.exit(1)
    
    # Parse database URL
    db_config = parse_database_url(DATABASE_URL_SQLALCHEMY)
    
    # Set environment variable for password
    env = os.environ.copy()
    env['PGPASSWORD'] = db_config['password']
    
    print(f"Restoring data to database '{db_config['database']}'...")
    print(f"From file: {backup_file}")
    
    # Build psql command to restore data
    cmd = [
        'psql',
        '-U', db_config['user'],
        '-h', db_config['host'],
        '-p', db_config['port'],
        '-d', db_config['database'],
        '-f', backup_file,
        '-v', 'ON_ERROR_STOP=0'  # Continue on errors
    ]
    
    try:
        result = subprocess.run(cmd, env=env, capture_output=True, text=True)
        
        if result.returncode != 0:
            print(f"Warning: Some errors occurred during restore:")
            print(result.stderr)
        
        print(f"\nRestore completed!")
        
        # Show summary
        if result.stdout:
            lines = result.stdout.strip().split('\n')
            insert_count = sum(1 for line in lines if 'INSERT' in line.upper())
            print(f"Processed approximately {insert_count} INSERT statements.")
        
    except FileNotFoundError:
        print("Error: psql not found. Please install PostgreSQL client tools.")
        sys.exit(1)


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Restore database data from backup')
    parser.add_argument('backup_file', help='Path to backup SQL file')
    
    args = parser.parse_args()
    
    restore_data(args.backup_file)


if __name__ == '__main__':
    main()
