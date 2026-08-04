"""
Database backup upload script for Supabase storage.

Uploads backup SQL files to a Supabase storage bucket for backup and disaster recovery.

Usage:
    python scripts/upload_backup_to_supabase.py --file backup.sql
    python scripts/upload_backup_to_supabase.py --auto-backup  # Creates and uploads backup
    python scripts/upload_backup_to_supabase.py --list         # List existing backups
    python scripts/upload_backup_to_supabase.py --delete FILENAME  # Delete a file from bucket
    python scripts/upload_backup_to_supabase.py --clean       # Delete all files in bucket
"""

import os
import sys
import argparse
from datetime import datetime
from dotenv import load_dotenv

import httpx


def get_storage_credentials():
    """Get Supabase storage credentials from environment."""
    load_dotenv()
    
    supabase_url = os.getenv('SUPABASE_URL')
    supabase_key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')
    bucket = os.getenv('SUPABASE_BUCKET', 'database-backups')
    
    if not supabase_url or not supabase_key:
        print("Error: SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY must be set in environment.")
        sys.exit(1)
    
    return supabase_url.rstrip('/'), supabase_key, bucket


def delete_file(remote_path: str) -> bool:
    """
    Delete a file from the Supabase bucket.
    
    Args:
        remote_path: Path to file in bucket
    
    Returns:
        True if deleted successfully
    """
    supabase_url, supabase_key, bucket = get_storage_credentials()
    
    storage_url = f"{supabase_url}/storage/v1/object/{bucket}/{remote_path}"
    
    headers = {
        'apikey': supabase_key,
        'Authorization': f'Bearer {supabase_key}',
    }
    
    try:
        with httpx.Client() as client:
            response = client.delete(storage_url, headers=headers)
            
            if response.status_code in [200, 204]:
                print(f"Deleted: {remote_path}")
                return True
            else:
                print(f"Delete error (HTTP {response.status_code}): {response.text}")
                return False
                    
    except Exception as e:
        print(f"Error during delete: {e}")
        return False


def clean_bucket() -> bool:
    """Delete all files in the Supabase bucket."""
    supabase_url, supabase_key, bucket = get_storage_credentials()
    
    print(f"Listing files to delete from bucket '{bucket}':")
    
    storage_url = f"{supabase_url}/storage/v1/object/{bucket}"
    
    headers = {
        'apikey': supabase_key,
        'Authorization': f'Bearer {supabase_key}',
    }
    
    try:
        with httpx.Client() as client:
            response = client.get(storage_url, headers=headers)
            
            if response.status_code not in [200, 201]:
                print(f"Error listing files (HTTP {response.status_code}): {response.text}")
                return False
            
            files = response.json()
            
            if not files:
                print("Bucket is already empty.")
                return True
            
            for file in files:
                name = file.get('name', 'unknown')
                delete_file(name)
            
            print(f"Cleaned {len(files)} file(s) from bucket.")
            return True
                    
    except Exception as e:
        print(f"Error cleaning bucket: {e}")
        return False


def upload_backup(local_path: str, remote_path: str = None, replace: bool = False) -> bool:
    """
    Upload a local backup file to Supabase storage using HTTP API.
    
    Args:
        local_path: Path to local backup file
        remote_path: Optional remote path in bucket (defaults to filename)
        replace: If True, delete existing file before upload
    
    Returns:
        True if upload successful
    """
    if not os.path.exists(local_path):
        print(f"Error: Backup file not found: {local_path}")
        return False
    
    supabase_url, supabase_key, bucket = get_storage_credentials()
    
    if remote_path is None:
        remote_path = os.path.basename(local_path)
    
    print(f"Uploading {local_path} to bucket '{bucket}' as {remote_path}...")
    
    storage_url = f"{supabase_url}/storage/v1/object/{bucket}/{remote_path}"
    
    headers = {
        'apikey': supabase_key,
        'Authorization': f'Bearer {supabase_key}',
    }
    
    try:
        with open(local_path, 'rb') as f:
            file_content = f.read()
        
        with httpx.Client() as client:
            response = client.put(storage_url, headers=headers, content=file_content)
            
            if response.status_code in [200, 201]:
                public_url = f"{supabase_url}/storage/v1/object/public/{bucket}/{remote_path}"
                print(f"Upload completed successfully!")    
                print(f"Public URL: {public_url}")
                return True
            elif response.status_code == 409:
                if replace:
                    print("File exists, deleting and retrying...")
                    delete_file(remote_path)
                    response = client.put(storage_url, headers=headers, content=file_content)
                    if response.status_code in [200, 201]:
                        public_url = f"{supabase_url}/storage/v1/object/public/{bucket}/{remote_path}"
                        print(f"Upload completed successfully!")
                        print(f"Public URL: {public_url}")
                        return True
                print(f"File already exists. Use -r to specify a different path, --replace, or delete existing file.")
                return False
            else:
                print(f"Upload error (HTTP {response.status_code}): {response.text}")
                return False
                    
    except Exception as e:
        print(f"Error during upload: {e}")
        return False


