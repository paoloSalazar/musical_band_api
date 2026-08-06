"""
Database backup script.

Creates a data-only backup of all tables in the database.
The backup file contains INSERT statements that can be used to restore data.

Usage:
    python scripts/backup_data.py [--output backup_data.sql]
"""

import os
import sys
import subprocess
from datetime import datetime
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


def backup_data(output_file: str = None) -> str:
    """
    Create a data-only backup of the database.
    
    Args:
        output_file: Path to output file. If None, generates a timestamped filename.
    
    Returns:
        Path to the backup file.
    """
    load_dotenv()
    
    # Generate output filename if not provided
    if output_file is None:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_file = f'backup_data_{timestamp}.sql'
    
    # Parse database URL
    db_config = parse_database_url(DATABASE_URL_SQLALCHEMY)
    
    # Set environment variable for password
    env = os.environ.copy()
    env['PGPASSWORD'] = db_config['password']
    
    # Build pg_dump command for data-only backup
    cmd = [
        'pg_dump',
        '-U', db_config['user'],
        '-h', db_config['host'],
        '-p', db_config['port'],
        '-d', db_config['database'],
        '--data-only',
        '--inserts',
        '--column-inserts',
        '-f', output_file
    ]
    
    print(f"Creating backup of database '{db_config['database']}'...")
    print(f"Output file: {output_file}")
    
    try:
        result = subprocess.run(cmd, env=env, capture_output=True, text=True)
        
        if result.returncode != 0:
            print(f"Error during backup: {result.stderr}")
            sys.exit(1)
        
        print(f"Backup completed successfully!")
        print(f"File: {os.path.abspath(output_file)}")
        
        return output_file
        
    except FileNotFoundError:
        print("Error: pg_dump not found. Please install PostgreSQL client tools.")
        sys.exit(1)


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Backup database data')
    parser.add_argument('--output', '-o', help='Output file path', default=None)
    
    args = parser.parse_args()
    
    backup_data(args.output)


if __name__ == '__main__':
    main()
