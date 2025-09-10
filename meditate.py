# Charles Doebler at Feral Cat AI
# Meditate routine - breathing pattern light effects for relaxation

from base_routine import BaseRoutine
import time
from adafruit_circuitplayground import cp


class Meditate(BaseRoutine):
    def __init__(self):
        super().__init__()

        # Load meditation preferences from config
        self.breath_pattern = self._load_breath_pattern()
        self.adaptive_timing = self._load_adaptive_timing()

        # Breathing pattern definitions
        self.breath_patterns = {
            1: {"name": "4-7-8 Breathing", "inhale": 4.8, "hold1": 2.4, "exhale": 4.8,
                "hold2": 0},
            2: {"name": "Box Breathing", "inhale": 4.0, "hold1": 4.0, "exhale": 4.0,
                "hold2": 4.0},
            3: {"name": "Triangle Breathing", "inhale": 4.0, "hold1": 4.0,
                "exhale": 4.0, "hold2": 0},
            4: {"name": "Deep Relaxation", "inhale": 6.0, "hold1": 2.0, "exhale": 8.0,
                "hold2": 0}
        }

        self.start_time = time.monotonic()
        self.last_phase = None
        self.last_update = 0
        self.update_delay = 0.03  # Smoother updates for meditation

        # Disable all interactions for pure meditation
        self.ignore_interactions = True

        current_pattern = self.breath_patterns[self.breath_pattern]
        print("[MEDITATE] 🧘 Enhanced Meditate initialized")
        print("[MEDITATE] Pattern: %s (Adaptive: %s)" % (
            current_pattern["name"],
            "ON" if self.adaptive_timing else "OFF"
        ))

    def _load_breath_pattern(self):
        """Load breath pattern preference from config."""
        try:
            from config_manager import ConfigManager
            config_mgr = ConfigManager()
            config = config_mgr.load_config()
            return config.get('meditate_breath_pattern', 1)
        except:
            return 1  # Default to 4-7-8 breathing

    def _load_adaptive_timing(self):
        """Load adaptive timing preference from config."""
        try:
            from config_manager import ConfigManager
            config_mgr = ConfigManager()
            config = config_mgr.load_config()
            return config.get('meditate_adaptive_timing', True)
        except:
            return True  # Default enabled

    def run(self, mode, volume):
        """Run the enhanced meditate routine - completely silent and non-reactive."""
        current_time = time.monotonic()

        # Control update frequency for smooth meditation experience
        if current_time - self.last_update < self.update_delay:
            return

        self.last_update = current_time
        color_func = self.get_color_function(mode)

        # Force silent operation - meditation should never make sound
        self._breathing_pattern(color_func, volume=0)  # Always silent

    def update_pattern(self, new_pattern):
        """Update breathing pattern when changed via Button B."""
        if new_pattern != self.breath_pattern:
            old_pattern_name = self.breath_patterns[self.breath_pattern]["name"]
            self.breath_pattern = new_pattern
            self.start_time = time.monotonic()  # Reset cycle timing for smooth transition

            new_pattern_name = self.breath_patterns[self.breath_pattern]["name"]
            print("[MEDITATE] 🔄 Pattern updated: %s -> %s" % (old_pattern_name,
                                                              new_pattern_name))

    def _calculate_adaptive_timing(self):
        """Calculate timing multiplier based on ambient light if enabled."""
        if not self.adaptive_timing:
            return 1.0

        light_level = cp.light

        if light_level < 30:  # Very dark - evening/night meditation
            return 1.3  # 30% slower for deep relaxation
        elif light_level < 60:  # Dark - indoor evening
            return 1.15  # 15% slower
        elif light_level > 150:  # Bright - daytime alertness
            return 0.9  # 10% faster
        else:  # Normal indoor lighting
            return 1.0  # Standard timing

    def _breathing_pattern(self, color_func, volume):
        """Enhanced breathing pattern with multiple techniques."""
        current_time = time.monotonic()

        # Get current pattern settings
        pattern = self.breath_patterns[self.breath_pattern]
        timing_multiplier = self._calculate_adaptive_timing()

        # Calculate total cycle time with adaptive timing
        total_cycle_time = (pattern["inhale"] + pattern["hold1"] +
                            pattern["exhale"] + pattern["hold2"]) * timing_multiplier

        # Calculate cycle position (0 to 1)
        cycle_position = ((
                                      current_time - self.start_time) % total_cycle_time) / total_cycle_time

        # Calculate phase boundaries
        inhale_end = (pattern["inhale"] * timing_multiplier) / total_cycle_time
        hold1_end = inhale_end + (
                    pattern["hold1"] * timing_multiplier) / total_cycle_time
        exhale_end = hold1_end + (
                    pattern["exhale"] * timing_multiplier) / total_cycle_time
        # hold2 is the remainder

        # Determine current phase and intensity
        if cycle_position < inhale_end:
            # Inhale phase
            current_phase = "inhale"
            phase_progress = cycle_position / inhale_end
            intensity = int(255 * phase_progress)

        elif cycle_position < hold1_end:
            # First hold phase
            current_phase = "hold1"
            intensity = 255

        elif cycle_position < exhale_end:
            # Exhale phase
            current_phase = "exhale"
            phase_progress = (cycle_position - hold1_end) / (exhale_end - hold1_end)
            intensity = int(255 * (1 - phase_progress))

        else:
            # Second hold phase (if exists)
            current_phase = "hold2"
            intensity = 30  # Very dim for rest phase

        # Update display with pattern-specific visualization
        self._update_meditation_display(color_func, intensity, current_phase, pattern)

        # Phase transition logging (silent - no sounds ever in meditation)
        if current_phase != self.last_phase:
            self.last_phase = current_phase

    def _update_meditation_display(self, color_func, intensity, phase, pattern):
        """Enhanced meditation display with pattern-specific visuals."""
        self.hardware.clear_pixels()

        # Ultra-low brightness for meditation
        base_brightness = min(0.05, self.hardware.pixels.brightness)
        self.hardware.pixels.brightness = base_brightness

        if phase == "inhale":
            self._show_expansion_pattern(color_func, intensity, pattern)
        elif phase in ["hold1", "hold2"]:
            self._show_hold_pattern(color_func, intensity, phase)
        else:  # exhale
            self._show_contraction_pattern(color_func, intensity, pattern)

        self.hardware.pixels.show()

    def _show_expansion_pattern(self, color_func, intensity, pattern):
        """Show expansion during inhale - pattern specific."""
        expansion_level = (intensity / 255.0) * 5

        # Center-focused expansion for all patterns
        center_pixels = [4, 5]  # Always start here
        for pos in center_pixels:
            self.hardware.pixels[pos] = color_func(intensity)

        # Pattern-specific expansion styles
        if pattern["name"] == "Box Breathing":
            # Square expansion pattern
            if expansion_level > 1:
                square_pixels = [3, 6, 2, 7]
                for i, pos in enumerate(square_pixels):
                    if expansion_level > i + 1:
                        fade_intensity = int(
                            intensity * min(1.0, expansion_level - i - 1))
                        self.hardware.pixels[pos] = color_func(fade_intensity)
        else:
            # Circular expansion for other patterns
            expansion_rings = [[3, 6], [2, 7], [1, 8], [0, 9]]
            for i, ring in enumerate(expansion_rings):
                if expansion_level > i + 1:
                    for pos in ring:
                        fade_intensity = int(
                            intensity * min(1.0, expansion_level - i - 1))
                        self.hardware.pixels[pos] = color_func(fade_intensity)

    def _show_hold_pattern(self, color_func, intensity, phase):
        """Show steady pattern during hold phases."""
        if phase == "hold2":
            # Second hold - very minimal presence
            center_pixels = [4, 5]
            for pos in center_pixels:
                self.hardware.pixels[pos] = color_func(intensity)
        else:
            # First hold - full steady presence
            for i in range(10):
                self.hardware.pixels[i] = color_func(intensity)

    def _show_contraction_pattern(self, color_func, intensity, pattern):
        """Show contraction during exhale."""
        fade_level = (intensity / 255.0) * 5
        pixels_active = int(fade_level) + 1  # Always keep at least center

        # Maintain center longest, fade outward
        pixel_priority = [4, 5, 3, 6, 2, 7, 1, 8, 0, 9]

        for i, pos in enumerate(pixel_priority):
            if i < pixels_active:
                self.hardware.pixels[pos] = color_func(intensity)