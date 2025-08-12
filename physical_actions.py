# Charles Doebler at Feral Cat AI
# Enhanced physical interaction responses for UFO

from adafruit_circuitplayground import cp
import time
import random

class PhysicalActions:
    @staticmethod
    def tapped(volume):
        """Enhanced tap response with random color burst - LOUDER version."""
        pixels = cp.pixels
        
        # Random color burst effect
        burst_colors = [
            (255, 100, 0),    # Orange
            (0, 255, 150),    # Cyan-green
            (255, 0, 255),    # Magenta
            (255, 255, 0),    # Yellow
            (0, 150, 255),    # Sky blue
        ]
        
        selected_color = random.choice(burst_colors)
        
        # Expanding ring effect with LOUDER tones
        for ring in range(3):
            pixels.fill(0)
            for i in range(ring * 3, min((ring + 1) * 3, 10)):
                pixels[i] = selected_color
                pixels[9-i] = selected_color  # Mirror effect
            pixels.show()
            
            if volume == 1:
                # Much louder and longer tones
                cp.play_tone(800 + ring * 200, 0.3, 1)  # Increased from 0.1 to 0.3
            
            time.sleep(0.15)  # Slightly longer visual
        
        # Quick flash all with BIG sound
        pixels.fill(selected_color)
        pixels.show()
        if volume == 1:
            cp.play_tone(1200, 0.5, 1)  # Much longer tone (0.2 -> 0.5)
        time.sleep(0.3)  # Longer flash
        
        pixels.fill(0)
        pixels.show()

    @staticmethod
    def shaken(volume):
        """Enhanced shake response with turbulence effect - LOUDER version."""
        pixels = cp.pixels
        
        # Turbulence simulation - chaotic flashing with LOUD chaos
        for _ in range(15):  # More flashes (10 -> 15)
            pixels.fill(0)
            
            # Random pixels light up in red/orange (danger colors)
            danger_colors = [(255, 0, 0), (255, 100, 0), (255, 50, 0)]
            
            for i in range(random.randint(3, 7)):  # 3-7 random pixels
                pixel_pos = random.randint(0, 9)
                pixels[pixel_pos] = random.choice(danger_colors)
            
            pixels.show()
            
            if volume == 1:
                # LOUDER random frequency for chaotic sound
                freq = random.randint(200, 1000)  # Wider range (200-800 -> 200-1000)
                cp.play_tone(freq, 0.1, 1)  # Longer duration (0.05 -> 0.1)
            
            time.sleep(0.08)  # Slightly longer (0.05 -> 0.08)
        
        # Stabilization sequence - calming blue sweep with LOUDER descending tones
        for i in range(10):
            pixels.fill(0)
            pixels[i] = (0, 0, 255)  # Blue
            if i > 0:
                pixels[i-1] = (0, 0, 100)  # Dimmer blue trail
            pixels.show()
            
            if volume == 1:
                # MUCH LOUDER descending tone sequence
                cp.play_tone(600 - i * 30, 0.15, 1)  # Louder and longer (400->600, 0.08->0.15)
            
            time.sleep(0.1)  # Slightly longer visual
        
        pixels.fill(0)
        pixels.show()
        
        # Final "stabilized" confirmation tone
        if volume == 1:
            cp.play_tone(220, 0.4, 1)  # Deep, long stabilization tone
