# Charles Doebler at Feral Cat AI
# Color utility functions for UFO NeoPixel ring lighting effects

from adafruit_circuitplayground import cp

class ColorFunctions:
    # Define pixel colors for UFO rainbow sequence (10 NeoPixels)
    COLORS = (
        (0xFF, 0x00, 0x00),  # Red
        (0xFF, 0x45, 0x00),  # Orange Red
        (0xFF, 0xA5, 0x00),  # Orange
        (0xFF, 0xD7, 0x00),  # Gold
        (0xFF, 0xFF, 0x00),  # Yellow
        (0xAD, 0xFF, 0x2F),  # Green Yellow
        (0x00, 0x80, 0x00),  # Green
        (0x00, 0xFF, 0xFF),  # Cyan
        (0x1E, 0x90, 0xFF),  # Dodger Blue
        (0x41, 0x69, 0xE1),  # Royal Blue
    )

    @staticmethod
    def wheel(wheelpos):
        """Color wheel function for smooth color transitions."""
        if wheelpos < 40:
            return 0, 0, 0
        elif wheelpos < 85:
            return wheelpos * 3, 255 - wheelpos * 3, 0
        elif wheelpos < 170:
            wheelpos -= 85
            return 255 - wheelpos * 3, 0, wheelpos * 3
        else:
            wheelpos -= 170
            return 0, wheelpos * 3, 255 - wheelpos * 3

    @staticmethod
    def pink(wheelpos):
        """Pink color variations for UFO effects."""
        if wheelpos < 40:
            return 0, 0, 0
        elif wheelpos < 85:
            return 199, 21, 133
        elif wheelpos < 170:
            return 255, 105, 180
        else:
            return 255, 20, 147

    @staticmethod
    def blue(wheelpos):
        """Blue color variations for UFO effects."""
        if wheelpos < 40:
            return 0, 0, 0
        elif wheelpos < 85:
            return 0, 191, 255
        elif wheelpos < 170:
            return 0, 0, 255
        else:
            return 25, 25, 112

    @staticmethod
    def show_selection_feedback(routine, mode):
        """Visual feedback for button presses - shows current routine/mode selection."""
        pixels = cp.pixels
        pixels.fill(0)
        
        # Green pixels show routine number (left side)
        for i in range(min(routine, 5)):  # Limit to available pixels
            pixels[i] = (0x00, 0xFF, 0x00)
        
        # Blue pixels show mode number (right side)
        for j in range(min(mode, 5)):  # Limit to available pixels
            pixels[9 - j] = (0x00, 0x00, 0xFF)
        
        pixels.show()
        pixels.fill(0)  # Clear after display

    # Add this method to ColorFunctions class

    @staticmethod
    def get_mode_description(mode):
        """Get description of color mode for user feedback."""
        descriptions = {
            1: "Rainbow Wheel",
            2: "Pink Nebula", 
            3: "Deep Space Blue",
            4: "Reserved",
            5: "Reserved"
        }
        return descriptions.get(mode, "Unknown Mode")
