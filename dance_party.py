# Charles Doebler — Feral Cat AI
# Multi-UFO Synchronized Dance Party — Name-string BLE Sync (CPB nRF52840)
#
# Leader: expressive audio-reactive baton (head + 1 trail + optional spark on beats).
# Followers: mirror exactly those 3 pixels using ILLO_* advertisement name.
# No changes to code.py or Routine 2. No AdvertisementError import.

from base_routine import BaseRoutine
import time
import gc
from adafruit_circuitplayground import cp
from adafruit_ble import BLERadio
from adafruit_ble.advertising.standard import Advertisement

# Optional project audio helper (as in your repo)
try:
    from audio_processor import AudioProcessor
    _HAS_AUDIO = True
except Exception:
    _HAS_AUDIO = False


class DanceParty(BaseRoutine):
    """
    Leader/follower visual sync over BLE advertisement name.
    Protocol (unchanged):
      ILLO_<seq>_<pos1>_<int1>_<col1>_<pos2>_<int2>_<col2>_<pos3>_<int3>_<col3>
    """

    _NUM_PIXELS = 10
    _BRIGHTNESS = 0.20

    # Timing (slower, follower-friendly)
    _STEP_MS = 260           # visual step; adv matches this (≈3.8 revs/min)
    _ADV_PERIOD_MS = 260     # advertising refresh cadence (aligned with step)
    _SCAN_BURST_S = 0.35     # follower scan burst (active scan)
    _LOSS_TIMEOUT_S = 3.0    # follower loss detection
    _MIN_RENDER_MS = 30      # ~33 FPS cap (rate limit follower render)
    _SMOOTH_ALPHA = 0.65     # follower smoothing 0..1; higher = snappier

    def __init__(self, device_name, debug_bluetooth=False, debug_audio=False):
        super().__init__()
        self.device_name = device_name
        self.debug_bluetooth = bool(debug_bluetooth)
        self.debug_audio = bool(debug_audio)

        # Config
        self.config = self._load_dance_config()
        self.is_leader = bool(self.config.get('is_leader', False))
        self.sync_enabled = bool(self.config.get('bluetooth_enabled', True))

        # BLE
        self.ble = None
        self.sync_active = False
        self.sync_manager = None   # checked by code.py

        # Leader state
        self._seq = 0
        self._last_adv_ms = 0
        self._index = 0
        self._next_tick_ms = self._now_ms() + self._STEP_MS

        # Expressive motion state (leader)
        self._dir = 1                # +1 or -1
        self._gap = 1                # trail spacing (1 or 2)
        self._swing_ms = 0           # ± jitter applied to next step after beats
        self._beat_on = False
        self._beat_timer = 0         # frames remaining for "pop"
        self._spark_pos = None       # transient spark position (uses third triple)

        # Follower state
        self._last_seen_t = None
        self._last_seq = None

        # Audio
        self._audio_ok = False
        if _HAS_AUDIO:
            try:
                self.audio = AudioProcessor()
                self._audio_ok = True
            except Exception as e:
                if self.debug_audio:
                    print("[DANCE] ⚠️ Audio init failed:", e)
        # Smoothed energy, envelope & hysteretic color (leader)
        self._energy_lp = 120.0
        self._env = 120.0
        self._ctype = 2  # 0=red, 1=green, 2=blue/pink-ish

        # Pixels
        cp.pixels.auto_write = False
        cp.pixels.brightness = self._BRIGHTNESS
        self._clear_pixels()
        self._last_render_ms = 0
        # per-pixel smoothed RGB; RAM-safe (10 × 3 floats)
        self._smooth_rgb = [[0.0, 0.0, 0.0] for _ in range(self._NUM_PIXELS)]

        print("[DANCE] 🎵 Dance Party init — is_leader=%s, BLE=%s, audio=%s"
              % ("Y" if self.is_leader else "N",
                 "EN" if self.sync_enabled else "DIS",
                 "Y" if self._audio_ok else "N"))

        if self.sync_enabled:
            self._initialize_ble()
            if self.sync_active:
                self.sync_manager = self  # allow code.py to call enable_bluetooth()

    # -------- Code.py contract --------
    def enable_bluetooth(self):
        if self.sync_active:
            if self.debug_bluetooth:
                print("[DANCE] ✅ Bluetooth already active")
            return True
        try:
            self._initialize_ble()
            return self.sync_active
        except Exception as e:
            print("[DANCE] ❌ Bluetooth enable failed:", e)
            return False

    # -------- Main loop --------
    def run(self, mode, volume):
        if not self.sync_active:
            # Local fallback: still show audio baton if possible
            self._leader_frame()     # draw current frame
            self._advance_ring_if_due()
            return

        if self.is_leader:
            # Draw first, then handle BLE (keeps visuals smooth)
            self._leader_frame()
            self._advance_ring_if_due()
            self._leader_advertise_if_due()
        else:
            self._follower_loop()

        # light GC under debug
        if self.debug_bluetooth and (self._seq % 50 == 0):
            gc.collect()

        time.sleep(0.001)

    # -------- Leader visuals --------
    def _leader_frame(self):
        """Render an audio-reactive baton with expressive beat pops."""
        intensity = 140   # calmer default
        color_type = self._ctype

        if self._audio_ok:
            try:
                samples = self.audio.record_samples()
                if samples:
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
                        # Two-stage smoothing: fast LP + slower envelope
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
            except Exception as e:
                if self.debug_audio:
                    print("[DANCE] audio err:", e)

        # Lightweight beat detect from envelope movement
        beat_thr_on, beat_thr_off = 192, 168
        if not self._beat_on and intensity >= beat_thr_on:
            self._beat_on = True
            self._beat_timer = 2                 # pop for ~2 frames
            self._gap = 2                        # wider trail on beat
            self._swing_ms = int(self._STEP_MS * 0.08)  # tiny forward swing
            if intensity >= 224:
                self._dir = -self._dir           # flip direction on big beat
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

        # Convert color_type + intensity to RGB for local display
        def themed_rgb(inten, ctype):
            inten = int(inten)
            if inten <= 0:
                return (0, 0, 0)
            if ctype == 0:   # red-ish
                return (inten, int(inten * 0.15), int(inten * 0.15))
            elif ctype == 1: # green-ish
                return (int(inten * 0.15), inten, int(inten * 0.15))
            else:            # blue/pink-ish
                return (int(inten * 0.3), int(inten * 0.05), inten)

        # Draw leader pixels
        self._clear_pixels()
        cp.pixels[trail2] = themed_rgb(t2_int, color_type)
        cp.pixels[trail1] = themed_rgb(t1_int, color_type)
        cp.pixels[head_pos] = themed_rgb(head_int, color_type)
        cp.pixels.show()

        # Cache for advertisement build
        self._last_triples = [
            (head_pos, head_int, color_type),
            (trail1,  t1_int,   color_type),
            (trail2,  t2_int,   color_type),
        ]

        # Decay one-frame spark and beat pop
        if self._beat_timer > 0:
            self._beat_timer -= 1
        if self._beat_timer == 0:
            self._spark_pos = None

    def _advance_ring_if_due(self):
        t = self._now_ms()
        if t >= self._next_tick_ms:
            self._index = (self._index + self._dir) % self._NUM_PIXELS
            step = self._STEP_MS + (self._swing_ms if self._swing_ms else 0)
            self._next_tick_ms = t + step   # schedule from now to avoid drift
            self._swing_ms = 0

    # -------- Leader BLE --------
    def _leader_advertise_if_due(self):
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
        except Exception as e:
            if self.debug_bluetooth and (self._seq % 20 == 0):
                print("[DANCE] ⚠️ ADV restart suppressed:", e)
        finally:
            self._last_adv_ms = t

    def _build_adv_name_from_triples(self):
        # Use cached triples from the current frame; pad if needed
        triples = getattr(self, "_last_triples", [])
        while len(triples) < 3:
            triples.append((0, 0, 0))
        self._seq = (self._seq + 1) % 256
        (p1,i1,c1) = triples[0]
        (p2,i2,c2) = triples[1]
        (p3,i3,c3) = triples[2]
        name = "ILLO_%d_%d_%d_%d_%d_%d_%d_%d_%d_%d" % (
            self._seq, p1, i1, c1, p2, i2, c2, p3, i3, c3
        )
        if self.debug_bluetooth and (self._seq % 20 == 0):
            print("[DANCE] 📡 ADV:", name)
        return name

    # -------- Follower --------
    def _follower_loop(self):
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
                continue

            found = True
            self._last_seen_t = time.monotonic()

            # Only render new frames
            if self._last_seq is None or parsed["seq"] != self._last_seq:
                self._last_seq = parsed["seq"]
                self._render_triples(parsed["triples"])
                if self.debug_bluetooth and (self._last_seq % 20 == 0):
                    print("[DANCE] 🔗 sync seq=%d" % self._last_seq)

            break  # one good packet is enough per burst

        self.ble.stop_scan()

        # Loss handling
        if not found and self._last_seen_t is not None:
            if (time.monotonic() - self._last_seen_t) >= self._LOSS_TIMEOUT_S:
                if self.debug_bluetooth:
                    print("[DANCE] ❌ leader lost — clearing")
                self._clear_pixels()
                self._last_seq = None

        time.sleep(0.003)

    # -------- Parse & render --------
    def _parse_name(self, name):
        # ILLO_seq_p1_i1_c1_p2_i2_c2_p3_i3_c3
        try:
            parts = name.split("_")
            # Expect exactly 11 parts: "ILLO", seq, then 9 ints (p/i/c * 3)
            if len(parts) != 11:
                return None
            seq = int(parts[1])
            vals = [int(x) for x in parts[2:11]]  # nine ints
            triples = [(vals[0], vals[1], vals[2]),
                       (vals[3], vals[4], vals[5]),
                       (vals[6], vals[7], vals[8])]
            # sanity clamp
            clean = []
            for (p,i,c) in triples:
                if 0 <= p < self._NUM_PIXELS and 0 <= i <= 255 and 0 <= c <= 2:
                    clean.append((p,i,c))
                else:
                    clean.append((0,0,0))
            return {"seq": seq, "triples": clean}
        except Exception:
            return None

    def _render_triples(self, triples):
        # Rate-limit overall render to avoid thrash
        now = self._now_ms()
        if (now - self._last_render_ms) < self._MIN_RENDER_MS:
            return

        # Build target RGB for all 10 pixels from the 3 triples
        target = [[0, 0, 0] for _ in range(self._NUM_PIXELS)]
        for (pos, inten, ctype) in triples:
            # Extra defensive casts (some stacks hand back smallints that confuse linters)
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
                # Ensure at least a whisper of red survives rounding + brightness
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

        # Exponential smoothing toward target; keep floats internally
        a = self._SMOOTH_ALPHA
        for i in range(self._NUM_PIXELS):
            sr, sg, sb = self._smooth_rgb[i]
            tr, tg, tb = target[i]
            sr = sr + (tr - sr) * a
            sg = sg + (tg - sg) * a
            sb = sb + (tb - sb) * a
            self._smooth_rgb[i] = [sr, sg, sb]
            # cast + clamp for NeoPixel
            r = 0 if sr < 0 else (255 if sr > 255 else int(sr + 0.5))
            g = 0 if sg < 0 else (255 if sg > 255 else int(sg + 0.5))
            b = 0 if sb < 0 else (255 if sb > 255 else int(sb + 0.5))
            cp.pixels[i] = (r, g, b)

        cp.pixels.show()
        self._last_render_ms = now

    # -------- BLE init --------
    def _initialize_ble(self):
        try:
            self.ble = BLERadio()
            self.sync_active = True
            if self.is_leader:
                # Seed initial adv; if it fails, loop will retry
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
                        print("[DANCE] ⚠️ initial advertising deferred:", e)
            print("[DANCE] ✅ BLE ready (leader=%s)" % ("Y" if self.is_leader else "N"))
        except Exception as e:
            print("[DANCE] ❌ BLE init failed:", e)
            self.sync_active = False

    # -------- Pixels --------
    def _clear_pixels(self):
        cp.pixels.fill((0, 0, 0))
        cp.pixels.show()

    # -------- Utils --------
    @staticmethod
    def _now_ms():
        return int(time.monotonic() * 1000)

    def _load_dance_config(self):
        try:
            from config_manager import ConfigManager
            return ConfigManager().load_config()
        except Exception:
            return {'is_leader': False, 'bluetooth_enabled': True}
