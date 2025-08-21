# Charles Doebler at Feral Cat AI
# Meditate routine - breathing pattern light effects for relaxation

from base_routine import BaseRoutine
import time

class Meditate(BaseRoutine):
    def __init__(self):
        super().__init__()
        self.breath_cycle_time = 12.0  # Increased to 12-second breathing cycle for deeper meditation
        self.start_time = time.monotonic()
        # Track when breathing sounds have been played to prevent clicking
        self.inhale_sound_played = False
        self.exhale_sound_played = False
        self.last_phase = None
        self.last_update = 0
        self.update_delay = 0.05  # Control display update rate
        print("[MEDITATE] 🧘 Meditate routine initialized - 12s breathing cycle")
        
    def run(self, mode, volume):
        """Run the meditate routine using the current instance."""
        current_time = time.monotonic()
        
        # Control update frequency to slow down the animation
        if current_time - self.last_update < self.update_delay:
            return
        
        self.last_update = current_time
        color_func = self.get_color_function(mode)
        self._breathing_pattern(color_func, volume)
    
    def _breathing_pattern(self, color_func, volume):
        """Gentle breathing pattern visualization for meditation."""
        current_time = time.monotonic()
        
        # Calculate breathing cycle position (0 to 1) - now over 12 seconds
        cycle_position = ((current_time - self.start_time) % self.breath_cycle_time) / self.breath_cycle_time
        
        # Breathing pattern: inhale (0-0.4), hold (0.4-0.6), exhale (0.6-1.0)
        if cycle_position < 0.4:  # Inhale phase (4.8 seconds)
            current_phase = "inhale"
            # Smooth inhale progression
            inhale_progress = cycle_position / 0.4
            intensity = int(255 * inhale_progress)
            self._update_breathing_display(color_func, intensity, "inhale")
            
            # Play gentle inhale tone only once at the beginning
            if volume == 1 and not self.inhale_sound_played and cycle_position < 0.02:
                self.hardware.play_tone_if_enabled(220, 1.0, volume)  # 1 second gentle tone for inhale
                self.inhale_sound_played = True
                
        elif cycle_position < 0.6:  # Hold phase (2.4 seconds)
            current_phase = "hold"
            intensity = 255  # Full brightness during hold
            self._update_breathing_display(color_func, intensity, "hold")
            
        else:  # Exhale phase (4.8 seconds)
            current_phase = "exhale"
            exhale_progress = (cycle_position - 0.6) / 0.4
            # Smooth exhale progression
            intensity = int(255 * (1 - exhale_progress))
            self._update_breathing_display(color_func, intensity, "exhale")
            
            # Play gentle exhale tone only once at the beginning
            if volume == 1 and not self.exhale_sound_played and exhale_progress < 0.02:
                self.hardware.play_tone_if_enabled(180, 1.2, volume)  # 1.2 second lower tone for exhale
                self.exhale_sound_played = True
        
        # Reset sound flags when transitioning between phases
        if current_phase != self.last_phase:
            if current_phase == "inhale":
                self.exhale_sound_played = False  # Reset for next exhale
            elif current_phase == "exhale":
                self.inhale_sound_played = False  # Reset for next inhale
            elif current_phase == "hold":
                # Optional: Add a subtle tone for the hold phase
                if volume == 1:
                    self.hardware.play_tone_if_enabled(200, 0.2, volume)  # Brief, gentle hold tone
            
            self.last_phase = current_phase
    
    def _update_breathing_display(self, color_func, intensity, phase):
        """Update pixel display based on breathing phase with smoother animations."""
        self.hardware.clear_pixels()
        
        if phase == "inhale":
            # Smooth expansion from center outward based on intensity
            expansion_level = (intensity / 255.0) * 5  # 0 to 5 expansion levels
            
            # Always light center pixels first
            center_pixels = [4, 5]
            for pos in center_pixels:
                self.hardware.pixels[pos] = color_func(intensity)
            
            # Gradually expand outward
            if expansion_level > 1:
                outer_pixels = [3, 6]  # Next ring
                for pos in outer_pixels:
                    fade_intensity = int(intensity * min(1.0, expansion_level - 1))
                    self.hardware.pixels[pos] = color_func(fade_intensity)
                    
            if expansion_level > 2:
                far_pixels = [2, 7]  # Further out
                for pos in far_pixels:
                    fade_intensity = int(intensity * min(1.0, expansion_level - 2))
                    self.hardware.pixels[pos] = color_func(fade_intensity)
                    
            if expansion_level > 3:
                edge_pixels = [1, 8]  # Near edges
                for pos in edge_pixels:
                    fade_intensity = int(intensity * min(1.0, expansion_level - 3))
                    self.hardware.pixels[pos] = color_func(fade_intensity)
                    
            if expansion_level > 4:
                final_pixels = [0, 9]  # Full expansion
                for pos in final_pixels:
                    fade_intensity = int(intensity * min(1.0, expansion_level - 4))
                    self.hardware.pixels[pos] = color_func(fade_intensity)
        
        elif phase == "hold":
            # All pixels at full, steady intensity - peaceful moment
            for i in range(10):
                self.hardware.pixels[i] = color_func(intensity)
        
        else:  # exhale - gradual fade from outside inward
            fade_level = (intensity / 255.0) * 5  # 5 to 0 as we exhale
            
            # Fade outer pixels first, keep center longest
            pixels_active = int(fade_level)
            
            # Always keep some center pixels during exhale
            if pixels_active >= 1:
                center_pixels = [4, 5]
                for pos in center_pixels:
                    self.hardware.pixels[pos] = color_func(intensity)
                    
            if pixels_active >= 2:
                inner_pixels = [3, 6]
                for pos in inner_pixels:
                    self.hardware.pixels[pos] = color_func(intensity)
                    
            if pixels_active >= 3:
                mid_pixels = [2, 7]
                for pos in mid_pixels:
                    self.hardware.pixels[pos] = color_func(intensity)
                    
            if pixels_active >= 4:
                outer_pixels = [1, 8]
                for pos in outer_pixels:
                    self.hardware.pixels[pos] = color_func(intensity)
                    
            if pixels_active >= 5:
                edge_pixels = [0, 9]
                for pos in edge_pixels:
                    self.hardware.pixels[pos] = color_func(intensity)
        
        self.hardware.pixels.show()
