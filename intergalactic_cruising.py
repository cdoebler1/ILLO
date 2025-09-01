# Charles Doebler at Feral Cat AI
# Intergalactic Cruising - Pure audio visualization routine with ambient brightness and Bluetooth control

from base_routine import BaseRoutine
from audio_processor import AudioProcessor
from bluetooth_controller import BluefruitController
import time


class IntergalacticCruising(BaseRoutine):
    def __init__(self):
        super().__init__()
        self.audio = AudioProcessor()
        self.last_update = time.monotonic()
        self.rotation_offset = 0

        # Debug flag - can be enabled via config
        self.debug = False
        self.debug_counter = 0  # Counter for periodic debug messages
        self._last_bt_mode = None  # Track last Bluetooth mode for change detection

        # Read configuration for Bluetooth setup
        try:
            from config_manager import ConfigManager
            config_mgr = ConfigManager()
            config = config_mgr.load_config()
            device_name = config.get('name', 'UFO_CRUISER')
            bluetooth_config_enabled = config.get('bluetooth_enabled', True)
        except Exception as e:
            print("[CRUISER] Config read error: %s, using defaults" % str(e))
            device_name = 'UFO_CRUISER'
            bluetooth_config_enabled = True
        
        # Only initialize Bluetooth if enabled in config
        if bluetooth_config_enabled:
            # NEW: Bluetooth controller for Bluefruit Connect app
            self.bluetooth = BluefruitController(debug=False)  # Debug disabled by default
            
            # Set the device name after initialization
            if hasattr(self.bluetooth, 'ble') and self.bluetooth.ble:
                self.bluetooth.ble.name = device_name
                if hasattr(self.bluetooth, 'advertisement'):
                    self.bluetooth.advertisement.complete_name = device_name
                    print("[CRUISER] Set Bluetooth name to: %s" % device_name)
            
            print("[CRUISER] Bluetooth available (enabled in config)")
        else:
            self.bluetooth = None
            print("[CRUISER] Bluetooth disabled in config - improved performance mode")
        
        self.bluetooth_enabled = False

        print("[CRUISER] Intergalactic Cruising initialized - Audio visualization")
        print("[CRUISER] Device name: %s" % device_name)

    def run(self, mode, volume):
        """Run the intergalactic cruising routine with optional Bluetooth control."""
        # Determine effective mode (could be overridden by Bluetooth)
        effective_mode = mode
        
        # Increment debug counter
        self.debug_counter += 1
        
        # Manage Bluetooth advertising lifecycle (only if Bluetooth is available)
        if self.bluetooth_enabled and self.bluetooth:
            # Add detailed UART service debugging
            if self.debug_counter % 50 == 0:  # Every ~2.5 seconds
                bt_status = "Disconnected"
                uart_status = "No UART"
                
                if self.bluetooth.ble and self.bluetooth.ble.connected:
                    bt_status = "Connected (%d)" % len(self.bluetooth.ble.connections)
                    
                if self.bluetooth.connection and self.bluetooth.uart_service:
                    try:
                        # Test if UART service is actually working
                        in_waiting = self.bluetooth.uart_service.in_waiting
                        uart_status = "UART OK (waiting: %d)" % in_waiting
                    except Exception as e:
                        uart_status = "UART Error: %s" % str(e)
                
                if self.debug:
                    print("[CRUISER] BT: %s, UART: %s" % (bt_status, uart_status))
            
            # Debug: Show connection status periodically (every 100 cycles ≈ 5 seconds)
            if self.debug and self.debug_counter % 100 == 0:
                status = self.bluetooth.get_connection_status() if hasattr(self.bluetooth, 'get_connection_status') else "Unknown"
                print("[CRUISER] Bluetooth status: %s" % status)
            
            # Check for disconnections and manage advertising
            old_connected = self.bluetooth.is_connected()
            self.bluetooth.manage_advertising()
            self.bluetooth.check_connection()
            new_connected = self.bluetooth.is_connected()
            
            # Only show connection changes, not every check
            if old_connected != new_connected:
                if self.debug:
                    print("[CRUISER] Connection changed: %s -> %s" % (old_connected, new_connected))
            
            # Handle disconnection
            if old_connected and not new_connected:
                self.bluetooth.handle_disconnection()
            
            # Process commands if connected
            if new_connected:
                self.bluetooth.process_commands()
                
                # Check for mode override from Bluetooth
                bt_mode = self.bluetooth.get_mode_override()
                if bt_mode is not None:
                    effective_mode = bt_mode
                    # Only show mode override when it changes
                    if self.debug and hasattr(self, '_last_bt_mode') and self._last_bt_mode != bt_mode:
                        print("[CRUISER] Bluetooth mode override changed: %d" % effective_mode)
                    self._last_bt_mode = bt_mode
        elif self.bluetooth_enabled and not self.bluetooth:
            print("[CRUISER] Bluetooth requested but not available")
            self.bluetooth_enabled = False

        # Use inherited method for color function selection
        color_func = self.get_color_function(effective_mode)

        # Reduced debug frequency - only every 50 cycles
        if self.debug and self.debug_counter % 50 == 0:
            print("[CRUISER] Running with mode: %d, volume: %s" % (effective_mode, volume))

        # Process audio and update display
        np_samples = self.audio.record_samples()
        deltas = self.audio.compute_deltas(np_samples)

        # Less frequent audio debug
        if self.debug and len(np_samples) > 0 and self.debug_counter % 200 == 0:
            print("[CRUISER] Audio samples: %d, Deltas: %d" % (len(np_samples), len(deltas)))

        self._update_visualization(deltas, color_func, volume)

    def _update_visualization(self, deltas, color_func, volume):
        """Audio visualization with rotation, persistence effects, and Bluetooth enhancements."""
        freq = self.audio.calculate_frequency(deltas)

        # Check for manual beat trigger from Bluetooth
        manual_beat = False
        if self.bluetooth_enabled:
            manual_beat = self.bluetooth.check_manual_beat()
            if manual_beat:
                print("[CRUISER] 📱 Bluetooth beat trigger!")  # Keep this - it's important

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
                    pixel_color = tuple(int(c * intensity_factor) for c in color_override)
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
            print("[CRUISER] Frame complete - rotation offset: %.2f" % self.rotation_offset)

    def enable_bluetooth(self):
        """Enable Bluetooth functionality."""
        self.bluetooth_enabled = True
        if self.debug:
            print("[CRUISER] Bluetooth enabled")
        
        # Force start advertising when enabled
        if self.bluetooth.start_advertising():
            print("[CRUISER] 📱 Started advertising - look for device in Bluefruit Connect")
        else:
            print("[CRUISER] ❌ Failed to start advertising")

    def enable_debug(self):
        """Enable debug output for this routine and Bluetooth."""
        self.debug = True
        if self.bluetooth:
            self.bluetooth.enable_debug()
        print("[CRUISER] Debug mode enabled")

    def disable_debug(self):
        """Disable debug output for this routine and Bluetooth."""
        self.debug = False
        if self.bluetooth:
            self.bluetooth.disable_debug()
        print("[CRUISER] Debug mode disabled")

    def disable_bluetooth_debug(self):
        """Disable only Bluetooth debug output, keep routine debug as-is."""
        if self.bluetooth:
            self.bluetooth.disable_debug()
        print("[CRUISER] Bluetooth debug disabled")

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

        # Much less frequent idle debug
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

    def check_advertising_status(self):
        """Check if the device is currently advertising."""
        if self.bluetooth and self.bluetooth.ble:
            is_advertising = self.bluetooth.ble.advertising
            device_name = self.bluetooth.ble.name
            print("[CRUISER] Advertising: %s, Device name: '%s'" % (is_advertising, device_name))
            return is_advertising
        return False

    def save_bluetooth_mode_to_config(self):
        """Optional: Save current Bluetooth mode override to config."""
        try:
            if self.bluetooth.bluetooth_mode_override is not None:
                from config_manager import ConfigManager
                config_mgr = ConfigManager()
                config = config_mgr.load_config()
                config['mode'] = self.bluetooth.bluetooth_mode_override
                config_mgr.save_config(config)
                print("[CRUISER] Saved mode %d to config" % self.bluetooth.bluetooth_mode_override)
        except Exception as e:
            print("[CRUISER] Could not save mode to config: %s" % str(e))
