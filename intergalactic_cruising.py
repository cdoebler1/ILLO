# Charles Doebler at Feral Cat AI
# Intergalactic Cruising - Pure audio visualization routine with ambient brightness and Bluetooth control

from base_routine import BaseRoutine
from audio_processor import AudioProcessor
import time


class IntergalacticCruising(BaseRoutine):
    def __init__(self):
        super().__init__()
        self.audio = AudioProcessor()
        self.last_update = time.monotonic()
        self.rotation_offset = 0

        # Debug flag - can be enabled via config
        # Debug flag - can be enabled via config or external call
        self.debug = False
        self.debug_counter = 0
        self._last_bt_mode = None

        # Simplified Bluetooth state tracking
        self.bluetooth = None
        self.bluetooth_enabled = False

        # Read configuration for Bluetooth setup
        device_name, bluetooth_config_enabled = self._load_configuration()

        # Initialize Bluetooth if enabled in config
        if bluetooth_config_enabled:
            self._initialize_bluetooth(device_name)

        print("[CRUISER] Intergalactic Cruising initialized - Audio visualization")
        if self.debug:  # Only show device name in debug mode
            print("[CRUISER] Device name: %s" % device_name)

    def _load_configuration(self):
        """Load configuration with proper error handling."""
        try:
            from config_manager import ConfigManager
            config_mgr = ConfigManager()
            config = config_mgr.load_config()
            device_name = config.get('name', 'UFO_CRUISER')
            bluetooth_config_enabled = config.get('bluetooth_enabled', True)
            return device_name, bluetooth_config_enabled
        except Exception as e:
            print("[CRUISER] Config read error: %s, using defaults" % str(e))
            return 'UFO_CRUISER', True

    def _initialize_bluetooth(self, device_name):
        """Initialize Bluetooth with simplified error handling."""
        try:
            from bluetooth_controller import BluefruitController
            self.bluetooth = BluefruitController(debug=False)

            # Validate basic initialization
            if self.bluetooth and hasattr(self.bluetooth, 'ble') and self.bluetooth.ble:
                # Set device name
                self.bluetooth.ble.name = device_name
                if hasattr(self.bluetooth, 'advertisement'):
                    self.bluetooth.advertisement.complete_name = device_name
                print("[CRUISER] Bluetooth available: %s" % device_name)
                return True
            else:
                print("[CRUISER] Bluetooth initialization incomplete")
                self.bluetooth = None
                return False

        except ImportError:
            print("[CRUISER] Bluetooth controller not available")
            self.bluetooth = None
            return False
        except Exception as e:
            print("[CRUISER] Bluetooth initialization failed: %s" % str(e))
            self.bluetooth = None
            return False

    def is_bluetooth_available(self):
        """Check if Bluetooth is available."""
        return (self.bluetooth is not None and
                hasattr(self.bluetooth, 'ble') and
                self.bluetooth.ble is not None)

    def run(self, mode, volume):
        """Run the intergalactic cruising routine with optional Bluetooth control."""
        # Determine effective mode (could be overridden by Bluetooth)
        effective_mode = mode

        # Increment debug counter
        self.debug_counter += 1

        # Manage Bluetooth if available and enabled
        if self.bluetooth_enabled and self.is_bluetooth_available():
            try:
                self._manage_bluetooth_interaction()

                # Check for mode override from Bluetooth
                bt_mode = self.bluetooth.get_mode_override()
                if bt_mode is not None:
                    effective_mode = bt_mode
                    # Only show mode override when it changes
                    if self._last_bt_mode != bt_mode:
                        if self.debug:
                            print(
                                "[CRUISER] Bluetooth mode override changed: %d" % effective_mode)
                        self._last_bt_mode = bt_mode

            except Exception as bt_error:
                if self.debug:
                    print("[CRUISER] Bluetooth management error: %s" % str(bt_error))
                # Don't disable Bluetooth entirely, just skip this cycle

        elif self.bluetooth_enabled and not self.is_bluetooth_available():
            if self.debug and self.debug_counter % 1000 == 0:  # Very infrequent warning
                print("[CRUISER] Bluetooth requested but not available")

        # Core audio visualization processing
        self._process_audio_visualization(effective_mode, volume)

    def _manage_bluetooth_interaction(self):
        """Centralized Bluetooth interaction management."""
        # Connection management
        old_connected = self.bluetooth.is_connected()
        self.bluetooth.manage_advertising()
        self.bluetooth.check_connection()
        new_connected = self.bluetooth.is_connected()

        # Handle connection state changes
        if old_connected != new_connected:
            if old_connected and not new_connected:
                self.bluetooth.handle_disconnection()

        # Process commands if connected
        if new_connected:
            self.bluetooth.process_commands()

    def _process_audio_visualization(self, effective_mode, volume):
        """Centralized audio processing and visualization."""
        # Use inherited method for color function selection
        color_func = self.get_color_function(effective_mode)

        # Process audio and update display
        np_samples = self.audio.record_samples()
        deltas = self.audio.compute_deltas(np_samples)

        self._update_visualization(deltas, color_func, volume)

    def _update_visualization(self, deltas, color_func, volume):
        """Audio visualization with rotation, persistence effects, and Bluetooth enhancements."""
        freq = self.audio.calculate_frequency(deltas)

        # Check for manual beat trigger from Bluetooth
        manual_beat = False
        if self.bluetooth_enabled:
            manual_beat = self.bluetooth.check_manual_beat()
            if manual_beat:
                print(
                    "[CRUISER] 📱 Bluetooth beat trigger!")  # Keep this - it's important

        # Reduced debug frequency for visualization details
        if self.debug and self.debug_counter % 100 == 0:
            print("[CRUISER] Freq: %s, Manual beat: %s" % (str(freq), manual_beat))

        if freq is None and not manual_beat:
            # No audio detected and no manual trigger - show gentle rotation
            if self.debug and self.debug_counter % 500 == 0:  # Very infrequent
                print("[CRUISER] No frequency detected - idle animation")
            self._idle_animation(color_func)
            return

        # Get Bluetooth modifiers (no debug spam)
        rotation_speed_mod = 1.0
        effect_modifier = "normal"
        brightness_override = None
        color_override = None

        if self.bluetooth_enabled:
            rotation_speed_mod = self.bluetooth.get_rotation_speed_modifier()
            effect_modifier = self.bluetooth.get_effect_modifier()
            brightness_override = self.bluetooth.get_brightness_override()
            color_override = self.bluetooth.get_color_override()

        # Use manual beat or calculated frequency
        display_freq = freq if freq is not None else 440  # Default frequency for manual beats

        # Audio-reactive mode with enhanced effects
        pixel_data = self.hardware.map_deltas_to_pixels(deltas) if deltas else [50] * 10

        # Much less frequent pixel debug
        if self.debug and self.debug_counter % 200 == 0:
            print("[CRUISER] Pixel data sample: %s..." % str(pixel_data[:3]))

        # Add rotation effect with Bluetooth speed modifier
        current_time = time.monotonic()
        time_delta = current_time - self.last_update

        rotation_increment = display_freq * time_delta * 0.01 * rotation_speed_mod
        self.rotation_offset = (self.rotation_offset + rotation_increment) % 10

        # Less frequent rotation debug
        if self.debug and self.debug_counter % 150 == 0:
            print("[CRUISER] Rotation: %.2f (freq: %.1f, speed: %.1fx)" %
                  (self.rotation_offset, display_freq, rotation_speed_mod))

        # Clear pixels before applying new pattern
        self.hardware.clear_pixels()

        # Apply rotation and intensity mapping with effect modifiers
        intensity_multiplier = 3
        intensity_threshold = 40

        if effect_modifier == "enhanced":
            intensity_multiplier = 5
            intensity_threshold = 30
        elif effect_modifier == "gentle":
            intensity_multiplier = 2
            intensity_threshold = 60

        lit_pixels = 0
        for ii in range(10):
            rotated_index = int((ii + self.rotation_offset) % 10)
            base_intensity = min(200, pixel_data[ii] * intensity_multiplier)

            # Apply brightness override
            if brightness_override is not None:
                base_intensity = int(base_intensity * brightness_override)

            if base_intensity > intensity_threshold or manual_beat:
                # Use color override or normal color function
                if color_override is not None:
                    # Scale custom color by intensity
                    intensity_factor = min(1.0, base_intensity / 200.0)
                    pixel_color = tuple(
                        int(c * intensity_factor) for c in color_override)
                    self.hardware.pixels[rotated_index] = pixel_color
                else:
                    self.hardware.pixels[rotated_index] = color_func(base_intensity)

                lit_pixels += 1

        # Much less frequent pixel detail debug
        if self.debug and self.debug_counter % 300 == 0:
            print("[CRUISER] Lit %d pixels out of 10" % lit_pixels)

        self.hardware.pixels.show()
        self.hardware.play_tone_if_enabled(display_freq, 0.05, volume)

        # Fade effect with effect modifier consideration
        fade_factor = 0.8
        if effect_modifier == "enhanced":
            fade_factor = 0.9  # Slower fade for more persistence
        elif effect_modifier == "gentle":
            fade_factor = 0.6  # Faster fade for gentler effect

        time.sleep(0.05)
        for ii in range(10):
            current_color = self.hardware.pixels[ii]
            if current_color != (0, 0, 0):
                faded_color = tuple(int(c * fade_factor) for c in current_color)
                self.hardware.pixels[ii] = faded_color

        self.last_update = current_time

        # Very infrequent frame completion debug
        if self.debug and self.debug_counter % 500 == 0:
            print(
                "[CRUISER] Frame complete - rotation offset: %.2f" % self.rotation_offset)

    def enable_bluetooth(self):
        """Enable Bluetooth functionality with better error handling."""
        if not self.is_bluetooth_available():
            return False

        self.bluetooth_enabled = True

        try:
            # Force start advertising when enabled
            if self.bluetooth.start_advertising():
                return True
            else:
                return False
        except Exception as e:
            if self.debug:
                print("[CRUISER] ❌ Error starting advertising: %s" % str(e))
            return False

    def disable_bluetooth(self):
        """Disable Bluetooth functionality."""
        self.bluetooth_enabled = False

        if self.is_bluetooth_available():
            try:
                if hasattr(self.bluetooth, 'ble') and self.bluetooth.ble.advertising:
                    self.bluetooth.ble.stop_advertising()
                    print("[CRUISER] Bluetooth advertising stopped")
            except Exception as e:
                if self.debug:
                    print("[CRUISER] Error stopping Bluetooth: %s" % str(e))

    def enable_debug(self):
        """Enable debug output for this routine and Bluetooth."""
        self.debug = True
        if self.is_bluetooth_available():
            self.bluetooth.enable_debug()
        print("[CRUISER] Debug mode enabled")

    def disable_debug(self):
        """Disable debug output for this routine and Bluetooth."""
        self.debug = False
        if self.is_bluetooth_available():
            self.bluetooth.disable_debug()
        print("[CRUISER] Debug mode disabled")

    def disable_bluetooth_debug(self):
        """Disable only Bluetooth debug output, keep routine debug as-is."""
        if self.bluetooth:
            self.bluetooth.disable_debug()
        print("[CRUISER] Bluetooth debug disabled")

    # ... existing code ...

    def test_uart_service(self):
        """Test if UART service is working by sending a test message."""
        if self.bluetooth_enabled and self.bluetooth.connection and self.bluetooth.uart_service:
            try:
                test_msg = "UART Test: %d\n" % time.monotonic()
                self.bluetooth.uart_service.write(test_msg.encode('utf-8'))
                print("[CRUISER] UART test message sent: %s" % test_msg.strip())
                return True
            except Exception as e:
                print("[CRUISER] UART test failed: %s" % str(e))
                return False
        else:
            print("[CRUISER] UART test skipped - not connected")
            return False

    def _idle_animation(self, color_func):
        """Gentle rotating animation when no audio detected, with Bluetooth color override."""
        current_time = time.monotonic()

        if self.debug and self.debug_counter % 1000 == 0:
            print("[CRUISER] Idle animation active")

        if current_time - self.last_update > 0.15:
            # Apply rotation speed modifier to idle animation too
            speed_mod = 1.0
            if self.bluetooth_enabled:
                speed_mod = self.bluetooth.get_rotation_speed_modifier()

            self.rotation_offset = (self.rotation_offset + (1 * speed_mod)) % 10

            # Clear all pixels first
            self.hardware.clear_pixels()

            # Create a rotating comet effect
            main_pos = int(self.rotation_offset)
            trail1_pos = (main_pos - 1) % 10
            trail2_pos = (main_pos - 2) % 10

            # Check for Bluetooth color override
            color_override = None
            brightness_override = None
            if self.bluetooth_enabled:
                color_override = self.bluetooth.get_color_override()
                brightness_override = self.bluetooth.get_brightness_override()

            if color_override is not None:
                # Use custom color for comet
                main_color = color_override
                trail1_color = tuple(int(c * 0.6) for c in color_override)
                trail2_color = tuple(int(c * 0.3) for c in color_override)
            else:
                # Use color function
                main_color = color_func(120)
                trail1_color = color_func(80)
                trail2_color = color_func(50)

            # Apply brightness override if set
            if brightness_override is not None:
                main_color = tuple(int(c * brightness_override) for c in main_color)
                trail1_color = tuple(int(c * brightness_override) for c in trail1_color)
                trail2_color = tuple(int(c * brightness_override) for c in trail2_color)

            self.hardware.pixels[main_pos] = main_color
            self.hardware.pixels[trail1_pos] = trail1_color
            self.hardware.pixels[trail2_pos] = trail2_color

            self.hardware.pixels.show()
            self.last_update = current_time

    def get_status(self):
        """Get basic status information."""
        status = {
            'bluetooth_available': self.is_bluetooth_available(),
            'bluetooth_enabled': self.bluetooth_enabled,
            'debug_enabled': self.debug
        }

        if self.is_bluetooth_available():
            try:
                bt_info = self.bluetooth.get_connection_info()
                status.update({
                    'bluetooth_connected': bt_info.get('connected', False),
                    'bluetooth_advertising': bt_info.get('advertising', False)
                })
            except Exception:
                status['bluetooth_status'] = 'error'

        return status

    def cleanup(self):
        """Clean up Intergalactic Cruising resources."""
        try:
            if self.bluetooth and hasattr(self.bluetooth, 'cleanup'):
                self.bluetooth.cleanup()

            # Clear references
            self.bluetooth = None
            self.audio = None

            print("[CRUISER] Cleanup completed")

        except Exception as e:
            print("[CRUISER] Cleanup error: %s" % str(e))
