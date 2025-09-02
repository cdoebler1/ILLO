# Charles Doebler at Feral Cat AI
# Memory Manager - Centralized memory monitoring and cleanup

import gc
import time


class MemoryManager:
    def __init__(self, enable_debug=True):
        """
        Initialize Memory Manager.
        
        Args:
            enable_debug: Whether to enable memory debug output
        """
        self.enable_debug = enable_debug
        self.last_memory_check = 0
        self.memory_check_interval = 10.0  # Check every 10 seconds
        self.low_memory_threshold = 5000   # Warn if less than 5KB free
        self.critical_memory_threshold = 2000  # Critical if less than 2KB free
        
        print("[MEMORY] Memory Manager initialized (debug: %s)" % enable_debug)
        
        # Initial memory report
        if self.enable_debug:
            self.log_memory_status("Startup")
    
    def periodic_cleanup(self, force=False):
        """
        Perform periodic memory cleanup and monitoring.
        
        Args:
            force: Force cleanup regardless of timing
            
        Returns:
            bool: True if cleanup was performed
        """
        current_time = time.monotonic()
        
        if force or (current_time - self.last_memory_check >= self.memory_check_interval):
            # Force garbage collection
            gc.collect()
            
            # Check memory status
            free_mem = gc.mem_free()
            alloc_mem = gc.mem_alloc()
            total_mem = free_mem + alloc_mem
            
            if self.enable_debug:
                print("[MEMORY] 🧠 Free: %d, Used: %d (%.1f%% full)" %
                      (free_mem, alloc_mem, (alloc_mem * 100.0) / total_mem))
            
            # Memory warnings
            if free_mem < self.critical_memory_threshold:
                print("[MEMORY] 🚨 CRITICAL MEMORY! Only %d bytes free!" % free_mem)
                # Force additional cleanup
                self._emergency_cleanup()
            elif free_mem < self.low_memory_threshold:
                print("[MEMORY] ⚠️  LOW MEMORY WARNING! %d bytes free" % free_mem)
            
            self.last_memory_check = current_time
            return True
        
        return False
    
    def _emergency_cleanup(self):
        """Perform emergency memory cleanup when critically low."""
        print("[MEMORY] 🚨 Emergency cleanup initiated...")
        
        # Multiple garbage collection passes
        for i in range(3):
            gc.collect()
            time.sleep(0.1)  # Brief pause between collections
        
        # Report results
        free_after = gc.mem_free()
        print("[MEMORY] 🚨 Emergency cleanup complete: %d bytes free" % free_after)
    
    def log_memory_status(self, context=""):
        """
        Log current memory status with context.
        
        Args:
            context: Context string for the memory report
        """
        if not self.enable_debug:
            return
        
        free_mem = gc.mem_free()
        alloc_mem = gc.mem_alloc()
        total_mem = free_mem + alloc_mem
        
        context_str = (" (%s)" % context) if context else ""
        print("[MEMORY] 📊%s Free: %d, Used: %d, Total: %d (%.1f%% used)" %
              (context_str, free_mem, alloc_mem, total_mem, (alloc_mem * 100.0) / total_mem))
    
    def get_memory_info(self):
        """
        Get current memory information.
        
        Returns:
            dict: Memory information including free, allocated, and percentages
        """
        free_mem = gc.mem_free()
        alloc_mem = gc.mem_alloc()
        total_mem = free_mem + alloc_mem
        
        return {
            'free': free_mem,
            'allocated': alloc_mem,
            'total': total_mem,
            'usage_percent': (alloc_mem * 100.0) / total_mem,
            'is_low': free_mem < self.low_memory_threshold,
            'is_critical': free_mem < self.critical_memory_threshold
        }
    
    def cleanup_before_routine_change(self):
        """Clean up memory before changing routines."""
        if self.enable_debug:
            print("[MEMORY] 🔄 Cleanup before routine change...")
        
        # Force garbage collection
        gc.collect()
        
        # Brief pause for cleanup to complete
        time.sleep(0.1)
        
        if self.enable_debug:
            self.log_memory_status("After routine cleanup")
    
    def set_debug(self, enabled):
        """Enable or disable memory debug output."""
        self.enable_debug = enabled
        print("[MEMORY] Debug output %s" % ("enabled" if enabled else "disabled"))
