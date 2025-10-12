"""Dance Party Routine - Multi-UFO Synchronized Light Show via BLE.

This module implements a synchronized dance party routine where multiple Circuit
Playground Express devices can synchronize their NeoPixel displays over Bluetooth
Low Energy (BLE) using advertisement names as the communication protocol.

The routine supports two roles:
    - **Leader**: Audio-reactive display with beat detection (Mode 1)
    - **Follower**: Mirrors leader's display in real-time (Modes 2-4)

Protocol Format:
    ILLO_<seq>_<pos1>_<int1>_<col1>_<pos2>_<int2>_<col2>_<pos3>_<int3>_<col3>

Example:
    >>> from dance_party import DanceParty
    >>> dance = DanceParty("ILLO_01", debug_bluetooth=True)
    >>> dance.run(mode=1, volume=1)  # Leader mode with audio (volume: 0=off, 1=on)

Author:
    Charles Doebler — Feral Cat AI

Dependencies:
    - adafruit_circuitplayground
    - adafruit_ble
    - audio_processor (optional)
    
Note:
    The "volume" parameter throughout this module is a sound enable flag (0=off, 1=on)
    rather than an actual volume control, since the Circuit Playground Express piezo
    speaker has no volume adjustment capability. The naming is maintained for consistency
    with the hardware switch and other routines.
"""

from base_routine import BaseRoutine
import time
import gc
from adafruit_circuitplayground import cp
from adafruit_ble import BLERadio
from adafruit_ble.advertising.standard import Advertisement

# Optional project audio helper
try:
    from audio_processor import AudioProcessor

    _HAS_AUDIO = True
except Exception:
    _HAS_AUDIO = False


