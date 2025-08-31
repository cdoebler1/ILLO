import os
import shutil
import time
import threading
from pathlib import Path
import serial.tools.list_ports
from typing import List, Optional

class CircuitPySync:
    def __init__(self, project_root: str = None):
        self.project_root = Path(project_root) if project_root else Path.cwd()
        self.circuitpy_drive = None
        self.auto_sync = False
        self.sync_thread = None
        
        # Files to sync (customize as needed)
        self.sync_files = [
            # Core CircuitPython files
            'code.py',                    # Main entry point
            'boot.py',                    # Boot configuration
            'config.json',                # Configuration settings
            
            # Audio and chant detection system
            'chant_detector.py',          # Main chant detection logic
            'audio_processor.py',         # Audio processing utilities
            
            # College system
            'college_manager.py',         # College data management
            'ufo_college_system.py',      # UFO college integration
            
            # UFO AI system
            'ufo_intelligence.py',        # Core AI logic
            'ufo_ai_behaviors.py',        # AI behavior patterns
            'ufo_ai_core.py',            # Core AI functionality
            'ufo_learning.py',           # Learning algorithms
            'ufo_memory_manager.py',     # Memory management
            
            # Hardware and utilities
            'hardware_manager.py',       # Hardware abstraction
            'base_routine.py',           # Base routines
            'color_utils.py',           # Color manipulation utilities
            'physical_actions.py',       # Physical device actions
            
            # Entertainment modules
            'dance_party.py',           # Dance party mode
            'music_player.py',          # Music playback
            'meditate.py',              # Meditation mode
            'intergalactic_cruising.py', # Cruising mode
            
            # Development tools (optional - comment out for production)
            # 'serial_monitor.py',        # Serial debugging
            # 'dev_sync.py',            # Development sync (usually not needed on device)
            # 'quick_sync.py',          # Quick sync (usually not needed on device)
            # 'sync_manager.py',        # Sync management (usually not needed on device)
        ]
        
        # Directories to sync
        self.sync_directories = [
            'lib',
            'colleges',
            'sd'
        ]
    
    def find_circuitpy_drive(self) -> Optional[str]:
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
        import psutil
        try:
            for partition in psutil.disk_partitions():
                if 'CIRCUITPY' in partition.mountpoint.upper():
                    return partition.mountpoint
        except:
            pass
            
        return None
    
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
            
            # Copy entire directory tree
            shutil.copytree(source_dir, dest_dir)
            if show_status:
                print(f"📂 Synced directory: {dirname}")
            return True
            
        except Exception as e:
            if show_status:
                print(f"❌ Failed to sync directory {dirname}: {e}")
            return False
    
    def sync_all(self) -> bool:
        """Sync all configured files and directories"""
        if not self.detect_drive():
            return False
        
        print("🔄 Starting full sync to Circuit Playground...")
        
        success_count = 0
        total_items = len(self.sync_files) + len(self.sync_directories)
        
        # Sync individual files
        for filename in self.sync_files:
            if self.sync_file(filename):
                success_count += 1
        
        # Sync directories
        for dirname in self.sync_directories:
            if self.sync_directory(dirname):
                success_count += 1
        
        print(f"✅ Sync complete: {success_count}/{total_items} items transferred")
        return success_count == total_items
    
    def watch_and_sync(self, interval: float = 2.0):
        """Watch for file changes and auto-sync"""
        if not self.detect_drive():
            return
        
        print(f"👁️  Starting auto-sync (checking every {interval}s)...")
        print("Press Ctrl+C to stop auto-sync")
        
        file_timestamps = {}
        
        def get_file_timestamp(filepath):
            try:
                return os.path.getmtime(filepath)
            except:
                return 0
        
        # Initialize timestamps
        for filename in self.sync_files:
            filepath = self.project_root / filename
            file_timestamps[filename] = get_file_timestamp(filepath)
        
        try:
            while self.auto_sync:
                changed_files = []
                
                # Check for changes
                for filename in self.sync_files:
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


def main():
    """Command-line interface for the sync utility"""
    import sys
    
    sync = CircuitPySync()
    
    if len(sys.argv) < 2:
        print("CircuitPy Sync Utility")
        print("Usage:")
        print("  python circuitpy_sync.py sync          - Sync all files once")
        print("  python circuitpy_sync.py watch         - Start auto-sync")
        print("  python circuitpy_sync.py list          - List files on device")
        print("  python circuitpy_sync.py reset         - Soft reset device")
        print("  python circuitpy_sync.py file <name>   - Sync specific file")
        return
    
    command = sys.argv[1].lower()
    
    if command == 'sync':
        sync.sync_all()
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
    else:
        print(f"Unknown command: {command}")

if __name__ == "__main__":
    main()
