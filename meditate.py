# Charles Doebler at Feral Cat AI
# Meditate routine - breathing pattern light effects for relaxation

from base_routine import BaseRoutine
import time
import math
from adafruit_circuitplayground import cp  # Missing - needed for cp.play_tone()

class Meditate(BaseRoutine):
    def __init__(self):
        super().__init__()
        self.breath_cycle_time = 8.0  # 8 second breathing cycle
        self.start_time = time.monotonic()
        
    def run(self, mode, volume):  # ← Add 'self' parameter here
        instance = Meditate()
        color_func = instance.get_color_function(mode)
        instance._breathing_pattern(color_func, volume)
    
    def _breathing_pattern(self, color_func, volume):
        """Gentle breathing pattern visualization for meditation."""
        current_time = time.monotonic()
        
        # Calculate breathing cycle position (0 to 1)
        cycle_position = ((current_time - self.start_time) % self.breath_cycle_time) / self.breath_cycle_time
        
        # Breathing pattern: inhale (0-0.4), hold (0.4-0.6), exhale (0.6-1.0)
        if cycle_position < 0.4:  # Inhale phase
            intensity = int(255 * (cycle_position / 0.4))
            self._update_breathing_display(color_func, intensity, "inhale")
            if volume == 1 and cycle_position < 0.1:  # Gentle tone at start of inhale
                cp.play_tone(220, 0.1)
                
        elif cycle_position < 0.6:  # Hold phase
            intensity = 255
            self._update_breathing_display(color_func, intensity, "hold")
            
        else:  # Exhale phase
            exhale_progress = (cycle_position - 0.6) / 0.4
            intensity = int(255 * (1 - exhale_progress))
            self._update_breathing_display(color_func, intensity, "exhale")
            if volume == 1 and exhale_progress > 0.9:  # Gentle tone at end of exhale
                cp.play_tone(180, 0.1)
    
    def _update_breathing_display(self, color_func, intensity, phase):
        """Update pixel display based on breathing phase."""
        self.hardware.clear_pixels()
        
        if phase == "inhale":
            # Gradual illumination from center outward
            center_pixels = [4, 5]  # Center of 10-pixel ring
            lit_count = max(1, int((intensity / 255) * 5))
            
            for i in range(lit_count):
                if i < len(center_pixels):
                    pos = center_pixels[i]
                else:
                    # Expand outward
                    offset = i - len(center_pixels) + 1
                    pos1 = (center_pixels[0] - offset) % 10
                    pos2 = (center_pixels[1] + offset) % 10
                    self.hardware.pixels[pos1] = color_func(intensity)
                    self.hardware.pixels[pos2] = color_func(intensity)
                    continue
                
                self.hardware.pixels[pos] = color_func(intensity)
        
        elif phase == "hold":
            # All pixels at full intensity
            for i in range(10):
                self.hardware.pixels[i] = color_func(intensity)
        
        else:  # exhale
            # Gradual fade from outside inward
            fade_count = max(1, int(((255 - intensity) / 255) * 5))
            
            for i in range(10):
                if i < fade_count or i >= (10 - fade_count):
                    self.hardware.pixels[i] = (0, 0, 0)  # Faded pixels
                else:
                    self.hardware.pixels[i] = color_func(intensity)
        
        self.hardware.pixels.show()
