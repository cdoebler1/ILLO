# Charles Doebler at Feral Cat AI
# Multi-UFO Synchronized Dance Party - ROYGBIV BLE Sync

from base_routine import BaseRoutine
from audio_processor import AudioProcessor
import time
import gc
import microcontroller
from adafruit_circuitplayground import cp
from adafruit_ble import BLERadio
from adafruit_ble.advertising.standard import Advertisement


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

        # Current mode for follower pattern replication
        self._current_mode = 1

        # Load configuration
        self.config = self._load_dance_config()

        # BLE sync configuration
        self.is_leader = self.config.get('is_leader', False)
        self.sync_enabled = self.config.get('bluetooth_enabled', True)

        # Add sync_manager attribute for compatibility with main code
        self.sync_manager = None

        # BLE sync components
        self.ble = None
        self.sync_active = False
        self.last_seen_t = None
        self.last_seq = None
        self.sync_count = 0
        self.next_tick_ms = None

        # ROYGBIV color sequence
        self.roygbiv_colors = [
            (255, 0, 0),  # Red
            (255, 69, 0),  # Orange-Red
            (255, 165, 0),  # Orange
            (255, 215, 0),  # Gold
            (255, 255, 0),  # Yellow
            (173, 255, 47),  # Green-Yellow
            (0, 128, 0),  # Green
            (0, 255, 255),  # Cyan
            (30, 144, 255),  # Dodger-Blue
            (65, 105, 225),  # Royal-Blue
        ]

        self.brightness_factor = 0.3
        self.color_names = ["Red", "Orange-Red", "Orange", "Gold", "Yellow",
                            "Green-Yellow", "Green", "Cyan", "Dodger-Blue",
                            "Royal-Blue"]

        # Sync timing
        self.step_ms = 100  # 100ms per step for 1-second full cycle
        self.rx_bias_ms = 50
        self.loss_timeout_s = 3.0
        self.tick_period_ms = self.step_ms

        # Leader state
        self.seq = 0
        self.sync_index = 0
        self.last_tick_ms = self._now_ms()
        self.next_sync_tick_ms = self.last_tick_ms + self.step_ms
        self.last_adv_time = 0

        # Beat detection parameters
        self.last_beat_time = 0
        self.beat_pattern_state = 0
        self.energy_threshold = 600

        # Dance timing
        self.last_pattern_update = time.monotonic()

        print("[DANCE] 🎵 Dance Party initialized with BLE ROYGBIV Sync")

        if self.is_leader:
            print("[DANCE] 👑 Configured as LEADER")
        else:
            print("[DANCE] 💃 Configured as FOLLOWER")

        # Initialize BLE if sync enabled
        if self.sync_enabled:
            self._initialize_ble()
            # Set sync_manager to self for compatibility
            if self.sync_active:
                self.sync_manager = self

    def enable_bluetooth(self):
        """Enable Bluetooth functionality - compatibility method for main code."""
        if self.sync_active:
            print("[DANCE] ✅ Bluetooth already active")
            return True
        else:
            print("[DANCE] ❌ Bluetooth initialization failed")
            return False

    def run(self, mode, volume):
        """Run the dance party with BLE audio visualization sync."""
        # Update current mode for follower pattern replication
        self._current_mode = mode
        
        # Increment debug counter
        self.debug_counter += 1

        # Force garbage collection periodically
        if self.debug_counter % 100 == 0:
            gc.collect()

        # Handle BLE sync
        if self.sync_active:
            if self.is_leader:
                # Leader: Run normal audio visualization, then broadcast the pattern
                self._process_beat_focused_dance(mode, 0)  # This creates the audio visualization
                self._leader_broadcast_sync()  # This broadcasts the resulting pattern

            else:
                # Follower: Scan for leader and replicate the audio visualization pattern
                self._follower_scan_for_leader()
        else:
            # Fallback to regular dance party behavior (beeping disabled)
            self._process_beat_focused_dance(mode, 0)

    def _leader_broadcast_sync(self):
        """Leader broadcasts current audio visualization pattern to followers."""
        if not self.is_leader or not self.sync_active or not self.ble:
            return

        t = self._now_ms()

        # Broadcast every 100ms for smooth sync
        if t - self.last_adv_time > 100:
            try:
                # Get current pixel pattern from the leader's audio visualization
                current_pattern = []
                for i in range(10):
                    pixel_color = self.hardware.pixels[i]
                    # Compress RGB to fit in BLE advertisement (use dominant values)
                    if pixel_color != (0, 0, 0):
                        # Find the dominant color component
                        max_component = max(pixel_color)
                        if max_component > 0:
                            # Normalize and encode: position, intensity, color_type
                            intensity = min(255, max_component)
                            if pixel_color[0] == max_component:  # Red dominant
                                color_type = 0
                            elif pixel_color[1] == max_component:  # Green dominant  
                                color_type = 1
                            else:  # Blue dominant
                                color_type = 2
                            current_pattern.append((i, intensity, color_type))

                # Create pattern data for broadcasting (max 3 pixels to fit in BLE)
                pattern_data = current_pattern[:3]  # Limit to 3 brightest pixels
                
                if len(pattern_data) == 0:
                    # No pattern - send idle data
                    pattern_data = [(0, 0, 0)]

                self.seq = (self.seq + 1) % 256

                # Create advertisement with pattern data
                # Format: ILLO_SEQ_POS1_INT1_COL1_POS2_INT2_COL2...
                adv_name = f"ILLO_{self.seq}"
                for pos, intensity, color_type in pattern_data:
                    adv_name += f"_{pos}_{intensity}_{color_type}"

                # Pad to consistent length if needed
                while len(pattern_data) < 3:
                    adv_name += "_0_0_0"
                    pattern_data.append((0, 0, 0))

                # Debug: Show what we're broadcasting
                if self.debug_bluetooth and self.debug_counter % 10 == 0:
                    print(f"[DANCE] 📡 LEADER: Broadcasting '{adv_name}' with {len(current_pattern)} active pixels")

                # Create and send advertisement
                adv = Advertisement()
                adv.complete_name = adv_name

                try:
                    self.ble.stop_advertising()
                except:
                    pass

                self.ble.start_advertising(adv)
                self.last_adv_time = t

            except Exception as e:
                if self.debug_bluetooth:
                    print(f"[DANCE] ❌ LEADER: Broadcast error: {e}")

    def _dance_audio_visualization(self, deltas, color_func, volume,
                                   beat_detected=False):
        """Audio visualization for non-sync mode."""
        current_time = time.monotonic()

        # Map audio deltas to pixels
        pixel_data = self.hardware.map_deltas_to_pixels(deltas)

        # Calculate frequency for rotation speed
        try:
            freq = self.audio.calculate_frequency(deltas)
            rotation_speed = max(2.0, freq * 0.08) if freq else 3.0
        except:
            rotation_speed = 3.0

        # Update rotation offset
        time_delta = current_time - self.last_update
        self.rotation_offset = (self.rotation_offset + rotation_speed * time_delta) % 10

        # Clear pixels
        self.hardware.clear_pixels()

        # Enhanced visualization
        active_pixel_count = min(8, max(3, len([p for p in pixel_data if p > 30])))

        for i in range(active_pixel_count):
            pos = int((self.rotation_offset + i * 1.2) % 10)
            pixel_index = min(i, len(pixel_data) - 1)
            intensity = pixel_data[pixel_index]
            boosted_intensity = min(255, int(intensity * 1.5))

            if boosted_intensity > 20:
                pixel_color = color_func(boosted_intensity)
                if boosted_intensity > 180:
                    pixel_color = tuple(min(255, int(c * 1.2)) for c in pixel_color)
                self.hardware.pixels[pos] = pixel_color

        # Beat emphasis - BEEPING DISABLED
        if beat_detected or (len(pixel_data) > 0 and max(pixel_data) > 150):
            beat_positions = [(int(self.rotation_offset) + 5) % 10]
            beat_color = color_func(255)
            for beat_pos in beat_positions:
                self.hardware.pixels[beat_pos] = beat_color
            # Note: Removed beeping - self.hardware.play_tone_if_enabled() call

        self.hardware.pixels.show()
        self.last_update = current_time

    def _load_dance_config(self):
        """Load dance-specific configuration from config.json."""
        try:
            from config_manager import ConfigManager
            config_mgr = ConfigManager()
            return config_mgr.load_config()
        except Exception as e:
            print("[DANCE] ❌ Failed to load config: %s" % str(e))
            return {
                'is_leader': False,
                'bluetooth_enabled': True
            }

    def _initialize_ble(self):
        """Initialize BLE radio for sync."""
        try:
            self.ble = BLERadio()
            self.sync_active = True
            print("[DANCE] ✅ BLE initialized for sync")
        except Exception as e:
            print("[DANCE] ❌ BLE initialization failed: %s" % str(e))
            self.sync_active = False

    def _now_ms(self):
        """Get current time in milliseconds."""
        return int(time.monotonic() * 1000)

    def _scale_color(self, rgb, factor):
        """Scale RGB values by factor for brightness control."""
        return tuple(int(c * factor) for c in rgb)

    def _parse_pattern_name(self, name):
        """Parse pattern advertisement name: ILLO_SEQ_POS1_INT1_COL1_POS2_INT2_COL2..."""
        if not name or not name.startswith("ILLO_"):
            return None

        try:
            parts = name.split("_")
            if len(parts) < 4:  # Need at least ILLO_SEQ_POS1_INT1_COL1
                return None

            seq = int(parts[1])
            pattern_pixels = []
            
            # Parse pattern data (groups of 3: position, intensity, color_type)
            for i in range(2, len(parts), 3):
                if i + 2 < len(parts):
                    pos = int(parts[i])
                    intensity = int(parts[i + 1])
                    color_type = int(parts[i + 2])
                    
                    if pos < 10 and intensity > 0:  # Valid pixel data
                        pattern_pixels.append((pos, intensity, color_type))

            return {
                "seq": seq,
                "pattern": pattern_pixels
            }
        except:
            return None

    def _follower_scan_for_leader(self):
        """Follower scans for leader and replicates the audio visualization pattern."""
        if self.is_leader or not self.sync_active or not self.ble:
            return

        try:
            found_leader = False

            # Increase scan timeout to give more time to find leader
            for adv in self.ble.start_scan(Advertisement, timeout=0.5, minimum_rssi=-120):
                # Get advertisement name
                adv_name = ''
                if hasattr(adv, 'complete_name') and adv.complete_name:
                    adv_name = adv.complete_name
                elif hasattr(adv, 'short_name') and adv.short_name:
                    adv_name = adv.short_name

                # Debug: Show all advertisements found
                if self.debug_bluetooth and adv_name:
                    print(f"[DANCE] 🔍 Found advertisement: {adv_name}")

                # Look for ILLO pattern advertisements
                if adv_name and adv_name.startswith("ILLO_"):
                    if self.debug_bluetooth:
                        print(f"[DANCE] 📡 Parsing ILLO advertisement: {adv_name}")
                    
                    parsed = self._parse_pattern_name(adv_name)
                    if parsed:
                        found_leader = True
                        current_time = time.monotonic()
                        self.last_seen_t = current_time

                        if self.debug_bluetooth:
                            print(f"[DANCE] ✅ Successfully parsed leader pattern with {len(parsed['pattern'])} pixels")

                        # Check if this is a new sequence - NO WHITE FLASH
                        if self.last_seq is None or parsed["seq"] != self.last_seq:
                            self.sync_count += 1
                            # NO WHITE FLASH: self._flash_sync_indicator() is disabled
                            
                            if self.debug_bluetooth:
                                print(f"🎯 SYNC #{self.sync_count}: New audio pattern from leader!")
                            self.last_seq = parsed["seq"]

                        # Replicate the leader's audio visualization pattern
                        self._replicate_audio_visualization(parsed["pattern"])
                        break
                    else:
                        if self.debug_bluetooth:
                            print(f"[DANCE] ❌ Failed to parse ILLO advertisement: {adv_name}")

            self.ble.stop_scan()

            # Debug: Report scan results
            if self.debug_bluetooth and not found_leader:
                print("[DANCE] 🔍 No leader found in this scan")

            # Handle loss of sync - clear pixels without white flash
            if not found_leader and self.last_seen_t is not None:
                if (time.monotonic() - self.last_seen_t) >= self.loss_timeout_s:
                    if self.debug_bluetooth:
                        print("[DANCE] ❌ FOLLOWER: Lost leader signal")
                    self.hardware.clear_pixels()
                    self.hardware.pixels.show()
                    self.last_seq = None

        except Exception as e:
            if self.debug_bluetooth:
                print(f"[DANCE] ❌ FOLLOWER: Scan error: {e}")

    def _replicate_audio_visualization(self, pattern_pixels):
        """Replicate the leader's exact audio visualization pattern."""
        # Get color function from current mode
        color_func = self.get_color_function(self._current_mode)

        # Clear all pixels first
        self.hardware.clear_pixels()

        # Apply the leader's pattern
        for pos, intensity, color_type in pattern_pixels:
            if pos < 10 and intensity > 0:
                # Use the color function directly with the intensity to get proper themed colors
                # The color_type just tells us the dominant component, but we want the full themed color
                themed_color = color_func(intensity)
                
                # Apply a slight color bias based on the dominant type to preserve audio character
                r, g, b = themed_color
                
                if color_type == 0:  # Red dominant - boost red slightly
                    final_color = (min(255, int(r * 1.1)), int(g * 0.9), int(b * 0.9))
                elif color_type == 1:  # Green dominant - boost green slightly  
                    final_color = (int(r * 0.9), min(255, int(g * 1.1)), int(b * 0.9))
                else:  # Blue dominant - boost blue slightly
                    final_color = (int(r * 0.9), int(g * 0.9), min(255, int(b * 1.1)))

                self.hardware.pixels[pos] = final_color

        self.hardware.pixels.show()

        if self.debug_bluetooth and self.debug_counter % 20 == 0:
            print(
                f"[DANCE] 🎨 FOLLOWER: Displayed {len(pattern_pixels)} pixels from leader's audio visualization")

    def _follower_local_sync(self):
        """Follower runs local sync when connected."""
        # This method is no longer needed since we handle sync in _follower_scan_for_leader
        pass

    def _process_beat_focused_dance(self, effective_mode, volume):
        """Fallback dance processing when BLE sync is disabled."""
        color_func = self.get_color_function(effective_mode)

        try:
            np_samples = self.audio.record_samples()
            deltas = self.audio.compute_deltas(np_samples)

            # Environmental brightness control
            self._apply_environmental_dimming()

            # Check for beats
            beat_detected = self._enhanced_dance_beat_detection(np_samples) if len(
                np_samples) > 0 else False

            # Use audio visualization
            if len(deltas) > 0:
                self._dance_audio_visualization(deltas, color_func, volume,
                                                beat_detected)
            else:
                # Simple rotating pattern when no audio
                self._dance_idle_animation(color_func)

        except MemoryError:
            print("[DANCE] ❌ Memory error - switching to safe mode")
            self._safe_mode_pattern(color_func)
            gc.collect()

    def _dance_idle_animation(self, color_func):
        """Idle animation for non-sync mode."""
        current_time = time.monotonic()

        if current_time - self.last_pattern_update > 0.1:
            self.rotation_offset = (self.rotation_offset + 2.0) % 10
            self.hardware.clear_pixels()

            main_pos = int(self.rotation_offset)
            trail1_pos = (main_pos - 1) % 10
            trail2_pos = (main_pos - 2) % 10
            trail3_pos = (main_pos - 3) % 10

            self.hardware.pixels[main_pos] = color_func(200)
            self.hardware.pixels[trail1_pos] = color_func(140)
            self.hardware.pixels[trail2_pos] = color_func(80)
            self.hardware.pixels[trail3_pos] = color_func(40)

            if self.debug_counter % 20 == 0:
                sparkle_pos = (main_pos + 5) % 10
                self.hardware.pixels[sparkle_pos] = color_func(100)

            self.hardware.pixels.show()
            self.last_pattern_update = current_time

    def _apply_environmental_dimming(self):
        """Apply environmental brightness control."""
        try:
            current_light = cp.light

            if current_light < 30:
                target_brightness = 0.03
            elif current_light < 60:
                target_brightness = 0.06
            elif current_light < 100:
                target_brightness = 0.12
            elif current_light < 150:
                target_brightness = 0.18
            else:
                target_brightness = 0.25

            current_brightness = self.hardware.pixels.brightness
            if abs(target_brightness - current_brightness) > 0.01:
                if target_brightness > current_brightness:
                    new_brightness = min(target_brightness, current_brightness + 0.01)
                else:
                    new_brightness = max(target_brightness, current_brightness - 0.01)
                self.hardware.pixels.brightness = new_brightness

        except Exception as e:
            if self.debug_counter % 50 == 0:
                print("[DANCE] Environmental dimming error: %s" % str(e))

    def _enhanced_dance_beat_detection(self, np_samples):
        """Enhanced beat detection."""
        if len(np_samples) < 50:
            return False

        current_time = time.monotonic()
        if current_time - self.last_beat_time < 0.12:
            return False

        try:
            sample_count = min(len(np_samples), 250)
            total_energy = 0
            sample_sum = sum(np_samples[i] for i in range(sample_count))
            mean_sample = sample_sum / sample_count

            for i in range(sample_count):
                diff = np_samples[i] - mean_sample
                total_energy += diff * diff

            energy = (total_energy / sample_count) ** 0.5
            beat_threshold = int(max(400, int(self.energy_threshold * 0.6)))
            beat_detected = energy > beat_threshold

            if beat_detected:
                self.energy_threshold = int(min(1000, self.energy_threshold + 15))
                self.last_beat_time = current_time
                return True
            else:
                self.energy_threshold = int(max(400, self.energy_threshold - 3))

        except MemoryError:
            return False

        return False

    def _safe_mode_pattern(self, color_func):
        """Ultra-simple pattern for low memory."""
        current_time = time.monotonic()

        if current_time - self.last_pattern_update > 0.3:
            pos = int((current_time * 2) % 10)
            self.hardware.clear_pixels()
            self.hardware.pixels[pos] = color_func(100)
            self.hardware.pixels.show()
            self.last_pattern_update = current_time