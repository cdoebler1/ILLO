# Charles Doebler at Feral Cat AI
# Multi-UFO Synchronized Dance Party - Leader/Follower with Bluetooth Control

from base_routine import BaseRoutine
from audio_processor import AudioProcessor
import time
import gc


class DanceParty(BaseRoutine):
    def __init__(self, device_name, debug_bluetooth=False, debug_audio=False):
        super().__init__()
        self.audio = AudioProcessor()
        self.device_name = device_name
        self.debug_bluetooth = debug_bluetooth
        self.debug_audio = debug_audio
        self.last_update = time.monotonic()
        self.rotation_offset = 0

        # Debug flag and counter
        self.debug = debug_bluetooth
        self.debug_counter = 0
        self._last_bt_mode = None

        # Simplified - no Bluetooth initialization for focus mode
        self.bluetooth = None
        self.bluetooth_enabled = False

        # Beat detection parameters - more sensitive for dance
        self.last_beat_time = 0
        self.beat_pattern_state = 0
        self.energy_threshold = 600  # Lowered from 800 for more sensitivity

        # Dance timing
        self.last_pattern_update = time.monotonic()

        # Multi-UFO sync state
        self.is_leader = False  # Default to follower mode
        self.pending_beat_sync = False

        print("[DANCE] 🎵 Dance Party initialized - Beat Detection Mode")
        print("[DANCE] Bluetooth: Disabled (Focus Mode)")

    def _initialize_bluetooth(self, device_name, bluetooth_config_enabled):
        """Initialize Bluetooth with robust error handling like Intergalactic Cruising."""
        print("[DANCE] _initialize_bluetooth() called")
        print("[DANCE] Parameters - device_name: %s, config_enabled: %s" % (device_name,
                                                                            bluetooth_config_enabled))

        self._bluetooth_init_attempted = True

        if not bluetooth_config_enabled:
            self.bluetooth = None
            print("[DANCE] Bluetooth disabled in config - standalone mode")
            return

        print("[DANCE] Bluetooth enabled in config, proceeding with initialization...")

        try:
            print("[DANCE] Importing BluefruitController...")
            from bluetooth_controller import BluefruitController
            print("[DANCE] BluefruitController imported successfully")

            # Initialize Bluetooth controller - SIMPLIFIED LIKE INTERGALACTIC CRUISING
            print("[DANCE] Creating BluefruitController instance...")
            self.bluetooth = BluefruitController(debug=self.debug_bluetooth)
            print("[DANCE] BluefruitController created: %s" % str(self.bluetooth))

            # Simple validation - just check if we have a BLE radio like Intergalactic Cruising
            if not self.bluetooth or not self.bluetooth.ble:
                print("[DANCE] ❌ Bluetooth controller failed to initialize")
                self.bluetooth = None
                return

            print("[DANCE] ✅ Bluetooth controller validation passed")

            # Set device name for dance party - SIMPLIFIED
            print("[DANCE] Setting device name...")
            final_name = device_name + "_DANCE"
            try:
                print("[DANCE] Setting BLE name to: %s" % final_name)
                self.bluetooth.ble.name = final_name

                # Set advertisement name - but don't fail if this doesn't work
                if hasattr(self.bluetooth,
                           'advertisement') and self.bluetooth.advertisement:
                    print("[DANCE] Setting advertisement name to: %s" % final_name)
                    self.bluetooth.advertisement.complete_name = final_name
                    print("[DANCE] ✅ Set Bluetooth name to: %s" % final_name)
                else:
                    print(
                        "[DANCE] ⚠️ No advertisement object found, using default name")
            except Exception as name_error:
                print("[DANCE] ⚠️ Could not set device name: %s" % str(name_error))
                print("[DANCE] ⚠️ Continuing with default name...")

            print("[DANCE] Bluetooth initialization successful!")
            self._bluetooth_init_success = True
            print("[DANCE] 📱 Bluetooth available for multi-UFO sync")

        except ImportError as ie:
            print(
                "[DANCE] ❌ Import error - Bluetooth controller not available: %s" % str(
                    ie))
            self.bluetooth = None
        except Exception as e:
            print("[DANCE] ❌ Bluetooth initialization failed: %s" % str(e))
            print("[DANCE] Error type: %s" % type(e).__name__)
            self.bluetooth = None

    def enable_bluetooth(self):
        """Enable Bluetooth functionality."""
        print("[DANCE] enable_bluetooth() called")
        print("[DANCE] is_bluetooth_available(): %s" % self.is_bluetooth_available())

        if not self.is_bluetooth_available():
            print("[DANCE] ❌ Bluetooth not available, cannot enable")
            return False

        self.bluetooth_enabled = True
        print("[DANCE] bluetooth_enabled set to True")

        try:
            print("[DANCE] Starting advertising...")
            if self.bluetooth.start_advertising():
                print("[DANCE] ✅ Advertising started successfully")
                print("[DANCE] 📡 Multi-UFO sync enabled - ready for followers!")
                return True
            else:
                print("[DANCE] ❌ start_advertising() returned False")
                return False
        except Exception as e:
            print("[DANCE] ❌ Error starting advertising: %s" % str(e))
            return False

    def is_bluetooth_available(self):
        """Check if Bluetooth is available and properly initialized."""
        return (self._bluetooth_init_success and
                self.bluetooth is not None and
                hasattr(self.bluetooth, 'ble') and
                self.bluetooth.ble is not None)

    def run(self, mode, volume):
        """Run the dance party with full audio visualization and environmental dimming."""
        # Determine effective mode (could be overridden by Bluetooth if enabled)
        effective_mode = mode

        # Increment debug counter
        self.debug_counter += 1

        # Basic run loop debug - every 100 cycles
        if self.debug_counter % 100 == 0:
            print("[DANCE] 🔄 Run loop cycle %d (bluetooth_enabled: %s)" % (
                self.debug_counter, self.bluetooth_enabled))

        # Force garbage collection periodically to manage memory
        if self.debug_counter % 100 == 0:
            gc.collect()

        # Only manage Bluetooth if explicitly enabled (skip when disabled for focus)
        if self.bluetooth_enabled and self.is_bluetooth_available():
            try:
                self._manage_bluetooth_interaction()
                # Check for mode override from Bluetooth
                bt_mode = self.bluetooth.get_mode_override()
                if bt_mode is not None:
                    effective_mode = bt_mode
                    if self._last_bt_mode != bt_mode:
                        if self.debug:
                            print(
                                "[DANCE] Bluetooth mode override changed: %d" % effective_mode)
                        self._last_bt_mode = bt_mode
            except Exception as bt_error:
                print("[DANCE] ❌ Bluetooth management error: %s" % str(bt_error))

        # Core dance processing - full audio visualization like Intergalactic Cruising
        try:
            self._process_beat_focused_dance(effective_mode, volume)
        except Exception as e:
            print("[DANCE] ❌ Dance processing error: %s" % str(e))

    def _manage_bluetooth_interaction(self):
        """Manage Bluetooth connections - simplified for focus mode."""
        # Since we're in focus mode, just skip all Bluetooth management
        if not self.bluetooth_enabled or not self.is_bluetooth_available():
            return

        # Only basic connection management if Bluetooth is somehow enabled
        try:
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

                # Check for dance-specific sync commands - REMOVED
                # Multi-UFO sync features planned for future builds
                pass

        except Exception as bt_error:
            print("[DANCE] ❌ Bluetooth management error: %s" % str(bt_error))

    def _process_synchronized_dance(self, effective_mode, volume):
        """Process dance with audio analysis and multi-UFO synchronization."""
        color_func = self.get_color_function(effective_mode)

        # Get audio samples for beat detection
        try:
            np_samples = self.audio.record_samples()
            deltas = self.audio.compute_deltas(np_samples)

            # Dance-optimized beat detection
            beat_detected = self._dance_beat_detection(np_samples)
            manual_beat = False

            # Check for manual beat trigger from Bluetooth (like Intergalactic Cruising)
            if self.bluetooth_enabled and self.is_bluetooth_available():
                manual_beat = self.bluetooth.check_manual_beat()
                if manual_beat:
                    print("[DANCE] 📱 Bluetooth beat trigger!")
                    beat_detected = True

            # If this is the leader and we detected a beat, queue sync command
            if self.is_leader and beat_detected and not manual_beat:
                self.pending_beat_sync = True
                self.beat_pattern_state = (
                                                  self.beat_pattern_state + 1) % 8  # 8 beat cycle

            self._update_dance_visualization(deltas, color_func, beat_detected, volume)

        except MemoryError:
            print("[DANCE] ❌ Memory error - switching to safe mode")
            self._safe_mode_pattern(color_func)
            gc.collect()

    def _dance_beat_detection(self, np_samples):
        """Enhanced beat detection optimized for dance synchronization."""
        if len(np_samples) < 50:
            return False

        current_time = time.monotonic()
        if current_time - self.last_beat_time < 0.2:  # Faster beats allowed for dancing
            return False

        try:
            # Energy calculation optimized for dance beats
            sample_count = min(len(np_samples), 300)
            total_energy = 0

            # Calculate mean
            sample_sum = sum(np_samples[i] for i in range(sample_count))
            mean_sample = sample_sum / sample_count

            # Calculate energy with dance-optimized weighting
            for i in range(sample_count):
                diff = np_samples[i] - mean_sample
                total_energy += diff * diff

            energy = (total_energy / sample_count) ** 0.5

            # Adaptive threshold based on recent energy levels
            beat_detected = energy > self.energy_threshold

            if self.debug_audio and self.debug_counter % 20 == 0:
                print("[DANCE] Energy: %.1f, Threshold: %.1f, Beat: %s" %
                      (energy, self.energy_threshold, beat_detected))

            if beat_detected:
                self.last_beat_time = current_time
                if self.debug_audio:
                    print("[DANCE] 🎵 DANCE BEAT! 🎵")
                return True

        except MemoryError:
            print("[DANCE] Beat detection memory error - using fallback")
            return False

        return False

    def _update_dance_visualization(self, deltas, color_func, beat_detected, volume):
        """Dance visualization with synchronized multi-UFO effects."""
        current_time = time.monotonic()

        # Get Bluetooth modifiers (similar to Intergalactic Cruising)
        rotation_speed_mod = 1.0
        effect_modifier = "normal"
        brightness_override = None
        color_override = None

        if self.bluetooth_enabled and self.is_bluetooth_available():
            rotation_speed_mod = self.bluetooth.get_rotation_speed_modifier()
            effect_modifier = self.bluetooth.get_effect_modifier()
            brightness_override = self.bluetooth.get_brightness_override()
            color_override = self.bluetooth.get_color_override()

        if beat_detected:
            # Beat response - synchronized flash across all UFOs
            self._display_beat_flash(color_func, volume)

        else:
            # Continuous dance pattern with rotation
            self._display_dance_pattern(deltas, color_func, rotation_speed_mod,
                                        effect_modifier, color_override,
                                        brightness_override)

        self.last_update = current_time

    def _display_dance_pattern(self, deltas, color_func, speed_mod, effect_mod,
                               color_override, brightness_override):
        """Display continuous dance pattern with audio-reactive rotation."""
        try:
            current_time = time.monotonic()
            time_delta = current_time - self.last_update

            # Audio-reactive rotation (similar to Intergalactic Cruising)
            pixel_data = self.hardware.map_deltas_to_pixels(
                deltas) if deltas else [30] * 10

            # Use average pixel intensity to drive rotation speed
            avg_intensity = sum(pixel_data) / len(pixel_data) if pixel_data else 50
            rotation_speed = max(0.5, avg_intensity * 0.01) * speed_mod

            self.rotation_offset = (
                                           self.rotation_offset + rotation_speed * time_delta * 5) % 10

            # Clear pixels
            self.hardware.clear_pixels()

            # Create dancing wave pattern with rotation
            wave_length = 3
            for i in range(wave_length):
                pos = int((self.rotation_offset + i * 2) % 10)

                # Audio-reactive intensity
                pixel_value = pixel_data[min(i, len(pixel_data) - 1)]
                base_intensity = min(200, int(pixel_value * 2))
                if effect_mod == "enhanced":
                    base_intensity = min(255, int(base_intensity * 1.5))
                elif effect_mod == "gentle":
                    base_intensity = int(base_intensity * 0.7)

                if base_intensity > 20:  # Lower threshold for continuous dance
                    if color_override is not None:
                        pixel_color = tuple(
                            int(c * (base_intensity / 255.0)) for c in color_override)
                    else:
                        pixel_color = color_func(base_intensity)

                    # Apply brightness override
                    if brightness_override is not None:
                        pixel_color = tuple(
                            int(c * brightness_override) for c in pixel_color)

                    self.hardware.pixels[pos] = pixel_color

            self.hardware.pixels.show()

        except MemoryError:
            print("[DANCE] Dance pattern memory error")
            self._safe_mode_pattern(color_func)

    def _safe_mode_pattern(self, color_func):
        """Ultra-simple pattern for when memory is critically low."""
        current_time = time.monotonic()

        # Single rotating pixel - minimal memory usage
        if current_time - self.last_pattern_update > 0.3:
            pos = int((current_time * 2) % 10)

            self.hardware.clear_pixels()
            self.hardware.pixels[pos] = color_func(100)
            self.hardware.pixels.show()

            self.last_pattern_update = current_time

            if self.debug:
                print("[DANCE] Safe mode - single pixel rotation")

    def disable_bluetooth(self):
        """Disable Bluetooth functionality."""
        self.bluetooth_enabled = False

        if self.is_bluetooth_available():
            try:
                if hasattr(self.bluetooth, 'ble') and self.bluetooth.ble.advertising:
                    self.bluetooth.ble.stop_advertising()
                    print("[DANCE] Bluetooth sync disabled")
            except Exception as e:
                if self.debug:
                    print("[DANCE] Error stopping Bluetooth: %s" % str(e))

    def set_as_leader(self):
        """Set this UFO as the dance leader."""
        self.is_leader = True
        print("[DANCE] 👑 This UFO is now the DANCE LEADER")

    def set_as_follower(self):
        """Set this UFO as a dance follower."""
        self.is_leader = False
        print("[DANCE] 💃 This UFO is now a DANCE FOLLOWER")

    def cleanup(self):
        """Clean up Dance Party resources."""
        try:
            print("[DANCE] 🧹 Cleaning up Dance Party...")

            if self.bluetooth:
                try:
                    if hasattr(self.bluetooth, 'cleanup'):
                        self.bluetooth.cleanup()
                    else:
                        if hasattr(self.bluetooth, 'ble') and self.bluetooth.ble:
                            if self.bluetooth.ble.advertising:
                                self.bluetooth.ble.stop_advertising()
                except Exception as bt_cleanup_error:
                    print("[DANCE] Bluetooth cleanup error: %s" % str(bt_cleanup_error))

            self.bluetooth = None
            self.audio = None

            print("[DANCE] ✅ Dance Party cleanup completed")

        except Exception as e:
            print("[DANCE] ❌ Cleanup error: %s" % str(e))

    def check_advertising_status(self):
        """Check if the device is currently advertising - runtime debug method."""
        if self.bluetooth and self.bluetooth.ble:
            try:
                is_advertising = self.bluetooth.ble.advertising
                device_name = self.bluetooth.ble.name
                print("[DANCE] 🔍 RUNTIME CHECK:")
                print("[DANCE]   Advertising: %s" % is_advertising)
                print("[DANCE]   Device name: '%s'" % device_name)
                print("[DANCE]   BLE object: %s" % str(self.bluetooth.ble))

                # Try to get connection info
                if hasattr(self.bluetooth, 'get_connection_info'):
                    conn_info = self.bluetooth.get_connection_info()
                    print("[DANCE]   Connection info: %s" % str(conn_info))

                return is_advertising
            except Exception as e:
                print("[DANCE] ❌ Error checking advertising status: %s" % str(e))
                return False
        else:
            print("[DANCE] ❌ No bluetooth or BLE object available")
            return False

    def get_status(self):
        """Get detailed status information for debugging."""
        status = {
            'bluetooth_init_attempted': self._bluetooth_init_attempted,
            'bluetooth_init_success': self._bluetooth_init_success,
            'bluetooth_available': self.is_bluetooth_available(),
            'bluetooth_enabled': self.bluetooth_enabled,
            'is_leader': self.is_leader,
            'beat_pattern_state': self.beat_pattern_state,
            'debug_enabled': self.debug
        }

        if self.is_bluetooth_available():
            try:
                bt_info = self.bluetooth.get_connection_info()
                status.update({
                    'bluetooth_connected': bt_info.get('connected', False),
                    'bluetooth_advertising': bt_info.get('advertising', False),
                    'connection_count': bt_info.get('connection_count', 0)
                })
            except Exception as e:
                if self.debug:
                    print("[DANCE] Error getting Bluetooth info: %s" % str(e))
                status['bluetooth_status'] = 'error_getting_info'

        return status

    def _process_beat_focused_dance(self, effective_mode, volume):
        """Process dance with full audio visualization like Intergalactic Cruising but more energetic."""
        color_func = self.get_color_function(effective_mode)

        # Use the same audio processing as Intergalactic Cruising for maximum reactivity
        try:
            np_samples = self.audio.record_samples()
            deltas = self.audio.compute_deltas(np_samples)
            
            # Environmental brightness control (like routine 2)
            self._apply_environmental_dimming()

            # Use the proven audio visualization from Intergalactic Cruising
            if len(deltas) > 0:
                self._dance_audio_visualization(deltas, color_func, volume)
            else:
                # Simple rotating pattern when no audio
                self._dance_idle_animation(color_func)

        except MemoryError:
            print("[DANCE] ❌ Memory error - switching to safe mode")
            self._safe_mode_pattern(color_func)
            gc.collect()

    def _dance_audio_visualization(self, deltas, color_func, volume):
        """Full audio visualization adapted from Intergalactic Cruising but more energetic for dancing."""
        current_time = time.monotonic()

        # Map audio deltas to pixels (same as Intergalactic Cruising)
        pixel_data = self.hardware.map_deltas_to_pixels(deltas)

        # Calculate frequency for rotation speed (same method as Cruising)
        try:
            freq = self.audio.calculate_frequency(deltas)
            if freq is not None:
                # Dance-optimized rotation - faster and more energetic
                rotation_speed = max(2.0, freq * 0.08)  # Faster than Cruising's 0.05
            else:
                rotation_speed = 3.0  # Higher default speed for dancing
        except:
            rotation_speed = 3.0

        # Update rotation offset
        time_delta = current_time - self.last_update
        self.rotation_offset = (self.rotation_offset + rotation_speed * time_delta) % 10

        # Clear pixels
        self.hardware.clear_pixels()

        # Enhanced visualization - more pixels active than Cruising
        active_pixel_count = min(8, max(3, len([p for p in pixel_data if p > 30])))  # More active pixels

        for i in range(active_pixel_count):
            # Calculate pixel position with rotation
            pos = int((self.rotation_offset + i * 1.2) % 10)  # Tighter spacing than Cruising
            
            # Get pixel intensity
            pixel_index = min(i, len(pixel_data) - 1)
            intensity = pixel_data[pixel_index]
            
            # Dance enhancement - boost intensity for more energy
            boosted_intensity = min(255, int(intensity * 1.5))  # 50% boost
            
            if boosted_intensity > 20:  # Lower threshold for more responsiveness
                # Get color
                pixel_color = color_func(boosted_intensity)
                
                # Dance special effect - add extra sparkle on high intensity
                if boosted_intensity > 180:
                    # Brighten high-energy pixels even more
                    pixel_color = tuple(min(255, int(c * 1.2)) for c in pixel_color)
                
                self.hardware.pixels[pos] = pixel_color

        # Beat emphasis - flash additional pixels on strong beats
        if len(pixel_data) > 0:
            max_intensity = max(pixel_data)
            if max_intensity > 150:  # Strong beat detected
                # Light up opposite pixels briefly for beat emphasis
                beat_positions = [(int(self.rotation_offset) + 5) % 10]
                beat_color = color_func(255)
                for beat_pos in beat_positions:
                    self.hardware.pixels[beat_pos] = beat_color
                    
                # Optional beat sound
                if volume:
                    self.hardware.play_tone_if_enabled(800, 0.05, volume)

        self.hardware.pixels.show()
        self.last_update = current_time

    def _dance_idle_animation(self, color_func):
        """Energetic idle animation when no audio - more active than Cruising."""
        current_time = time.monotonic()
        
        if current_time - self.last_pattern_update > 0.1:  # Faster updates than Cruising
            # Faster rotation for dance energy
            self.rotation_offset = (self.rotation_offset + 2.0) % 10  # Faster than Cruising's 1.0
            
            # Clear pixels
            self.hardware.clear_pixels()
            
            # Create a more energetic comet effect with multiple trails
            main_pos = int(self.rotation_offset)
            trail1_pos = (main_pos - 1) % 10
            trail2_pos = (main_pos - 2) % 10
            trail3_pos = (main_pos - 3) % 10
            
            # Brighter colors for dance energy
            main_color = color_func(200)  # Brighter than Cruising's 120
            trail1_color = color_func(140)  # Brighter than Cruising's 80
            trail2_color = color_func(80)   # Brighter than Cruising's 50
            trail3_color = color_func(40)   # Additional trail
            
            self.hardware.pixels[main_pos] = main_color
            self.hardware.pixels[trail1_pos] = trail1_color
            self.hardware.pixels[trail2_pos] = trail2_color
            self.hardware.pixels[trail3_pos] = trail3_color
            
            # Add some sparkle - occasionally light up random pixels
            if self.debug_counter % 20 == 0:  # Every 20 cycles
                sparkle_pos = (main_pos + 5) % 10  # Opposite side
                sparkle_color = color_func(100)
                self.hardware.pixels[sparkle_pos] = sparkle_color
            
            self.hardware.pixels.show()
            self.last_pattern_update = current_time

    def _apply_environmental_dimming(self):
        """Apply environmental brightness control similar to Intergalactic Cruising."""
        try:
            # Import light sensor functionality
            from adafruit_circuitplayground import cp

            current_light = cp.light

            # Map light sensor reading to brightness levels (similar to routine 2)
            if current_light < 30:  # Very dark
                target_brightness = 0.03  # Very dim but visible
            elif current_light < 60:  # Dark
                target_brightness = 0.06  # Dim
            elif current_light < 100:  # Indoor lighting
                target_brightness = 0.12  # Low-medium brightness
            elif current_light < 150:  # Bright indoor
                target_brightness = 0.18  # Medium brightness
            else:  # Daylight/very bright
                target_brightness = 0.25  # Maximum brightness

            # Smooth brightness transitions
            current_brightness = self.hardware.pixels.brightness
            if abs(target_brightness - current_brightness) > 0.01:
                if target_brightness > current_brightness:
                    new_brightness = target_brightness if target_brightness < current_brightness + 0.01 else current_brightness + 0.01
                else:
                    new_brightness = target_brightness if target_brightness > current_brightness - 0.01 else current_brightness - 0.01
                self.hardware.pixels.brightness = new_brightness

        except Exception as e:
            if self.debug_counter % 50 == 0:  # Don't spam errors
                print("[DANCE] Environmental dimming error: %s" % str(e))

    def _enhanced_dance_beat_detection(self, np_samples):
        """Enhanced beat detection optimized for dance with higher sensitivity."""
        if len(np_samples) < 50:
            return False

        current_time = time.monotonic()
        if current_time - self.last_beat_time < 0.12:  # Allow even faster beats (was 0.15)
            return False

        try:
            # Focus on recent samples for responsiveness - ensure integer values
            sample_count = min(len(np_samples), 250)  # Increased from 200 for more sensitivity
            total_energy = 0

            # Calculate mean
            sample_sum = sum(np_samples[i] for i in range(sample_count))
            mean_sample = sample_sum / sample_count

            # Calculate energy with dance-optimized weighting
            for i in range(sample_count):
                diff = np_samples[i] - mean_sample
                total_energy += diff * diff

            energy = (total_energy / sample_count) ** 0.5

            # More sensitive threshold than routine 2 - fix integer type issues
            beat_threshold = int(
                max(400, int(self.energy_threshold * 0.6)))  # Lowered multiplier from 0.7 to 0.6
            beat_detected = energy > beat_threshold

            # Adaptive threshold adjustment for dance - more responsive
            if beat_detected:
                self.energy_threshold = int(
                    min(1000, self.energy_threshold + 15))  # Reduced max from 1200 to 1000
            else:
                self.energy_threshold = int(
                    max(400, self.energy_threshold - 3))  # Lowered min from 500 to 400, faster decay

            if self.debug_audio and self.debug_counter % 20 == 0:
                print("[DANCE] Energy: %.1f, Threshold: %d, Beat: %s" %
                      (energy, beat_threshold, beat_detected))

            if beat_detected:
                self.last_beat_time = current_time
                if self.debug_audio:
                    print("[DANCE] 🎵 DANCE BEAT DETECTED! 🎵")
                return True

        except MemoryError:
            print("[DANCE] Beat detection memory error - using fallback")
            return False

        return False

    def _update_beat_focused_visualization(self, color_func, beat_detected, volume):
        """Beat-focused visualization - flash on beats, subtle ambient otherwise."""
        current_time = time.monotonic()

        if beat_detected:
            # Beat response - dramatic full-ring flash
            self._display_beat_flash(color_func, volume)
        else:
            # Subtle ambient pattern when no beat (much more subdued than routine 2)
            self._display_ambient_dance_pattern(color_func)

        self.last_update = current_time

    def _display_beat_flash(self, color_func, volume):
        """Display dramatic beat flash - full ring lights up."""
        try:
            # Beat flash - all pixels with bright color
            flash_color = color_func(255)  # Full intensity

            # Flash all pixels
            for i in range(10):
                self.hardware.pixels[i] = flash_color

            self.hardware.pixels.show()

            # Optional beat sound
            if volume:
                beat_freq = 800 + (self.beat_pattern_state * 30)
                self.hardware.play_tone_if_enabled(beat_freq, 0.08, volume)

            # Cycle beat pattern state for variation
            self.beat_pattern_state = (self.beat_pattern_state + 1) % 8

        except MemoryError:
            print("[DANCE] Beat flash memory error")
            self.hardware.clear_pixels()
            self.hardware.pixels.show()

    def _display_ambient_dance_pattern(self, color_func):
        """Display very subtle ambient pattern when no beat detected."""
        try:
            current_time = time.monotonic()

            # Much more subtle than the continuous wave in routine 2
            # Just a slow, gentle rotating pair of dim pixels
            if current_time - self.last_pattern_update > 0.4:  # Slower rotation
                rotation_speed = 0.5  # Much slower than routine 2
                time_delta = current_time - self.last_update

                self.rotation_offset = (
                                                   self.rotation_offset + rotation_speed * time_delta) % 10

                # Clear pixels
                self.hardware.clear_pixels()

                # Just 2 dim pixels rotating slowly
                pos1 = int(self.rotation_offset % 10)
                pos2 = int((self.rotation_offset + 5) % 10)  # Opposite side

                dim_color = color_func(40)  # Very dim ambient

                self.hardware.pixels[pos1] = dim_color
                self.hardware.pixels[pos2] = dim_color

                self.hardware.pixels.show()
                self.last_pattern_update = current_time

        except MemoryError:
            print("[DANCE] Ambient pattern memory error")
            self._safe_mode_pattern(color_func)
