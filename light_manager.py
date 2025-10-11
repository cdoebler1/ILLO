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
            self.light_history = [0] * 5  # Track recent light readings for spike detection
            self.light_history_index = 0
            self.last_light_update = 0
            self.interaction_threshold = 50  # Light change threshold for interaction detection
            
            # Adaptive baseline for normalization
            self.baseline_light = 0  # Long-term average that adapts slowly
            self.baseline_initialized = False
            self.baseline_adaptation_rate = 0.02  # How quickly baseline adapts (2% per reading)

        print(
            "[LIGHT] Light Manager initialized (interactions: %s)" % enable_interactions)

    def update_brightness_for_ambient_light(self, pixels):
        """
        Automatically adjust LED brightness based on ambient light.
        Uses proportional scaling with min/max bounds for better adaptation.
        
        Args:
            pixels: NeoPixel object to adjust brightness on
            
        Returns:
            current_light: Current light sensor reading
        """
        current_light = cp.light

        # Proportional brightness mapping with reasonable bounds
        # Light sensor typically ranges 0-320 on Circuit Playground
        min_brightness = 0.02  # Minimum visibility in darkness
        max_brightness = 0.25  # Maximum to conserve battery
        
        # Use logarithmic scaling for more natural perception
        # Clamp light reading to reasonable range
        clamped_light = max(0, min(320, current_light))
        
        # Map using square root for perceptual linearity
        # (human perception of brightness is non-linear)
        if clamped_light < 10:  # Very dark - use minimum
            target_brightness = min_brightness
        else:
            # Scale from min to max based on square root of light level
            normalized = (clamped_light / 320.0) ** 0.5  # Square root scaling
            target_brightness = min_brightness + (max_brightness - min_brightness) * normalized
            
        # Smooth brightness transitions
        current_brightness = pixels.brightness
        if abs(target_brightness - current_brightness) > 0.01:
            # Adaptive step size based on difference
            brightness_diff = abs(target_brightness - current_brightness)
            if brightness_diff > 0.1:
                step_size = 0.05  # Faster for large changes
            else:
                step_size = 0.01  # Slower for fine adjustments
                
            if target_brightness > current_brightness:
                pixels.brightness = min(target_brightness, current_brightness + step_size)
            else:
                pixels.brightness = max(target_brightness, current_brightness - step_size)

        return current_light

    def check_light_interaction(self):
        """
        Check for sudden light changes indicating user interaction.
        Uses adaptive baseline that normalizes to ambient light over time.
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

            # Initialize baseline on first reading
            if not self.baseline_initialized:
                self.baseline_light = current_light
                self.baseline_initialized = True
            
            # Store in circular buffer for short-term history
            self.light_history[self.light_history_index] = current_light
            self.light_history_index = (self.light_history_index + 1) % len(
                self.light_history)

            self.last_light_update = current_time

            # Check for significant change from baseline
            if len([x for x in self.light_history if x > 0]) >= 3:  # Have enough history
                # Compare current reading to adaptive baseline
                light_change = abs(current_light - self.baseline_light)

                interaction_detected = light_change > self.interaction_threshold
                
                # Slowly adapt baseline toward current light level
                # But only if we're not in the middle of an interaction
                if not interaction_detected:
                    # Gradually move baseline toward current reading
                    self.baseline_light += (current_light - self.baseline_light) * self.baseline_adaptation_rate
                
                if interaction_detected:
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
