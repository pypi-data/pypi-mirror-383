"""Core cleanup functionality with all safety features."""

import os
import shutil
import csv
import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Any, Tuple, Optional

from .config import Config
from .utils import (
    ProgressBar,
    confirm_deletion,
    bytes_to_human_readable,
    check_size_threshold,
    is_path_excluded,
    create_deletion_manifest,
    validate_path_safety,
    normalize_path,
    is_protected_path
)
from .notifications import notify_completion, notify_error, notify_dry_run_complete


class CleanupEngine:
    """Main cleanup engine with safety features."""
    
    def __init__(self, config: Config, dry_run: bool = False, archive_mode: bool = False):
        """Initialize cleanup engine.
        
        Args:
            config: Configuration object
            dry_run: If True, only preview without deleting
            archive_mode: If True, move to archive instead of deleting
        """
        self.config = config
        self.dry_run = dry_run or config.get("safety", {}).get("dry_run", False)
        self.archive_mode = archive_mode or config.get("safety", {}).get("backup_mode", False)
        self.deleted_items: List[Dict[str, Any]] = []
        self.stats = {
            "folders_deleted": 0,
            "folders_size": 0,
            "bin_deleted": 0,
            "bin_size": 0,
            "errors": []
        }
    
    def get_size(self, path: str) -> int:
        """Calculate total size of a file or folder in bytes."""
        total_size = 0
        try:
            if os.path.isfile(path):
                total_size = os.path.getsize(path)
            elif os.path.isdir(path):
                for dirpath, dirnames, filenames in os.walk(path):
                    for filename in filenames:
                        filepath = os.path.join(dirpath, filename)
                        if os.path.exists(filepath):
                            try:
                                total_size += os.path.getsize(filepath)
                            except:
                                pass  # Skip files we can't access
        except Exception as e:
            print(f"Error calculating size for {path}: {e}")
        return total_size
    
    def get_last_modified_time(self, folder_path: str) -> datetime:
        """Get the most recent modification time in a folder."""
        try:
            latest_time = os.path.getmtime(folder_path)
            
            for root, dirs, files in os.walk(folder_path):
                for item in dirs + files:
                    item_path = os.path.join(root, item)
                    if os.path.exists(item_path):
                        try:
                            item_time = os.path.getmtime(item_path)
                            latest_time = max(latest_time, item_time)
                        except:
                            pass  # Skip items we can't access
            
            return datetime.fromtimestamp(latest_time)
        except Exception as e:
            return datetime.now()
    
    def scan_for_targets(self, main_folder: str, target_name: str, days_threshold: int) -> List[Dict[str, Any]]:
        """Scan for target folders that meet deletion criteria.
        
        Returns:
            List of dictionaries with path, size, last_modified info
        """
        cutoff_date = datetime.now() - timedelta(days=days_threshold)
        candidates = []
        exclusions = self.config.get("exclusions", [])
        
        print(f"\n🔍 Scanning {main_folder} for '{target_name}' folders...")
        
        # First pass: count directories for progress bar
        total_dirs = sum(1 for _, dirs, _ in os.walk(main_folder) if target_name in dirs)
        
        if total_dirs == 0:
            print(f"No '{target_name}' folders found.")
            return candidates
        
        progress = ProgressBar(total_dirs, prefix=f"Scanning '{target_name}'", width=40)
        
        for root, dirs, files in os.walk(main_folder):
            if target_name in dirs:
                target_path = os.path.join(root, target_name)
                
                # Safety checks
                if is_protected_path(target_path):
                    progress.update(suffix="(skipped - protected)")
                    continue
                
                if is_path_excluded(target_path, exclusions):
                    progress.update(suffix="(skipped - excluded)")
                    continue
                
                # Check modification time of parent folder
                parent_path = os.path.dirname(target_path)
                last_modified = self.get_last_modified_time(parent_path)
                
                if last_modified < cutoff_date:
                    folder_size = self.get_size(target_path)
                    candidates.append({
                        "path": target_path,
                        "size": folder_size,
                        "last_modified": last_modified.isoformat(),
                        "type": "folder",
                        "target_name": target_name
                    })
                    progress.update(suffix=f"({bytes_to_human_readable(folder_size)})")
                else:
                    progress.update(suffix="(too recent)")
        
        progress.finish()
        print(f"✓ Found {len(candidates)} '{target_name}' folders eligible for cleanup")
        
        return candidates
    
    def delete_or_archive_item(self, item: Dict[str, Any]) -> bool:
        """Delete or archive a single item.
        
        Returns:
            True if successful, False otherwise
        """
        path = item["path"]
        
        # Validate safety
        is_safe, error_msg = validate_path_safety(path)
        if not is_safe:
            print(f"⚠️  Skipped unsafe path: {error_msg}")
            self.stats["errors"].append(error_msg)
            return False
        
        try:
            if self.archive_mode:
                # Move to archive folder
                archive_folder = self.config.get("safety", {}).get("archive_folder")
                os.makedirs(archive_folder, exist_ok=True)
                
                # Create unique archive path
                rel_path = os.path.relpath(path, "/")
                archive_path = os.path.join(archive_folder, rel_path)
                os.makedirs(os.path.dirname(archive_path), exist_ok=True)
                
                shutil.move(path, archive_path)
                item["archived_to"] = archive_path
                print(f"📦 Archived: {path} → {archive_path}")
            else:
                # Permanently delete
                if os.path.isfile(path):
                    os.remove(path)
                elif os.path.isdir(path):
                    shutil.rmtree(path)
                print(f"🗑️  Deleted: {path} ({bytes_to_human_readable(item['size'])})")
            
            return True
        except Exception as e:
            error_msg = f"Failed to process {path}: {e}"
            print(f"❌ {error_msg}")
            self.stats["errors"].append(error_msg)
            return False
    
    def cleanup_targets(self) -> int:
        """Clean up all enabled target folders.
        
        Returns:
            Total size deleted in bytes
        """
        targets = self.config.get_enabled_targets()
        main_folder = self.config.get("main_folder")
        all_candidates = []
        
        # Scan for all targets
        for target in targets:
            candidates = self.scan_for_targets(
                main_folder,
                target["name"],
                target["days_threshold"]
            )
            all_candidates.extend(candidates)
        
        if not all_candidates:
            print("\n✓ No folders to clean up!")
            return 0
        
        # Calculate total size
        total_size = sum(item["size"] for item in all_candidates)
        
        # Check safety threshold
        safety_config = self.config.get("safety", {})
        exceeds_threshold, warning_msg = check_size_threshold(
            total_size,
            safety_config.get("size_threshold_mb", 5000)
        )
        
        if exceeds_threshold:
            print(f"\n{warning_msg}")
        
        # Show summary
        print(f"\n📊 Summary:")
        print(f"   Items to process: {len(all_candidates)}")
        print(f"   Total size: {bytes_to_human_readable(total_size)}")
        print(f"   Mode: {'DRY RUN' if self.dry_run else ('ARCHIVE' if self.archive_mode else 'DELETE')}")
        
        if self.dry_run:
            print(f"\n{'='*60}")
            print("DRY RUN - No actual deletions will be performed")
            print(f"{'='*60}")
            for item in all_candidates:
                print(f"  Would delete: {item['path']} ({bytes_to_human_readable(item['size'])})")
            
            if self.config.get("notifications", {}).get("enabled"):
                notify_dry_run_complete(len(all_candidates), total_size / (1024 * 1024))
            
            return 0
        
        # Ask for confirmation if above threshold
        confirmation_threshold = safety_config.get("require_confirmation_above_mb", 500)
        if total_size > confirmation_threshold * 1024 * 1024:
            if not confirm_deletion(
                f"\n⚠️  About to {'archive' if self.archive_mode else 'delete'} "
                f"{len(all_candidates)} items ({bytes_to_human_readable(total_size)}). Continue?",
                default=False
            ):
                print("❌ Operation cancelled by user.")
                return 0
        
        # Perform cleanup
        print(f"\n{'🚀 Starting cleanup...'}")
        progress = ProgressBar(len(all_candidates), prefix="Processing", width=40)
        
        successful = 0
        for item in all_candidates:
            if self.delete_or_archive_item(item):
                self.deleted_items.append(item)
                successful += 1
                self.stats["folders_deleted"] += 1
                self.stats["folders_size"] += item["size"]
            progress.update()
        
        progress.finish()
        
        print(f"\n✅ Cleanup complete!")
        print(f"   Successfully processed: {successful}/{len(all_candidates)}")
        if self.stats["errors"]:
            print(f"   Errors: {len(self.stats['errors'])}")
        
        return self.stats["folders_size"]
    
    def clean_bin_folder(self) -> int:
        """Clean the bin/trash folder.
        
        Returns:
            Total size deleted in bytes
        """
        bin_folder = self.config.get("bin_folder")
        
        if not os.path.exists(bin_folder):
            print(f"\n📁 Bin folder not found: {bin_folder}")
            print("Creating bin folder for future use...")
            try:
                os.makedirs(bin_folder, exist_ok=True)
                print(f"✓ Created: {bin_folder}")
            except Exception as e:
                print(f"❌ Could not create bin folder: {e}")
            return 0
        
        print(f"\n🗑️  Cleaning bin folder: {bin_folder}")
        
        try:
            items = os.listdir(bin_folder)
            if not items:
                print("✓ Bin folder is already empty")
                return 0
            
            # Calculate total size first
            total_size = 0
            for item in items:
                item_path = os.path.join(bin_folder, item)
                total_size += self.get_size(item_path)
            
            if self.dry_run:
                print(f"DRY RUN: Would delete {len(items)} items ({bytes_to_human_readable(total_size)})")
                return 0
            
            # Delete items
            progress = ProgressBar(len(items), prefix="Cleaning bin", width=40)
            
            for item in items:
                item_path = os.path.join(bin_folder, item)
                try:
                    item_size = self.get_size(item_path)
                    
                    if os.path.isfile(item_path):
                        os.remove(item_path)
                    elif os.path.isdir(item_path):
                        shutil.rmtree(item_path)
                    
                    self.stats["bin_deleted"] += 1
                    self.stats["bin_size"] += item_size
                    progress.update(suffix=f"({bytes_to_human_readable(item_size)})")
                except Exception as e:
                    error_msg = f"Failed to delete {item}: {e}"
                    self.stats["errors"].append(error_msg)
                    progress.update(suffix="(error)")
            
            progress.finish()
            print(f"✅ Bin cleanup complete: {self.stats['bin_deleted']} items, "
                  f"{bytes_to_human_readable(self.stats['bin_size'])}")
            
        except PermissionError:
            print("❌ Permission denied: Cannot access bin folder")
            print("Note: Some system trash folders have restricted access.")
            return 0
        except Exception as e:
            print(f"❌ Error accessing bin folder: {e}")
            return 0
        
        return self.stats["bin_size"]
    
    def save_deletion_manifest(self):
        """Save manifest of deleted items for potential undo."""
        if not self.deleted_items:
            return
        
        manifest_file = self.config.get("logging", {}).get("manifest_file")
        manifest = create_deletion_manifest(self.deleted_items)
        
        try:
            os.makedirs(os.path.dirname(manifest_file), exist_ok=True)
            with open(manifest_file, 'w') as f:
                json.dump(manifest, f, indent=2)
            print(f"\n📝 Deletion manifest saved: {manifest_file}")
        except Exception as e:
            print(f"⚠️  Could not save deletion manifest: {e}")
    
    def log_to_csv(self):
        """Log the deletion stats to CSV."""
        log_file = self.config.get("logging", {}).get("log_file")
        file_exists = os.path.exists(log_file)
        
        folders_size_mb = self.stats["folders_size"] / (1024 * 1024)
        bin_size_mb = self.stats["bin_size"] / (1024 * 1024)
        
        # Get previous cumulative totals
        prev_folders_total, prev_bin_total = self._read_cumulative_totals(log_file)
        
        # Calculate new cumulative totals
        new_folders_total = prev_folders_total + folders_size_mb
        new_bin_total = prev_bin_total + bin_size_mb
        total_deleted = folders_size_mb + bin_size_mb
        cumulative_total = new_folders_total + new_bin_total
        
        try:
            os.makedirs(os.path.dirname(log_file), exist_ok=True)
            with open(log_file, 'a', newline='') as file:
                fieldnames = ['datetime', 'folders_deleted_mb', 'bin_deleted_mb', 'total_deleted_mb',
                            'cumulative_folders_mb', 'cumulative_bin_mb', 'cumulative_total_mb']
                writer = csv.DictWriter(file, fieldnames=fieldnames)
                
                if not file_exists:
                    writer.writeheader()
                
                writer.writerow({
                    'datetime': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'folders_deleted_mb': round(folders_size_mb, 2),
                    'bin_deleted_mb': round(bin_size_mb, 2),
                    'total_deleted_mb': round(total_deleted, 2),
                    'cumulative_folders_mb': round(new_folders_total, 2),
                    'cumulative_bin_mb': round(new_bin_total, 2),
                    'cumulative_total_mb': round(cumulative_total, 2)
                })
            
            print(f"\n📊 Log updated: {log_file}")
            print(f"   Cumulative totals:")
            print(f"   • Folders: {round(new_folders_total, 2)} MB")
            print(f"   • Bin: {round(new_bin_total, 2)} MB")
            print(f"   • Total: {round(cumulative_total, 2)} MB")
            
        except Exception as e:
            print(f"⚠️  Error writing to log file: {e}")
    
    def _read_cumulative_totals(self, log_file: str) -> Tuple[float, float]:
        """Read the last cumulative totals from the CSV."""
        if not os.path.exists(log_file):
            return 0.0, 0.0
        
        try:
            with open(log_file, 'r') as file:
                reader = list(csv.DictReader(file))
                if reader:
                    last_row = reader[-1]
                    return float(last_row['cumulative_folders_mb']), float(last_row['cumulative_bin_mb'])
        except Exception:
            pass
        
        return 0.0, 0.0
    
    def run(self) -> Dict[str, Any]:
        """Run the complete cleanup process.
        
        Returns:
            Dictionary with cleanup statistics
        """
        start_time = datetime.now()
        
        print(f"\n{'='*60}")
        print(f"🧹 jhadoo - Smart Cleanup Tool")
        print(f"{'='*60}")
        print(f"Started: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Mode: {'DRY RUN' if self.dry_run else ('ARCHIVE' if self.archive_mode else 'DELETE')}")
        
        try:
            # Ensure directories exist
            self.config.ensure_directories()
            
            # Task 1: Clean up target folders
            folders_size = self.cleanup_targets()
            
            # Task 2: Clean bin folder
            bin_size = self.clean_bin_folder()
            
            # Save deletion manifest
            if not self.dry_run:
                self.save_deletion_manifest()
                self.log_to_csv()
            
            # Send notification
            if self.config.get("notifications", {}).get("enabled") and not self.dry_run:
                total_mb = (folders_size + bin_size) / (1024 * 1024)
                total_items = self.stats["folders_deleted"] + self.stats["bin_deleted"]
                notify_completion(total_mb, total_items)
            
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            print(f"\n{'='*60}")
            print(f"✅ Cleanup completed in {duration:.1f} seconds")
            print(f"{'='*60}")
            
            return {
                "success": True,
                "stats": self.stats,
                "duration_seconds": duration
            }
            
        except Exception as e:
            error_msg = f"Cleanup failed: {e}"
            print(f"\n❌ {error_msg}")
            
            if self.config.get("notifications", {}).get("on_error"):
                notify_error(str(e))
            
            return {
                "success": False,
                "error": error_msg,
                "stats": self.stats
            }


