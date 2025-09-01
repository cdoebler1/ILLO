# Charles Doebler at Feral Cat AI
# Hardware management for Circuit Playground UFO

from adafruit_circuitplayground import cp
import simpleio
import time

class HardwareManager:
    def __init__(self):
        self.pixels = cp.pixels
        self.base_brightness = 0.1  # Default brightness for battery conservation
        self.pixels.brightness = self.base_brightness
        
        # Light-based features
        self.light_history = [0] * 5  # Track recent light readings
        self.light_history_index = 0
        self.last_light_update = 0
        self.interaction_threshold = 50  # Light change threshold for interaction detection
        
    def update_brightness_for_ambient_light(self):
        """Automatically adjust LED brightness based on ambient light."""
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
        current_brightness = self.pixels.brightness
        if abs(target_brightness - current_brightness) > 0.01:
            if target_brightness > current_brightness:
                self.pixels.brightness = min(target_brightness, current_brightness + 0.01)
            else:
                self.pixels.brightness = max(target_brightness, current_brightness - 0.01)
        
        return current_light
    
    def check_light_interaction(self):
        """Check for sudden light changes indicating user interaction."""
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
        
    def update_pixels_with_data(self, pixel_data, color_func):
        """Update pixels based on data array and color function."""
        for ii in range(10):
            self.pixels[ii] = color_func(pixel_data[ii])
        self.pixels.show()
        
    def clear_pixels(self):
        """Clear all pixels."""
        self.pixels.fill(0)

    @staticmethod
    def play_tone_if_enabled(freq, duration, volume):
        """Play tone if volume is enabled."""
        if volume == 1:
            cp.play_tone(freq, duration, 1)

    @staticmethod
    def map_deltas_to_pixels(deltas):
        """Map audio deltas to pixel positions."""
        pixel_data = [0] * 10
        for ii, delta in enumerate(deltas):
            ix = round(simpleio.map_range(ii, 0, len(deltas), 0, 9))
            pixel_data[ix] += delta
        return pixel_data

    @staticmethod
    def get_accelerometer():
        """Get accelerometer data from the Circuit Playground."""
        return cp.acceleration

    @staticmethod
    def tap_detected():
        """Check if a tap has been detected."""
        return cp.tapped

    @staticmethod
    def shake_detected(threshold=11):
        """Check if a shake has been detected."""
        return cp.shake(shake_threshold=threshold)
    
    @property
    def light(self):
        """Get the current light sensor reading."""
        return cp.light
    
    @property
    def temperature(self):
        """Get the current temperature reading."""
        return cp.temperature
