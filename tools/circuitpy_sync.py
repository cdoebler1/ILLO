import os
import json
import shutil
import time
import threading
from pathlib import Path
from typing import List, Optional, Dict, Any

class CircuitPySync:
    def __init__(self, project_root: str = None, config_path: str = None):
        self.project_root = Path(project_root) if project_root else Path.cwd()
        
        # If we're in tools directory, adjust project root to parent
        if self.project_root.name == 'tools':
            self.project_root = self.project_root.parent
            
        # Set config path - check tools directory first, then project root
        if config_path:
            self.config_path = Path(config_path)
        else:
            # Try tools directory first, then project root
            tools_config = self.project_root / 'tools' / 'sync_config.json'
            root_config = self.project_root / 'sync_config.json'
            
            if tools_config.exists():
                self.config_path = tools_config
            elif root_config.exists():
                self.config_path = root_config
            else:
                # Default to tools directory for new installations
                self.config_path = tools_config
        self.circuitpy_drive = None
        self.auto_sync = False
        self.sync_thread = None
        
        # Load configuration
        self.config = self.load_config()
        
        # Extract configuration values
        self.sync_files = self.config.get('sync_files', [])
        self.sync_directories = self.config.get('sync_directories', [])
        self.ignore_patterns = self.config.get('ignore_patterns', [])
        self.auto_discover = self.config.get('auto_discover', True)
        self.max_file_size_mb = self.config.get('max_file_size_mb', 5)
        self.development_files = self.config.get('development_files', [])
    
    def load_config(self) -> Dict[str, Any]:
        """Load sync configuration from JSON file"""
        try:
            with open(self.config_path, 'r') as f:
                config = json.load(f)
                print(f"✅ Loaded sync configuration from {self.config_path}")
                return config
        except FileNotFoundError:
            print(f"⚠️  Config file not found at {self.config_path}, using defaults")
            return {
                'sync_files': ['code.py', 'boot.py', 'config.json'],
                'sync_directories': ['lib'],
                'ignore_patterns': ['*.pyc', '__pycache__', '.git'],
                'auto_discover': True,
                'max_file_size_mb': 5
            }
        except json.JSONDecodeError as e:
            print(f"❌ Error parsing config file: {e}")
            print("Using default configuration")
            return self.load_config.__defaults__[0] if hasattr(self.load_config, '__defaults__') else {}
    
    def should_ignore_file(self, filepath: str) -> bool:
        """Check if file should be ignored based on patterns"""
        from fnmatch import fnmatch
        filename = os.path.basename(filepath)
        
        for pattern in self.ignore_patterns:
            if fnmatch(filename, pattern) or fnmatch(filepath, pattern):
                return True
        return False
    
    def is_file_too_large(self, filepath: Path) -> bool:
        """Check if file exceeds maximum size limit"""
        try:
            size_mb = filepath.stat().st_size / (1024 * 1024)
            return size_mb > self.max_file_size_mb
        except (OSError, ValueError):
            return False
    
    @staticmethod
    def find_circuitpy_drive() -> Optional[str]:
        """Find the CIRCUITPY drive letter"""
        # Check common Windows drive letters
        for drive_letter in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ':
            drive_path = f"{drive_letter}:\\"
            if os.path.exists(drive_path):
                # Check if it's a CircuitPython drive
                if os.path.exists(os.path.join(drive_path, 'boot_out.txt')):
                    return drive_path
                # Alternative check - look for code.py
                if os.path.exists(os.path.join(drive_path, 'code.py')):
                    return drive_path

        # Also check for mounted drives with CIRCUITPY label
        try:
            import psutil
            for partition in psutil.disk_partitions():
                if 'CIRCUITPY' in partition.mountpoint.upper():
                    return partition.mountpoint
        except ImportError:
            # psutil not available, skip this check
            pass
        except (OSError, AttributeError):
            # psutil errors (permissions, missing attributes, etc.)
            pass

    def detect_drive(self) -> bool:
        """Detect and set the CircuitPy drive"""
        drive = self.find_circuitpy_drive()
        if drive:
            self.circuitpy_drive = drive
            print(f"✅ Found CIRCUITPY drive at: {drive}")
            return True
        else:
            print("❌ CIRCUITPY drive not found. Make sure Circuit Playground is connected.")
            return False

    def sync_file(self, filename: str, show_status: bool = True) -> bool:
        """Sync a single file to Circuit Playground"""
        if not self.circuitpy_drive:
            if not self.detect_drive():
                return False

        source_path = self.project_root / filename
        dest_path = Path(self.circuitpy_drive) / filename

        if not source_path.exists():
            if show_status:
                print(f"⚠️  Source file not found: {filename}")
            return False

        # Check if file should be ignored
        if self.should_ignore_file(filename):
            if show_status:
                print(f"⏭️  Skipped (ignored): {filename}")
            return True

        # Check file size
        if self.is_file_too_large(source_path):
            if show_status:
                print(f"⚠️  File too large (>{self.max_file_size_mb}MB): {filename}")
            return False

        try:
            # Create destination directory if needed
            dest_path.parent.mkdir(parents=True, exist_ok=True)

            # Copy the file
            shutil.copy2(source_path, dest_path)
            if show_status:
                print(f"📁 Synced: {filename}")
            return True

        except Exception as e:
            if show_status:
                print(f"❌ Failed to sync {filename}: {e}")
            return False
    
    def sync_directory(self, dirname: str, show_status: bool = True) -> bool:
        """Sync an entire directory to Circuit Playground"""
        if not self.circuitpy_drive:
            if not self.detect_drive():
                return False
        
        source_dir = self.project_root / dirname
        dest_dir = Path(self.circuitpy_drive) / dirname
        
        if not source_dir.exists():
            if show_status:
                print(f"⚠️  Source directory not found: {dirname}")
            return False
        
        try:
            # Remove destination directory if it exists
            if dest_dir.exists():
                shutil.rmtree(dest_dir)
            
            # Copy entire directory tree, but filter ignored files
            def ignore_func(dir_path, filenames):
                ignored = []
                for filename in filenames:
                    full_path = str(Path(dir_path) / filename)
                    rel_path = os.path.relpath(full_path, str(source_dir))
                    if self.should_ignore_file(rel_path):
                        ignored.append(filename)
                return ignored
            
            shutil.copytree(source_dir, dest_dir, ignore=ignore_func)
            if show_status:
                print(f"📂 Synced directory: {dirname}")
            return True
            
        except Exception as e:
            if show_status:
                print(f"❌ Failed to sync directory {dirname}: {e}")
            return False
    
    def auto_discover_files(self) -> List[str]:
        """Auto-discover Python files in project if enabled"""
        if not self.auto_discover:
            return []
        
        discovered = []
        for py_file in self.project_root.glob("*.py"):
            filename = py_file.name
            # Skip if already in sync_files or in development_files or should be ignored
            if (filename not in self.sync_files and 
                filename not in self.development_files and
                not self.should_ignore_file(filename)):
                discovered.append(filename)
        
        return discovered
    
    def sync_all(self, include_development: bool = False) -> bool:
        """Sync all configured files and directories with auto-reload protection"""
        if not self.detect_drive():
            return False
        
        print("🔄 Starting full sync to Circuit Playground...")
        
        # Disable auto-reload during sync
        self._disable_circuitpy_autoreload()
        
        try:
        # Determine files to sync
            files_to_sync = self.sync_files.copy()
        
            # Add auto-discovered files if enabled
            if self.auto_discover:
                discovered = self.auto_discover_files()
                if discovered:
                    print(f"🔍 Auto-discovered files: {', '.join(discovered)}")
                    files_to_sync.extend(discovered)
        
            # Add development files if requested
            if include_development:
                files_to_sync.extend(self.development_files)
                print(f"🛠️  Including development files: {', '.join(self.development_files)}")
        
            success_count = 0
            total_items = len(files_to_sync) + len(self.sync_directories)
        
            # Sync directories first
            for dirname in self.sync_directories:
                if self.sync_directory(dirname):
                    success_count += 1
        
            # Sync non-critical files first
            critical_files = ['boot.py', 'code.py']
            other_files = [f for f in files_to_sync if f not in critical_files]
            critical_files_to_sync = [f for f in files_to_sync if f in critical_files]
        
            # Sync other files first
            for filename in other_files:
                if self.sync_file(filename):
                    success_count += 1
        
            # Sync critical files last
            for filename in critical_files_to_sync:
                if self.sync_file(filename):
                    success_count += 1
        
            print(f"✅ Sync complete: {success_count}/{total_items} items transferred")
            return success_count == total_items
        
        finally:
            # Always re-enable auto-reload, even if sync failed
            time.sleep(0.5)  # Give filesystem time to settle
            self._enable_circuitpy_autoreload()
    
    def watch_and_sync(self, interval: float = 2.0):
        """Watch for file changes and auto-sync"""
        if not self.detect_drive():
            return
        
        print(f"👁️  Starting auto-sync (checking every {interval}s)...")
        print("Press Ctrl+C to stop auto-sync")
        
        file_timestamps = {}
        
        def get_file_timestamp(file_path):
            try:
                return os.path.getmtime(file_path)
            except (OSError, ValueError):
                return 0
        
        # Get all files to watch
        files_to_watch = self.sync_files.copy()
        if self.auto_discover:
            files_to_watch.extend(self.auto_discover_files())
        
        # Initialize timestamps
        for filename in files_to_watch:
            filepath = self.project_root / filename
            file_timestamps[filename] = get_file_timestamp(filepath)
        
        try:
            while self.auto_sync:
                changed_files = []
                
                # Check for changes
                for filename in files_to_watch:
                    filepath = self.project_root / filename
                    current_timestamp = get_file_timestamp(filepath)
                    
                    if current_timestamp > file_timestamps[filename]:
                        changed_files.append(filename)
                        file_timestamps[filename] = current_timestamp
                
                # Sync changed files
                for filename in changed_files:
                    print(f"🔄 File changed, syncing: {filename}")
                    self.sync_file(filename)
                
                time.sleep(interval)
                
        except KeyboardInterrupt:
            print("\n⏹️  Auto-sync stopped")
    
    def start_auto_sync(self, interval: float = 2.0):
        """Start auto-sync in background thread"""
        if self.sync_thread and self.sync_thread.is_alive():
            print("Auto-sync already running")
            return
        
        self.auto_sync = True
        self.sync_thread = threading.Thread(target=self.watch_and_sync, args=(interval,), daemon=True)
        self.sync_thread.start()
    
    def stop_auto_sync(self):
        """Stop auto-sync"""
        self.auto_sync = False
        if self.sync_thread:
            self.sync_thread.join(timeout=1)
        print("⏹️  Auto-sync stopped")
    
    def list_circuitpy_files(self):
        """List files currently on Circuit Playground"""
        if not self.detect_drive():
            return
        
        print(f"📋 Files on CIRCUITPY drive ({self.circuitpy_drive}):")
        drive_path = Path(self.circuitpy_drive)
        
        for item in sorted(drive_path.iterdir()):
            if item.is_file():
                size = item.stat().st_size
                print(f"  📄 {item.name} ({size} bytes)")
            elif item.is_dir():
                print(f"  📁 {item.name}/")
    
    def safe_reset_circuitpy(self):
        """Safely reset Circuit Playground by creating a soft reset file"""
        if not self.circuitpy_drive:
            if not self.detect_drive():
                return False
        
        try:
            # Create a temporary file that triggers soft reset
            reset_file = Path(self.circuitpy_drive) / ".reset_request"
            reset_file.write_text("reset")
            print("🔄 Reset request sent to Circuit Playground")
            
            # Clean up the file after a moment
            time.sleep(0.5)
            if reset_file.exists():
                reset_file.unlink()
            
            return True
        except Exception as e:
            print(f"❌ Failed to reset Circuit Playground: {e}")
            return False
    
    def _disable_circuitpy_autoreload(self):
        """Disable CircuitPython auto-reload during sync"""
        if not self.circuitpy_drive:
            return False
        
        try:
            # Create .no_auto_run file to disable auto-reload
            no_reload_file = Path(self.circuitpy_drive) / ".no_auto_run"
            no_reload_file.touch()
            print("🛑 Disabled CircuitPython auto-reload for sync")
            return True
        except Exception as e:
            print(f"⚠️  Couldn't disable auto-reload: {e}")
            return False

    def _enable_circuitpy_autoreload(self):
        """Re-enable CircuitPython auto-reload after sync"""
        if not self.circuitpy_drive:
            return
        
        try:
            no_reload_file = Path(self.circuitpy_drive) / ".no_auto_run"
            if no_reload_file.exists():
                no_reload_file.unlink()
                print("✅ Re-enabled CircuitPython auto-reload")
        except Exception as e:
            print(f"⚠️  Couldn't re-enable auto-reload: {e}")


