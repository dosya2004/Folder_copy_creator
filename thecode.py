import sys
import os
import shutil
import time
import logging
import hashlib
from pathlib import Path


def setup_logging(log_file: str):
    """Configure logging to file and console"""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s:%(levelname)s:%(message)s",
        handlers=[
            logging.FileHandler(log_file, mode="a"),
            logging.StreamHandler()
        ]
    )


def log_message(message: str, level: str = "info"):
    #Log a message with specified level
    if level == "info":
        logging.info(message)
    elif level == "warning":
        logging.warning(message)
    elif level == "error":
        logging.error(message)


def get_first_file_hash(source_path: str) -> str | None:
    
    #Calculate MD5 hash of the first encountered file in the source folder.
    #Returns None if no files are found.
    
    source_path_obj = Path(source_path)
    for file in source_path_obj.rglob("*"):
        if file.is_file():
            hash_md5 = hashlib.md5()
            with file.open("rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_md5.update(chunk)
            return hash_md5.hexdigest()
    return None


def remove_extra_files(source_path: str, replica_path: str):
    #Remove files/folders from replica that don't exist in source
    source_path_obj = Path(source_path)
    replica_path_obj = Path(replica_path)

    # Remove extra files
    for item in replica_path_obj.rglob("*"):
        relative_path = item.relative_to(replica_path_obj)
        source_item = source_path_obj / relative_path
        if not source_item.exists():
            if item.is_file():
                log_message(f"Removing extra file: {relative_path}")
                item.unlink()
            elif item.is_dir():
                try:
                    item.rmdir()
                    log_message(f"Removed empty directory: {relative_path}")
                except OSError:
                    pass  # Directory not empty


def copy_files(source_path: str, replica_path: str):
    #Copy/update files from source to replica
    source_path_obj = Path(source_path)
    replica_path_obj = Path(replica_path)

    for source_item in source_path_obj.rglob("*"):
        relative_path = source_item.relative_to(source_path_obj)
        replica_item = replica_path_obj / relative_path

        if source_item.is_dir():
            replica_item.mkdir(parents=True, exist_ok=True)
        else:
            needs_copy = True
            if replica_item.exists():
                source_mtime = source_item.stat().st_mtime
                replica_mtime = replica_item.stat().st_mtime
                source_size = source_item.stat().st_size
                replica_size = replica_item.stat().st_size
                if abs(source_mtime - replica_mtime) < 1 and source_size == replica_size:
                    needs_copy = False
            if needs_copy:
                log_message(f"Copying file: {relative_path}")
                shutil.copy2(source_item, replica_item)


def sync_folders(source_path: str, replica_path: str, interval: int, max_syncs: int):
    #Synchronize source folder to replica folder periodically
    sync_count = 0

    while sync_count < max_syncs:
        log_message(f"Starting synchronization #{sync_count + 1}")

        Path(source_path).mkdir(parents=True, exist_ok=True)
        Path(replica_path).mkdir(parents=True, exist_ok=True)

        remove_extra_files(source_path, replica_path)
        copy_files(source_path, replica_path)

        log_message(f"Synchronization #{sync_count + 1} completed successfully")

        sync_count += 1
        if sync_count >= max_syncs:
            log_message(f"Completed {max_syncs} synchronizations. Stopping.")
            break

        log_message(f"Next synchronization in {interval} seconds...")
        time.sleep(interval)


def main():
    
    
    #Entry point for the script.
    #Expected arguments (in strict order):
    #1) path to source folder
    #2) path to replica folder
    #3) interval between synchronizations (int)
    #4) amount of synchronizations (int)
    #5) path to log file
    
    if len(sys.argv) != 6:
        print("Usage: python sync.py <source> <replica> <interval> <count> <log_file>")
        return

    source = sys.argv[1]
    replica = sys.argv[2]
    try:
        interval = int(sys.argv[3])
        max_syncs = int(sys.argv[4])
    except ValueError:
        print("Interval and count must be integers")
        return
    log_file = sys.argv[5]

    setup_logging(log_file)

    log_message("Starting folder synchronization")
    log_message(f"Source: {source}")
    log_message(f"Replica: {replica}")
    log_message(f"Interval: {interval} seconds")
    log_message(f"Synchronizations to perform: {max_syncs}")

    # Calculate and log hash of first file
    file_hash = get_first_file_hash(source)
    if file_hash:
        log_message(f"MD5 of first file in source: {file_hash}")
    else:
        log_message("No files found in source to hash")

    try:
        sync_folders(source, replica, interval, max_syncs)
    except KeyboardInterrupt:
        log_message("Synchronization stopped by user")
    except Exception as e:
        log_message(f"Fatal error: {str(e)}", "error")


if __name__ == "__main__":
    main()
