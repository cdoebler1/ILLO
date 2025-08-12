# Charles Doebler at Feral Cat AI
# Main UFO routine - reactive audio visualization with NeoPixel ring

from base_routine import BaseRoutine
from audio_processor import AudioProcessor
import time

class IntergalacticCruising(BaseRoutine):
    def __init__(self):
        super().__init__()
        self.audio = AudioProcessor()
        self.last_update = time.monotonic()
        self.rotation_offset = 0
        
        # Debug flag - can be enabled via config
        self.debug = False
        print("[CRUISER] Intergalactic Cruising initialized")
        
    def run(self, mode, volume):
        """Run the intergalactic cruising routine."""
        # Use inherited method for color function selection
        color_func = self.get_color_function(mode)
        
        if self.debug:
            print("[CRUISER] Running with mode: %d, volume: %s" % (mode, volume))
        
        # Process audio and update display
        np_samples = self.audio.record_samples()
        deltas = self.audio.compute_deltas(np_samples)
        
        if self.debug and len(np_samples) > 0:
            print("[CRUISER] Samples: %d, Deltas: %d" % (len(np_samples), len(deltas)))
        
        self._update_visualization(deltas, color_func, volume)
    
    def _update_visualization(self, deltas, color_func, volume):
        """Enhanced visualization with rotation and persistence effects."""
        freq = self.audio.calculate_frequency(deltas)
        
        if self.debug:
            print("[CRUISER] Calculated frequency: %s" % str(freq))
        
        if freq is None:
            # No audio detected - show gentle rotation
            if self.debug:
                print("[CRUISER] No frequency detected - switching to idle animation")
            self._idle_animation(color_func)
            return
            
        # Audio-reactive mode with enhanced effects
        pixel_data = self.hardware.map_deltas_to_pixels(deltas)
        
        if self.debug:
            print("[CRUISER] Pixel data: %s" % str(pixel_data[:3]) + "...")  # Show first 3 values
        
        # Add rotation effect based on frequency
        current_time = time.monotonic()
        time_delta = current_time - self.last_update
        old_rotation = self.rotation_offset
        self.rotation_offset = (self.rotation_offset + freq * time_delta * 0.01) % 10
        
        if self.debug:
            print("[CRUISER] Rotation: %.2f -> %.2f (freq: %.1f, delta: %.3f)" % 
                  (old_rotation, self.rotation_offset, freq, time_delta))
        
        # Clear pixels before applying new pattern
        self.hardware.clear_pixels()
        
        # Apply rotation and intensity mapping
        lit_pixels = 0
        for ii in range(10):
            rotated_index = int((ii + self.rotation_offset) % 10)
            intensity = min(200, pixel_data[ii] * 3)  # Scale for color functions
            if intensity > 40:  # Only light pixels above threshold
                self.hardware.pixels[rotated_index] = color_func(intensity)
                lit_pixels += 1
                
                if self.debug and ii < 3:  # Debug first few pixels
                    print("[CRUISER] Pixel %d -> %d, intensity: %d" % (ii, rotated_index, intensity))
        
        if self.debug:
            print("[CRUISER] Lit %d pixels out of 10" % lit_pixels)
        
        self.hardware.pixels.show()
        self.hardware.play_tone_if_enabled(freq, 0.05, volume)
        
        # Fade effect instead of immediate clear
        time.sleep(0.05)  # Shorter delay
        for ii in range(10):
            current_color = self.hardware.pixels[ii]
            if current_color != (0, 0, 0):  # Only fade non-black pixels
                faded_color = tuple(int(c * 0.8) for c in current_color)  # Gentler fade
                self.hardware.pixels[ii] = faded_color
        
        self.last_update = current_time
        
        if self.debug:
            print("[CRUISER] Frame complete - rotation offset: %.2f" % self.rotation_offset)
    
    def _idle_animation(self, color_func):
        """Gentle rotating animation when no audio detected."""
        current_time = time.monotonic()
        
        if self.debug:
            print("[CRUISER] Idle animation - time since last: %.3f" % (current_time - self.last_update))
        
        if current_time - self.last_update > 0.15:  # Smooth timing
            old_offset = self.rotation_offset
            self.rotation_offset = (self.rotation_offset + 1) % 10
            
            if self.debug:
                print("[CRUISER] Idle rotation: %d -> %d" % (old_offset, self.rotation_offset))
            
            # Clear all pixels first
            self.hardware.clear_pixels()
            
            # Create a rotating comet effect
            main_pos = int(self.rotation_offset)
            trail1_pos = (main_pos - 1) % 10
            trail2_pos = (main_pos - 2) % 10
            
            if self.debug:
                print("[CRUISER] Comet positions - main: %d, trail1: %d, trail2: %d" % 
                      (main_pos, trail1_pos, trail2_pos))
            
            # Use appropriate intensities for the color functions
            # The color functions work best with values around 100-200
            self.hardware.pixels[main_pos] = color_func(120)    # Bright main pixel
            self.hardware.pixels[trail1_pos] = color_func(80)   # Medium trail
            self.hardware.pixels[trail2_pos] = color_func(50)   # Dim trail
            
            self.hardware.pixels.show()
            self.last_update = current_time
            
            if self.debug:
                print("[CRUISER] Idle animation frame displayed")
        else:
            if self.debug:
                print("[CRUISER] Idle animation - waiting (%.3fs remaining)" % 
                      (0.15 - (current_time - self.last_update)))
    
    def enable_debug(self):
        """Enable debug output for this routine."""
        self.debug = True
        print("[CRUISER] Debug mode ENABLED")
