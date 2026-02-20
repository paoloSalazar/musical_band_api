"""
Complete database sync script.

Performs the full database sync workflow:
1. Clear all database tables
2. Run migrations to recreate schema
3. Restore data from a backup file

Usage:
    python scripts/sync_database.py backup_data.sql [--force]
"""

import os
import sys
import subprocess

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def run_command(cmd: list, cwd: str = None) -> bool:
    """
    Run a command and return True if successful.
    
    Args:
        cmd: Command and arguments as a list.
        cwd: Working directory.
    
    Returns:
        True if command succeeded, False otherwise.
    """
    try:
        result = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
        
        if result.returncode != 0:
            print(f"Error: {result.stderr}")
            return False
        
        if result.stdout:
            print(result.stdout)
        
        return True
        
    except Exception as e:
        print(f"Error running command: {e}")
        return False


def sync_database(backup_file: str, force: bool = False) -> None:
    """
    Perform complete database sync.
    
    Args:
        backup_file: Path to the backup SQL file.
        force: If True, skip confirmation prompt.
    """
    # Get the project root directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    
    # Check if backup file exists
    if not os.path.exists(backup_file):
        print(f"Error: Backup file not found: {backup_file}")
        sys.exit(1)
    
    if not force:
        print("=" * 60)
        print("DATABASE SYNC WORKFLOW")
        print("=" * 60)
        print("\nThis will:")
        print("  1. Clear all database tables (DELETE ALL DATA)")
        print("  2. Run migrations to recreate schema")
        print(f"  3. Restore data from: {backup_file}")
        print("\nWARNING: All existing data will be lost!")
        response = input("\nContinue? (yes/no): ")
        if response.lower() != 'yes':
            print("Aborted.")
            return
    
    print("\n" + "=" * 60)
    print("STEP 1: Clearing database...")
    print("=" * 60)
    
    clear_cmd = [sys.executable, os.path.join(script_dir, 'clear_database.py'), '--force']
    if not run_command(clear_cmd):
        print("Failed to clear database!")
        sys.exit(1)
    
    print("\n" + "=" * 60)
    print("STEP 2: Running migrations...")
    print("=" * 60)
    
    migrate_cmd = [sys.executable, '-m', 'alembic', 'upgrade', 'head']
    if not run_command(migrate_cmd, cwd=project_root):
        print("Failed to run migrations!")
        sys.exit(1)
    
    print("\n" + "=" * 60)
    print("STEP 3: Restoring data...")
    print("=" * 60)
    
    restore_cmd = [sys.executable, os.path.join(script_dir, 'restore_data.py'), backup_file]
    if not run_command(restore_cmd):
        print("Failed to restore data!")
        sys.exit(1)
    
    print("\n" + "=" * 60)
    print("DATABASE SYNC COMPLETED SUCCESSFULLY!")
    print("=" * 60)


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Sync database: clear, migrate, and restore'
    )
    parser.add_argument('backup_file', help='Path to backup SQL file')
    parser.add_argument('--force', '-f', action='store_true',
                        help='Skip confirmation prompt')
    
    args = parser.parse_args()
    
    sync_database(args.backup_file, args.force)


if __name__ == '__main__':
    main()