def list_backups() -> bool:
    """List all backup files in the Supabase bucket."""
    supabase_url, supabase_key, bucket = get_storage_credentials()
    
    print(f"Listing backups in bucket '{bucket}':")
    
    storage_url = f"{supabase_url}/storage/v1/object/{bucket}"
    
    headers = {
        'apikey': supabase_key,
        'Authorization': f'Bearer {supabase_key}',
    }
    
    try:
        with httpx.Client() as client:
            response = client.get(storage_url, headers=headers)
            
            if response.status_code in [200, 201]:
                files = response.json()
                
                if not files:
                    print("No backups found in bucket.")
                    return True
                
                for file in files:
                    name = file.get('name', 'unknown')
                    created_at = file.get('metadata', {}).get('created_at', 'unknown')
                    size = file.get('metadata', {}).get('size', 0)
                    print(f"  - {name} ({size} bytes, {created_at})")
                
                return True
            else:
                print(f"Error listing backups (HTTP {response.status_code}): {response.text}")
                return False
                    
    except Exception as e:
        print(f"Error listing backups: {e}")
        return False


def auto_backup_and_upload(replace: bool = False) -> bool:
    """Create a new backup and upload it to Supabase."""
    from scripts.backup_data import backup_data
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_file = f'backup_data_{timestamp}.sql'
    
    print("Creating backup...")
    created_file = backup_data(backup_file)
    
    if not created_file or not os.path.exists(created_file):
        print("Failed to create backup.")
        return False
    
    print(f"Backup created: {created_file}")
    
    success = upload_backup(created_file, replace=replace)
    
    if success:
        print(f"Backup uploaded successfully: {created_file}")
    else:
        print(f"Failed to upload backup: {created_file}")
    
    return success


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Upload database backup to Supabase storage'
    )
    
    parser.add_argument('--file', '-f', help='Path to local backup file to upload')
    parser.add_argument('--auto-backup', '-a', action='store_true',
                        help='Create new backup and upload to Supabase')
    parser.add_argument('--list', '-l', action='store_true',
                        help='List existing backups in bucket')
    parser.add_argument('--delete', '-d', metavar='FILENAME',
                        help='Delete a file from the bucket')
    parser.add_argument('--clean', '-c', action='store_true',
                        help='Delete all files in the bucket')
    parser.add_argument('--remote-path', '-r', help='Remote path in Supabase bucket (default: filename)')
    parser.add_argument('--replace', action='store_true',
                        help='Replace existing file if it exists')
    
    args = parser.parse_args()
    
    if not any([args.file, args.auto_backup, args.list, args.delete, args.clean]):
        parser.print_help()
        sys.exit(1)
    
    success = True
    
    if args.clean:
        print("Cleaning bucket...")
        success = clean_bucket()
        if not success:
            sys.exit(1)
    
    if success and (args.delete or args.file or args.auto_backup):
        if args.delete:
            success = delete_file(args.delete)
        elif args.auto_backup:
            success = auto_backup_and_upload(replace=args.replace)
        elif args.file:
            success = upload_backup(args.file, args.remote_path, replace=args.replace)
    
    if success and args.list:
        success = list_backups()
    
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()