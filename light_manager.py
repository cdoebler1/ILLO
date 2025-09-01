# Charles Doebler at Feral Cat AI
# Light Manager - Handles all light sensing and interaction detection

import time
from adafruit_circuitplayground import cp


class LightManager:
    def __init__(self, enable_interactions=True):
        """
        Initialize Light Manager.
        
        Args:
            enable_interactions: Whether to enable complex light interaction detection
        """
        self.enable_interactions = enable_interactions
        
        # Light-based features (only if interactions enabled)
        if self.enable_interactions:
            self.light_history = [0] * 5  # Track recent light readings
            self.light_history_index = 0
            self.last_light_update = 0
            self.interaction_threshold = 50  # Light change threshold for interaction detection
        
        print("[LIGHT] Light Manager initialized (interactions: %s)" % enable_interactions)
        
    def update_brightness_for_ambient_light(self, pixels):
        """
        Automatically adjust LED brightness based on ambient light.
        
        Args:
            pixels: NeoPixel object to adjust brightness on
            
        Returns:
            current_light: Current light sensor reading
        """
        current_light = cp.light
        
        # Map light sensor reading to brightness levels
        if current_light < 20:  # Very dark
            target_brightness = 0.03
        elif current_light < 50:  # Dark
            target_brightness = 0.05
        elif current_light < 100:  # Indoor lighting
            target_brightness = 0.1
        elif current_light < 200:  # Bright indoor
            target_brightness = 0.15
        else:  # Very bright
            target_brightness = 0.2
            
        # Smooth brightness transitions
        current_brightness = pixels.brightness
        if abs(target_brightness - current_brightness) > 0.01:
            if target_brightness > current_brightness:
                pixels.brightness = min(target_brightness, current_brightness + 0.01)
            else:
                pixels.brightness = max(target_brightness, current_brightness - 0.01)
        
        return current_light
    
    def check_light_interaction(self):
        """
        Check for sudden light changes indicating user interaction.
        Only works if interactions are enabled.
        
        Returns:
            (interaction_detected, light_change, current_light)
        """
        if not self.enable_interactions:
            return False, 0, cp.light
            
        current_time = time.monotonic()
        
        # Update light history every 0.1 seconds
        if current_time - self.last_light_update > 0.1:
            current_light = cp.light
            
            # Store in circular buffer
            self.light_history[self.light_history_index] = current_light
            self.light_history_index = (self.light_history_index + 1) % len(self.light_history)
            
            self.last_light_update = current_time
            
            # Check for significant change
            if len([x for x in self.light_history if x > 0]) >= 3:  # Have enough history
                avg_light = sum(self.light_history) / len(self.light_history)
                light_change = abs(current_light - avg_light)
                
                if light_change > self.interaction_threshold:
                    return True, light_change, current_light
        
        return False, 0, cp.light
    
    def get_current_light_level(self):
        """Get the current light sensor reading."""
        return cp.light
    
    def reset_light_history(self):
        """Reset light interaction history."""
        if self.enable_interactions:
            self.light_history = [0] * 5
            self.light_history_index = 0
            print("[LIGHT] Light interaction history reset")
