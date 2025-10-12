# Charles Doebler at Feral Cat AI
# Meditate routine - breathing pattern light effects for relaxation

from base_routine import BaseRoutine
import time
from adafruit_circuitplayground import cp


class Meditate(BaseRoutine):
    def __init__(self, adaptive_timing=None, ultra_dim=None):
        super().__init__()

        if adaptive_timing is not None:
            self.adaptive_timing = adaptive_timing
        else:
            self.adaptive_timing = self._load_adaptive_timing()

        # Store ultra_dim setting (not currently used but available for future brightness control)
        self.ultra_dim = ultra_dim if ultra_dim is not None else True

        # Breathing pattern definitions
        self.breath_patterns = {
            1: {"name": "4-7-8 Breathing", "inhale": 4.0, "hold1": 7.0, "exhale": 8.0,
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
        self.update_delay = 0.05  # Increased from 0.03 for better performance

        # Cache for smoother performance
        self.last_intensity = -1

        # Disable all interactions for pure meditation
        self.ignore_interactions = True

        # Track last pattern mode to detect changes
        self.last_pattern_mode = None

        print("[MEDITATE] 🧘 Enhanced Meditate initialized")
        print("[MEDITATE] Breathing pattern controlled by Button B (Mode 1-4)")
        print("[MEDITATE] Adaptive: %s, Ultra-dim: %s" % (
            "ON" if self.adaptive_timing else "OFF",
            "ON" if self.ultra_dim else "OFF"
        ))

    @staticmethod
    def _load_adaptive_timing():
        """Load adaptive timing preference from config."""
        try:
            from config_manager import ConfigManager
            config_mgr = ConfigManager()
            config = config_mgr.load_config()
            return config.get('meditate_adaptive_timing', True)
        except:
            return True  # Default enabled

    def run(self, mode, volume):
        """Run the enhanced 'meditate' routine - completely silent and non-reactive."""
        current_time = time.monotonic()

        # Control update frequency for a smooth meditation experience
        if current_time - self.last_update < self.update_delay:
            return

        self.last_update = current_time
        color_func = self.get_color_function(mode)

        # Use mode value as the breathing pattern (1-4) to select breathing pattern
        # Volume is ignored - meditation is always silent
        self._breathing_pattern(color_func, pattern_mode=mode)

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

    def _breathing_pattern(self, color_func, pattern_mode):
        """Enhanced breathing pattern with multiple techniques."""
        current_time = time.monotonic()

        # Use pattern_mode (which is mode 1-4) to select a breathing pattern
        pattern = self.breath_patterns[pattern_mode]
        timing_multiplier = self._calculate_adaptive_timing()

        # Calculate total cycle time with adaptive timing
        total_cycle_time = (pattern["inhale"] + pattern["hold1"] +
                            pattern["exhale"] + pattern["hold2"]) * timing_multiplier

        # Calculate cycle position (0 to 1)
        cycle_position = ((
                                  current_time - self.start_time) % total_cycle_time) / total_cycle_time

        # Calculate phase boundaries
        inhale_duration = pattern["inhale"] * timing_multiplier
        hold1_duration = pattern["hold1"] * timing_multiplier
        exhale_duration = pattern["exhale"] * timing_multiplier

        inhale_end = inhale_duration / total_cycle_time
        hold1_end = (inhale_duration + hold1_duration) / total_cycle_time
        exhale_end = (
                             inhale_duration + hold1_duration + exhale_duration) / total_cycle_time
        # hold2 is the remainder

        # Determine current phase and intensity
        if cycle_position < inhale_end:
            # Inhale phase - gradual increase from 0 to 255
            current_phase = "inhale"
            phase_progress = cycle_position / inhale_end
            intensity = int(255 * phase_progress)

        elif cycle_position < hold1_end:
            # First hold phase - maintain full brightness
            current_phase = "hold1"
            intensity = 255

        elif cycle_position < exhale_end:
            # Exhale phase - gradual decrease from 255 to minimum
            current_phase = "exhale"
            phase_progress = (cycle_position - hold1_end) / (exhale_end - hold1_end)
            # Start from full brightness and fade to a gentle minimum (not 0)
            intensity = int(
                255 * (1 - phase_progress * 0.9))  # Only fade to 10% instead of 0
            intensity = max(25, intensity)  # Ensure minimum visibility

        else:
            # Second hold phase (if exists) - very dim but visible
            current_phase = "hold2"
            intensity = 30

        # Update display with pattern-specific visualization
        self._update_meditation_display(color_func, intensity, current_phase, pattern)

        # Print breathing pattern at start of each breath cycle or when a pattern changes
        if current_phase != self.last_phase:
            if current_phase == "inhale" or pattern_mode != self.last_pattern_mode:
                print("[MEDITATE] 🫁 %s" % pattern["name"])
                self.last_pattern_mode = pattern_mode
            self.last_phase = current_phase

    def _update_meditation_display(self, color_func, intensity, phase, pattern):
        """Enhanced meditation display with pattern-specific visuals - optimized for performance."""
        # Only update if intensity changed significantly (reduces flicker and improves performance)
        if abs(intensity - self.last_intensity) < 5 and phase == self.last_phase:
            return

        self.last_intensity = intensity

        # Set ultra-low brightness once instead of every update
        if self.hardware.pixels.brightness != 0.05:
            self.hardware.pixels.brightness = 0.05

        # Clear pixels directly on hardware
        self.hardware.clear_pixels()

        if phase == "inhale":
            self._show_expansion_pattern(color_func, intensity, pattern)
        elif phase in ["hold1", "hold2"]:
            self._show_hold_pattern(color_func, intensity, phase)
        else:  # exhale
            # Use the same expansion pattern as inhale for a smooth reverse effect
            self._show_expansion_pattern(color_func, intensity, pattern)

        # Show the pixels
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
        """Show a steady pattern during hold phases."""
        if phase == "hold2":
            # Second hold - very minimal presence
            center_pixels = [4, 5]
            for pos in center_pixels:
                self.hardware.pixels[pos] = color_func(intensity)
        else:
            # First hold - full steady presence
            for i in range(10):
                self.hardware.pixels[i] = color_func(intensity)