class DanceParty(BaseRoutine):
    """Leader/follower visual synchronization over BLE advertisement names.

    This class implements a synchronized light show routine where one device acts
    as a leader (audio-reactive) and others follow by mirroring the leader's display.

    The visual display consists of three pixels that form an animated baton:
        - Head pixel: Full intensity at current position
        - Trail1: 55% intensity, follows head by 1 step
        - Trail2/Spark: Temporary beat effect at 75% intensity

    Audio processing features (leader mode):
        - Two-stage smoothing prevents visual jitter
        - Hysteretic color switching prevents rapid flickering
        - Beat detection triggers direction changes and visual effects

    Attributes:
        device_name (str): BLE device identifier
        debug_bluetooth (bool): Enable verbose BLE debugging output
        debug_audio (bool): Enable verbose audio processing output
        sync_enabled (bool): Whether BLE sync is enabled via config
        sync_active (bool): Whether BLE is currently initialized and active
        ble (BLERadio): BLE radio instance (None if not initialized)

    Class Attributes:
        _NUM_PIXELS (int): Number of NeoPixels on the device (10)
        _BRIGHTNESS (float): Global brightness setting (0.0-1.0)
        _STEP_MS (int): Time between position updates in milliseconds
        _ADV_PERIOD_MS (int): BLE advertisement refresh rate in milliseconds
        _SCAN_BURST_S (float): Follower scan duration in seconds
        _LOSS_TIMEOUT_S (float): Follower timeout before declaring leader lost
        _MIN_RENDER_MS (int): Minimum time between render updates (rate limiting)
        _SMOOTH_ALPHA (float): Exponential smoothing factor for follower (0.0-1.0)


    Example:
        >>> # Leader mode with debugging
        >>> leader = DanceParty("LEADER_01", debug_bluetooth=True, debug_audio=True)
        >>> leader.run(mode=1, volume=1)  # volume: 0=off, 1=on

        >>> # Follower mode
        >>> follower = DanceParty("FOLLOWER_02")
        >>> follower.run(mode=2, volume=0)  # silent follower

    Note:
        - Mode 1 is always Leader
        - Modes 2-4 are always Follower (safe default for undefined modes)
        - Follower mode ignores audio input and mirrors leader visuals
        - Volume parameter is a sound on/off flag, not actual volume control
    """

    _NUM_PIXELS = 10
    _BRIGHTNESS = 0.20

    # Timing constants
    _STEP_MS = 260  # visual step; adv matches this (≈3.8 revs/min)
    _ADV_PERIOD_MS = 260  # advertising refresh cadence (aligned with a step)
    _SCAN_BURST_S = 0.35  # follower scan burst (active scan)
    _LOSS_TIMEOUT_S = 3.0  # follower loss detection
    _MIN_RENDER_MS = 30  # ~33 FPS cap (rate limit follower render)
    _SMOOTH_ALPHA = 0.65  # follower smoothing 0..1; higher = snappier

    def __init__(self, device_name, debug_bluetooth=False, debug_audio=False):
        """Initialize Dance Party routine.

        Args:
            device_name (str): BLE device identifier (e.g., "ILLO_01")
            debug_bluetooth (bool, optional): Enable BLE debugging output. Defaults to False.
            debug_audio (bool, optional): Enable audio debugging output. Defaults to False.

        Raises:
            ImportError: If required CircuitPython libraries are missing
            MemoryError: If insufficient memory for initialization

        Note:
            - Validates timing constants on initialization
            - Reports memory usage if debugging enabled
            - Attempts BLE initialization if enabled in config
        """
        super().__init__()
        self.device_name = device_name
        self.debug_bluetooth = bool(debug_bluetooth)
        self.debug_audio = bool(debug_audio)

        # Validate timing configuration
        if self._STEP_MS < 100 or self._STEP_MS > 1000:
            print("[DANCE] ⚠️ _STEP_MS out of recommended range (100-1000ms)")
        if self._ADV_PERIOD_MS > self._STEP_MS:
            print("[DANCE] ⚠️ _ADV_PERIOD_MS should be <= _STEP_MS for smooth sync")

        # Memory tracking
        if debug_bluetooth or debug_audio:
            self._initial_free_mem = gc.mem_free()
            print("[DANCE] 💾 Initial free memory: %d bytes" % self._initial_free_mem)

        # Config
        self.config = self._load_dance_config()
        self.sync_enabled = bool(self.config.get('bluetooth_enabled', True))

        # BLE
        self.ble = None
        self.sync_active = False
        self.sync_manager = None  # checked by code.py

        # Leader state
        self._seq = 0
        self._last_adv_ms = 0
        self._index = 0
        self._next_tick_ms = self._now_ms() + self._STEP_MS

        # Expressive motion state (leader)
        self._dir = 1  # +1 or -1
        self._gap = 1  # trail spacing (1 or 2)
        self._swing_ms = 0  # jitter applied to the next step after beats
        self._beat_on = False
        self._beat_timer = 0  # frames remaining for "pop"
        self._spark_pos = None  # transient spark position (uses third triple)

        # Follower state
        self._last_seen_t = None
        self._last_seq = None

        # Connection health tracking
        self._sync_success_count = 0
        self._sync_fail_count = 0
        self._last_health_report_t = 0

        # Role tracking
        self._role_announced = False
        self._current_role = None

        # Audio
        self._audio_ok = False
        if _HAS_AUDIO:
            try:
                self.audio = AudioProcessor()
                self._audio_ok = True
            except Exception as e:
                if self.debug_audio:
                    print("[DANCE] ⚠️ Audio init failed: %s" % e)

        # Smoothed energy, envelope and hysteretic color (leader)
        self._energy_lp = 120.0
        self._env = 120.0
        self._ctype = 2  # 0=red, 1=green, 2=blue/pink-ish

        # Pixels
        cp.pixels.auto_write = False
        cp.pixels.brightness = self._BRIGHTNESS
        self._clear_pixels()
        self._last_render_ms = 0
        self._smooth_rgb = [[0.0, 0.0, 0.0] for _ in range(self._NUM_PIXELS)]

        print("[DANCE] 🎵 Dance Party init — BLE=%s, audio=%s"
              % ("EN" if self.sync_enabled else "DIS",
                 "Y" if self._audio_ok else "N"))

        if self.sync_enabled:
            self._initialize_ble()
            if self.sync_active:
                self.sync_manager = self

        # Memory report after init
        if debug_bluetooth or debug_audio:
            final_free = gc.mem_free()
            used = self._initial_free_mem - final_free
            print(
                "[DANCE] 💾 Init used %d bytes, %d bytes remaining" % (used, final_free))

    def enable_bluetooth(self):
        """Enable Bluetooth if not already active.

        Returns:
            bool: True if BLE is active after call, False otherwise

        Note:
            This method is called by code.py to enable BLE dynamically.
            Safe to call multiple times - idempotent operation.
        """
        if self.sync_active:
            if self.debug_bluetooth:
                print("[DANCE] ✅ Bluetooth already active")
            return True
        try:
            self._initialize_ble()
            return self.sync_active
        except Exception as e:
            print("[DANCE] ❌ Bluetooth enable failed: %s" % e)
            return False

    def run(self, mode, volume):

        """Main execution loop for Dance Party routine.

        Args:
            mode (int): Determines role. 1=Leader, 2-4=Follower (safe default)
            volume (int): Sound enable flag (0=off, 1=on). Note: Called "volume" for
                         consistency with hardware switch, but acts as boolean since
                         piezo speaker has no actual volume control. Passed to audio
                         processor for compatibility with other routines.

        Note:
            - Called repeatedly by main event loop in code.py
            - Leader mode: Draws audio-reactive visuals and broadcasts via BLE
            - Follower mode: Scans for leader and mirrors received visuals
            - Falls back to local audio visualization if BLE unavailable

        Example:
            >>> dance = DanceParty("ILLO_01")
            >>> while True:
            ...     dance.run(mode=1, volume=1)  # Leader with audio (sound enabled)
        """
        # Determine leader/follower based on mode
        is_leader = (mode == 1)

        # Announce role once when it's determined
        if not self._role_announced or self._current_role != is_leader:
            role_name = "LEADER" if is_leader else "FOLLOWER"
            sync_status = "enabled" if self.sync_active else "disabled"
            print("[DANCE] 💃 Role: %s (BLE sync %s)" % (role_name, sync_status))
            self._role_announced = True
            self._current_role = is_leader

        # Reinitialize BLE if mode changed and not yet active
        if self.sync_enabled and not self.sync_active:
            self._initialize_ble(is_leader)

        if not self.sync_active:
            # Local fallback: still show audio baton if possible
            self._leader_frame()
            self._advance_ring_if_due()
            return

        if is_leader:
            # Draw first, then handle BLE (keeps visuals smooth)
            self._leader_frame()
            self._advance_ring_if_due()
            self._leader_advertise_if_due()
        else:
            self._follower_loop()

        # Periodic GC under debug
        if self.debug_bluetooth and (self._seq % 50 == 0):
            gc.collect()

        time.sleep(0.001)

    def _leader_frame(self):
        """Render an audio-reactive baton with expressive beat pops.

        This method implements the leader's visual display, which consists of:
            - Audio energy analysis with two-stage smoothing
            - Hysteretic color selection (prevents flickering)
            - Beat detection triggering visual effects
            - Three-pixel baton (head + trail + optional spark)

        The rendered state is cached in `_last_triples` for BLE broadcasting.

        Note:
            - Falls back to default intensity (140) if audio unavailable
            - Beat detection triggers direction reversal and spark effects
            - Quantizes intensity to reduce BLE state changes
        """
        intensity = 140  # calmer default
        color_type = self._ctype

        if self._audio_ok:
            try:
                samples = self.audio.record_samples()
                if samples and len(samples) > 0:
                    n = min(len(samples), 200)
                    if n > 0:
                        ssum = 0.0
                        mean = 0.0
                        for i in range(n):
                            mean += samples[i]
                        mean = mean / n
                        for i in range(n):
                            d = samples[i] - mean
                            ssum += d * d
                        energy = (ssum / n) ** 0.5

                        # Sanity check on energy value (16-bit PCM range)
                        if 0 <= energy <= 32768:
                            # Two-stage smoothing: fast LP plus slower envelope
                            self._energy_lp = 0.82 * self._energy_lp + 0.18 * energy
                            if self._energy_lp > self._env:  # attack
                                self._env = 0.60 * self._env + 0.40 * self._energy_lp
                            else:  # decay
                                self._env = 0.92 * self._env + 0.08 * self._energy_lp
                            intensity = int(max(60, min(240, self._env)))
                            # Quantize intensity to coarse steps (fewer states)
                            intensity = (intensity // 32) * 32
                            # Hysteretic color selection
                            high_on, high_off = 208, 192
                            mid_on, mid_off = 152, 136
                            if self._ctype == 0 and intensity < high_off:
                                self._ctype = 1
                            elif self._ctype == 1 and intensity < mid_off:
                                self._ctype = 2
                            elif self._ctype == 1 and intensity > high_on:
                                self._ctype = 0
                            elif self._ctype == 2 and intensity > mid_on:
                                self._ctype = 1
                            color_type = self._ctype
                        else:
                            if self.debug_audio:
                                print("[DANCE] ⚠️ Invalid energy value: %f" % energy)

            except Exception as e:
                if self.debug_audio:
                    print("[DANCE] audio err: %s" % e)

        # Lightweight beat detect from envelope movement
        beat_thr_on, beat_thr_off = 192, 168
        if not self._beat_on and intensity >= beat_thr_on:
            self._beat_on = True
            self._beat_timer = 2
            self._gap = 2
            self._swing_ms = int(self._STEP_MS * 0.08)
            if intensity >= 224:
                self._dir = -self._dir
            self._spark_pos = (self._index + (2 * self._dir)) % self._NUM_PIXELS
        elif self._beat_on and intensity <= beat_thr_off:
            self._beat_on = False

        # Build 3 pixels: head + ONE trail + optional spark (3rd triple)
        head_pos = self._index
        trail1 = (head_pos - (1 * self._dir)) % self._NUM_PIXELS
        trail2 = (head_pos - (self._gap * self._dir)) % self._NUM_PIXELS

        head_int = intensity + (40 if self._beat_timer > 0 else 0)
        if head_int > 255:
            head_int = 255
        t1_int = max(0, int(head_int * 0.55))
        t2_int = 0
        if self._spark_pos is not None:
            trail2 = self._spark_pos
            t2_int = min(255, int(head_int * 0.75))

        # Convert color_type + intensity to RGB
        def themed_rgb(inten, ctype):
            """Convert intensity and color type to RGB tuple.

            Args:
                inten (int): Intensity value (0-255)
                ctype (int): Color type (0=red, 1=green, 2=blue/pink)

            Returns:
                tuple: RGB color tuple (r, g, b) with values 0-255
            """
            inten = int(inten)
            if inten <= 0:
                return 0, 0, 0
            if ctype == 0:  # red-ish
                return inten, int(inten * 0.15), int(inten * 0.15)
            elif ctype == 1:  # green-ish
                return int(inten * 0.15), inten, int(inten * 0.15)
            else:  # blue/pink-ish
                return int(inten * 0.3), int(inten * 0.05), inten

        # Draw leader pixels
        self._clear_pixels()
        cp.pixels[trail2] = themed_rgb(t2_int, color_type)
        cp.pixels[trail1] = themed_rgb(t1_int, color_type)
        cp.pixels[head_pos] = themed_rgb(head_int, color_type)
        cp.pixels.show()

        # Cache for advertisement build
        self._last_triples = [
            (head_pos, head_int, color_type),
            (trail1, t1_int, color_type),
            (trail2, t2_int, color_type),
        ]

        # Decay one-frame spark and beat pop
        if self._beat_timer > 0:
            self._beat_timer -= 1
        if self._beat_timer == 0:
            self._spark_pos = None

    def _advance_ring_if_due(self):
        """Advance the ring position based on timing and swing effects.

        Updates the current position index if enough time has elapsed since
        the last position update. Applies swing timing offset from beat effects.

        Note:
            - Uses `_next_tick_ms` to avoid timing drift
            - Applies and then resets `_swing_ms` offset
        """
        t = self._now_ms()
        if t >= self._next_tick_ms:
            self._index = (self._index + self._dir) % self._NUM_PIXELS
            step = self._STEP_MS + (self._swing_ms if self._swing_ms else 0)
            self._next_tick_ms = t + step
            self._swing_ms = 0

    def _leader_advertise_if_due(self):
        """Advertise current visual state via BLE name if due.

        Builds advertisement name from cached visual state and broadcasts via BLE.
        Includes emergency garbage collection if MemoryError occurs.

        Raises:
            MemoryError: Triggers emergency GC and reports memory status

        Note:
            - Rate-limited by `_ADV_PERIOD_MS`
            - Stops previous advertisement before starting new one
            - Errors are suppressed except MemoryError (always reported)
        """
        t = self._now_ms()
        if (t - self._last_adv_ms) < self._ADV_PERIOD_MS:
            return

        name = self._build_adv_name_from_triples()
        adv = Advertisement()
        adv.complete_name = name

        try:
            try:
                self.ble.stop_advertising()
            except Exception:
                pass
            self.ble.start_advertising(adv)

            # Success feedback
            if self.debug_bluetooth and (self._seq % 100 == 0):
                print("[DANCE] ✅ ADV healthy, seq=%d" % self._seq)

        except MemoryError as e:
            print("[DANCE] 🚨 MEMORY ERROR in advertising: %s" % e)
            gc.collect()
            print("[DANCE] 🧹 Emergency GC, freed to %d bytes" % gc.mem_free())
        except Exception as e:
            if self.debug_bluetooth and (self._seq % 20 == 0):
                print("[DANCE] ⚠️ ADV restart suppressed: %s" % e)
        finally:
            self._last_adv_ms = t

    def _build_adv_name_from_triples(self):
        """Build BLE advertisement name from current visual state.

        Returns:
            str: Advertisement name in ILLO protocol format

        Format:
            ILLO_<seq>_<p1>_<i1>_<c1>_<p2>_<i2>_<c2>_<p3>_<i3>_<c3>

        Where:
            - seq: Sequence number (0-255, wraps)
            - p: Pixel position (0-9)
            - i: Intensity (0-255)
            - c: Color type (0=red, 1=green, 2=blue)

        Note:
            - Pads with zeros if fewer than 3 triples cached
            - Increments sequence number on each call
        """
        triples = getattr(self, "_last_triples", [])
        while len(triples) < 3:
            triples.append((0, 0, 0))
        self._seq = (self._seq + 1) % 256
        (p1, i1, c1) = triples[0]
        (p2, i2, c2) = triples[1]
        (p3, i3, c3) = triples[2]
        name = "ILLO_%d_%d_%d_%d_%d_%d_%d_%d_%d_%d" % (
            self._seq, p1, i1, c1, p2, i2, c2, p3, i3, c3
        )
        if self.debug_bluetooth and (self._seq % 20 == 0):
            print("[DANCE] 📡 ADV: %s" % name)
        return name

    def _follower_loop(self):
        """Follower mode: scan for leader advertisements and mirror visuals.

        Performs active BLE scan to find leader advertisements, parses received
        visual state, and renders to local NeoPixels with smoothing.

        Features:
            - Active scanning for long advertisement names
            - Duplicate frame detection via sequence number
            - Connection health tracking (success/fail counts)
            - Leader loss detection with timeout
            - Periodic health reporting (every 30 seconds if debugging)

        Note:
            - Stops after first valid advertisement (one per burst)
            - Clears display after `_LOSS_TIMEOUT_S` without leader packets
        """
        found = False

        # Active scan to receive scan responses (name overflow)
        for adv in self.ble.start_scan(
                Advertisement, timeout=self._SCAN_BURST_S, minimum_rssi=-85, active=True
        ):
            adv_name = ""
            try:
                if getattr(adv, "complete_name", None):
                    adv_name = adv.complete_name
                elif getattr(adv, "short_name", None):
                    adv_name = adv.short_name
            except Exception:
                adv_name = ""

            if not adv_name or not adv_name.startswith("ILLO_"):
                continue

            parsed = self._parse_name(adv_name)
            if not parsed:
                self._sync_fail_count += 1
                continue

            found = True
            self._sync_success_count += 1
            self._last_seen_t = time.monotonic()

            # Only render new frames
            if self._last_seq is None or parsed["seq"] != self._last_seq:
                self._last_seq = parsed["seq"]
                self._render_triples(parsed["triples"])
                if self.debug_bluetooth and (self._last_seq % 20 == 0):
                    print("[DANCE] 🔗 sync seq=%d" % self._last_seq)

            break

        self.ble.stop_scan()

        # Periodic health report (every 30 seconds)
        now = time.monotonic()
        if self.debug_bluetooth and (now - self._last_health_report_t) >= 30.0:
            total = self._sync_success_count + self._sync_fail_count
            if total > 0:
                success_rate = (self._sync_success_count * 100) // total
                print("[DANCE] 📊 Sync health: %d%% success (%d/%d)" %
                      (success_rate, self._sync_success_count, total))
            self._last_health_report_t = now

        # Loss handling
        if not found and self._last_seen_t is not None:
            if (time.monotonic() - self._last_seen_t) >= self._LOSS_TIMEOUT_S:
                if self.debug_bluetooth:
                    print("[DANCE] ❌ leader lost — clearing")
                self._clear_pixels()
                self._last_seq = None

        time.sleep(0.003)

    def _parse_name(self, name):
        """Parse BLE advertisement name into visual state.

        Args:
            name (str): BLE advertisement name in ILLO protocol format

        Returns:
            dict or None: Dictionary with keys 'seq' (int) and 'triples' (list of tuples),
                or None if parsing failed or format invalid

        Format:
            ILLO_seq_p1_i1_c1_p2_i2_c2_p3_i3_c3

        Note:
            - Validates all values are within acceptable ranges
            - Replaces invalid triples with (0,0,0)
            - Returns None if name format is incorrect
        """
        try:
            parts = name.split("_")
            if len(parts) != 11:
                return None
            seq = int(parts[1])
            vals = [int(x) for x in parts[2:11]]
            triples = [(vals[0], vals[1], vals[2]),
                       (vals[3], vals[4], vals[5]),
                       (vals[6], vals[7], vals[8])]
            # Sanity clamp
            clean = []
            for (p, i, c) in triples:
                if 0 <= p < self._NUM_PIXELS and 0 <= i <= 255 and 0 <= c <= 2:
                    clean.append((p, i, c))
                else:
                    clean.append((0, 0, 0))
            return {"seq": seq, "triples": clean}
        except Exception:
            return None

    def _render_triples(self, triples):
        """Render received visual state to NeoPixels with smoothing.

        Args:
            triples (list): List of (position, intensity, color_type) tuples

        Note:
            - Rate-limited to `_MIN_RENDER_MS` to prevent thrashing
            - Uses exponential smoothing (`_SMOOTH_ALPHA`) for smooth transitions
            - Maps color types to RGB: 0=red, 1=green, 2=blue/pink
            - Clamps all output values to valid NeoPixel range (0-255)
        """
        # Rate-limit overall render to avoid thrash
        now = self._now_ms()
        if (now - self._last_render_ms) < self._MIN_RENDER_MS:
            return

        # Build target RGB for all 10 pixels from the 3 triples
        target = [[0, 0, 0] for _ in range(self._NUM_PIXELS)]
        for (pos, inten, ctype) in triples:
            pos = int(pos)
            inten = int(inten)
            ctype = int(ctype)

            if inten <= 0 or not (0 <= pos < self._NUM_PIXELS):
                continue

            # Map ILLO color types to RGB
            if ctype == 0:  # red-ish
                r = inten
                g = int(inten * 0.15)
                b = int(inten * 0.15)
                if r == 0 and inten > 0:
                    r = 1
            elif ctype == 1:  # green-ish
                r = int(inten * 0.15)
                g = inten
                b = int(inten * 0.15)
            else:  # blue/pink-ish
                r = int(inten * 0.30)
                g = int(inten * 0.05)
                b = inten

            target[pos] = [r, g, b]

        # Exponential smoothing toward target
        a = self._SMOOTH_ALPHA
        for i in range(self._NUM_PIXELS):
            sr, sg, sb = self._smooth_rgb[i]
            tr, tg, tb = target[i]
            sr = sr + (tr - sr) * a
            sg = sg + (tg - sg) * a
            sb = sb + (tb - sb) * a
            self._smooth_rgb[i] = [sr, sg, sb]
            # Cast + clamp for NeoPixel
            r = 0 if sr < 0 else (255 if sr > 255 else int(sr + 0.5))
            g = 0 if sg < 0 else (255 if sg > 255 else int(sg + 0.5))
            b = 0 if sb < 0 else (255 if sb > 255 else int(sb + 0.5))
            cp.pixels[i] = (r, g, b)

        cp.pixels.show()
        self._last_render_ms = now

    def _initialize_ble(self, is_leader=False):
        """Initialize BLE radio for leader or follower mode.

        Args:
            is_leader (bool, optional): True for leader mode, False for follower.
                Defaults to False.

        Note:
            - Leader mode seeds initial advertisement (may defer if error)
            - Sets `sync_active` flag on successful initialization
            - Safe to call multiple times (stops previous advertisement first)
        """
        try:
            self.ble = BLERadio()
            self.sync_active = True

            if is_leader:
                try:
                    name = "ILLO_0_0_0_0_0_0_0_0_0_0"
                    adv = Advertisement()
                    adv.complete_name = name
                    try:
                        self.ble.stop_advertising()
                    except Exception:
                        pass
                    self.ble.start_advertising(adv)
                except Exception as e:
                    if self.debug_bluetooth:
                        print("[DANCE] ⚠️ initial advertising deferred: %s" % e)

            if self.debug_bluetooth:
                print("[DANCE] ✅ BLE initialized")
        except Exception as e:
            print("[DANCE] ❌ BLE init failed: %s" % e)
            self.sync_active = False

    @staticmethod
    def _clear_pixels():
        """Clear all NeoPixels to black and update display."""
        cp.pixels.fill((0, 0, 0))
        cp.pixels.show()

    @staticmethod
    def _now_ms():
        """Get current monotonic time in milliseconds.

        Returns:
            int: Current time in milliseconds since boot
        """
        return int(time.monotonic() * 1000)

    def get_debug_status(self):
        """Return current status for debugging and monitoring.

        Returns:
            dict: Status dictionary with the following keys:
                - sync_active (bool): Whether BLE is initialized
                - seq (int): Current sequence number
                - free_memory (int): Available memory in bytes
                - sync_success (int): Successful sync count (follower)
                - sync_fail (int): Failed sync count (follower)
                - last_seen_age (float): Seconds since last leader packet (follower)

        Example:
            >>> dance = DanceParty("ILLO_01")
            >>> status = dance.get_debug_status()
            >>> print(status['free_memory'])
            45632
        """
        status = {
            'sync_active': self.sync_active,
            'seq': self._seq,
            'free_memory': gc.mem_free(),
            'sync_success': self._sync_success_count,
            'sync_fail': self._sync_fail_count
        }

        if self._last_seen_t:
            status['last_seen_age'] = time.monotonic() - self._last_seen_t

        return status

    @staticmethod
    def _load_dance_config():
        """Load configuration from ConfigManager or return defaults.

        Returns:
            dict: Configuration dictionary with at least 'bluetooth_enabled' key

        Note:
            Falls back to default config if ConfigManager unavailable
        """
        try:
            from config_manager import ConfigManager
            return ConfigManager().load_config()
        except Exception:
            return {'bluetooth_enabled': True}

    def cleanup(self):
        """Clean shutdown of Dance Party resources.

        Called by code.py when switching routines. Stops all BLE operations,
        clears NeoPixel display, and reports cleanup status if debugging.

        Note:
            - Safe to call multiple times
            - Catches and logs all exceptions during cleanup
            - Always attempts to clear pixels even if BLE cleanup fails
        """
        try:
            if self.ble:
                try:
                    self.ble.stop_advertising()
                except Exception:
                    pass
                try:
                    self.ble.stop_scan()
                except Exception:
                    pass

            self._clear_pixels()

            if self.debug_bluetooth:
                print("[DANCE] 🧹 Cleanup complete")

        except Exception as e:
            print("[DANCE] ⚠️ Cleanup error: %s" % e)