def main():
    """Command-line interface for the sync utility"""
    import sys
    
    # Determine project root (parent of tools directory if we're in tools)
    current_dir = Path(__file__).parent
    if current_dir.name == 'tools':
        project_root = current_dir.parent
    else:
        project_root = current_dir
    
    sync = CircuitPySync(project_root=str(project_root))
    
    if len(sys.argv) < 2:
        print("CircuitPy Sync Utility (Config-Driven)")
        print("Usage:")
        print("  python circuitpy_sync.py sync             - Sync all files once")
        print("  python circuitpy_sync.py sync --dev       - Sync all files including development tools")
        print("  python circuitpy_sync.py watch            - Start auto-sync")
        print("  python circuitpy_sync.py list             - List files on device")
        print("  python circuitpy_sync.py reset            - Soft reset device")
        print("  python circuitpy_sync.py file <name>      - Sync specific file")
        print("  python circuitpy_sync.py config           - Show current configuration")
        return
    
    command = sys.argv[1].lower()
    
    if command == 'sync':
        include_dev = '--dev' in sys.argv or '-d' in sys.argv
        sync.sync_all(include_development=include_dev)
    elif command == 'watch':
        sync.start_auto_sync()
        try:
            # Keep main thread alive
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            sync.stop_auto_sync()
    elif command == 'list':
        sync.list_circuitpy_files()
    elif command == 'reset':
        sync.safe_reset_circuitpy()
    elif command == 'file' and len(sys.argv) > 2:
        filename = sys.argv[2]
        sync.sync_file(filename)
    elif command == 'config':
        print("Current Configuration:")
        print(f"  Config file: {sync.config_path}")
        print(f"  Project root: {sync.project_root}")
        print(f"  Sync files ({len(sync.sync_files)}): {sync.sync_files}")
        print(f"  Sync directories: {sync.sync_directories}")
        print(f"  Auto-discover: {sync.auto_discover}")
        print(f"  Max file size: {sync.max_file_size_mb}MB")
        print(f"  Ignore patterns: {sync.ignore_patterns}")
        if sync.auto_discover:
            discovered = sync.auto_discover_files()
            if discovered:
                print(f"  Auto-discovered files: {discovered}")
    else:
        print(f"Unknown command: {command}")

if __name__ == "__main__":
    main()
