#!/usr/bin/env python3
"""Development sync with auto-watch for active development"""

from circuitpy_sync import CircuitPySync
import time

def main():
    print("🔧 Development Sync Mode")
    sync = CircuitPySync()
    
    # Do initial sync
    if sync.sync_all():
        print("✅ Initial sync complete")
        print("🎯 Starting auto-watch mode...")
        print("   Files will auto-sync when changed")
        print("   Press Ctrl+C to stop")
        
        sync.start_auto_sync(interval=1.5)  # Check every 1.5 seconds
        
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            sync.stop_auto_sync()
            print("\n👋 Development sync stopped")

if __name__ == "__main__":
    main()
