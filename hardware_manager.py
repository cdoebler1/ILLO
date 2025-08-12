# Charles Doebler at Feral Cat AI
# Hardware management for Circuit Playground UFO

from adafruit_circuitplayground import cp
import simpleio

class HardwareManager:
    def __init__(self):
        self.pixels = cp.pixels
        self.pixels.brightness = 0.1  # Battery conservation
        
    def update_pixels_with_data(self, pixel_data, color_func):
        """Update pixels based on data array and color function."""
        for ii in range(10):
            self.pixels[ii] = color_func(pixel_data[ii])
        self.pixels.show()
        
    def clear_pixels(self):
        """Clear all pixels."""
        self.pixels.fill(0)
        
    def play_tone_if_enabled(self, freq, duration, volume):
        """Play tone if volume is enabled."""
        if volume == 1:
            cp.play_tone(freq, duration, 1)
            
    def map_deltas_to_pixels(self, deltas):
        """Map audio deltas to pixel positions."""
        pixel_data = [0] * 10
        for ii, delta in enumerate(deltas):
            ix = round(simpleio.map_range(ii, 0, len(deltas), 0, 9))
            pixel_data[ix] += delta
        return pixel_data
    
    def get_accelerometer(self):
        """Get accelerometer data from the Circuit Playground."""
        return cp.acceleration
