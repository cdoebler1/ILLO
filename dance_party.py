# Charles Doebler at Feral Cat AI
# Synchronized dance party routine with beat detection - Memory Optimized

from base_routine import BaseRoutine
from audio_processor import AudioProcessor
import time
# import math
import gc  # Garbage collection for memory management

class DanceParty(BaseRoutine):
    def __init__(self, device_name, debug_bluetooth=False, debug_audio=False):
        super().__init__()
        self.audio = AudioProcessor()
        self.device_name = device_name
        self.debug_bluetooth = debug_bluetooth
        self.debug_audio = debug_audio
        
        # Simplified - no Bluetooth sync to avoid memory issues
        self.sync_manager = None
        self.is_leader = True  # Always run as standalone
        
        # Beat detection parameters - reduced memory footprint
        self.last_beat_time = 0
        self.energy_history = []  # Keep smaller history
        
        self.last_pattern_update = time.monotonic()
        
        print("[DANCE] 🎵 Dance Party initialized (Standalone Mode - No BLE)")
        if debug_bluetooth:
            print("[DANCE] ⚠️ Bluetooth disabled to prevent memory errors")
        
    def run(self, mode, volume):
        """Run the standalone dance party (no Bluetooth sync)."""
        # Force garbage collection to free memory
        gc.collect()
        
        color_func = self.get_color_function(mode)
        self._run_standalone(color_func, volume)
    
    def _run_standalone(self, color_func, volume):
        """Standalone dance mode - no Bluetooth, just local beat detection."""
        try:
            # Get audio samples for beat detection
            np_samples = self.audio.record_samples()
            
            # Simple beat detection to avoid memory allocation issues
            beat_detected = self._simple_beat_detection(np_samples)
            
            # Generate and display pattern locally
            self._display_standalone_pattern(color_func, beat_detected, volume)
            
            # Clean up memory periodically
            if int(time.monotonic()) % 10 == 0:  # Every 10 seconds
                gc.collect()
                
        except MemoryError:
            print("[DANCE] ❌ Memory error - switching to safe mode")
            self._safe_mode_pattern(color_func)
            gc.collect()
    
    def _simple_beat_detection(self, np_samples):
        """Simplified beat detection using minimal memory."""
        if len(np_samples) < 50:  # Reduced requirement
            return False
        
        current_time = time.monotonic()
        if current_time - self.last_beat_time < 0.3:  # Minimum interval
            return False
        
        try:
            # Simple energy calculation without creating new arrays
            total_energy = 0
            sample_count = min(len(np_samples), 200)  # Limit processing
            
            # Calculate mean first
            sample_sum = sum(np_samples[i] for i in range(sample_count))
            mean_sample = sample_sum / sample_count
            
            # Calculate energy without storing intermediate arrays
            for i in range(sample_count):
                diff = np_samples[i] - mean_sample
                total_energy += diff * diff
            
            energy = (total_energy / sample_count) ** 0.5
            
            # Simple threshold - no adaptive history to save memory
            beat_detected = energy > 800  # Fixed threshold
            
            if self.debug_audio and int(current_time * 2) % 2 == 0:
                print("[DANCE] Energy: %.1f, Beat: %s" % (energy, beat_detected))
            
            if beat_detected:
                self.last_beat_time = current_time
                if self.debug_audio:
                    print("[DANCE] 🎵 BEAT! 🎵")
                return True
                
        except MemoryError:
            print("[DANCE] Beat detection memory error - using fallback")
            return False
        
        return False
    
    def _display_standalone_pattern(self, color_func, beat_detected, volume):
        """Display dance pattern locally without Bluetooth."""
        try:
            if beat_detected:
                # Beat flash - all pixels same color
                flash_color = color_func(255)
                for i in range(10):
                    self.hardware.pixels[i] = flash_color
                
                # Beat sound
                if volume:
                    self.hardware.play_tone_if_enabled(800, 0.1, volume)
                    
            else:
                # Continuous wave pattern
                current_time = time.monotonic()
                wave_offset = int((current_time * 3) % 10)  # Slower wave
                
                self.hardware.clear_pixels()
                
                # Simple wave with 3 active pixels
                for i in range(3):
                    pos = (wave_offset + i * 3) % 10
                    intensity = 150 - (i * 40)  # Decreasing intensity
                    self.hardware.pixels[pos] = color_func(intensity)
            
            self.hardware.pixels.show()
            
        except MemoryError:
            print("[DANCE] Display memory error - clearing pixels")
            self.hardware.clear_pixels()
            self.hardware.pixels.show()
    
    def _safe_mode_pattern(self, color_func):
        """Ultra-simple pattern for when memory is critically low."""
        current_time = time.monotonic()
        
        # Single rotating pixel - minimal memory usage
        if current_time - self.last_pattern_update > 0.3:
            pos = int((current_time * 2) % 10)
            
            self.hardware.clear_pixels()
            self.hardware.pixels[pos] = color_func(100)
            self.hardware.pixels.show()
            
            self.last_pattern_update = current_time
            
            if self.debug_bluetooth:
                print("[DANCE] Safe mode - single pixel rotation")