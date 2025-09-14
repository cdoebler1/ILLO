# ILLO Routine 4 — Dance Party BLE Sync (CPB Bluefruit, nRF52840)
# Role via config.json: {"is_leader": true/false}
# Leader: broadcasts revolving ROYGBIV colors @ 60 BPM (10 steps/second), followers mirror.

import time
import json
import microcontroller
import supervisor

from adafruit_circuitplayground import cp
from adafruit_ble import BLERadio
from adafruit_ble.advertising.standard import Advertisement

# ------------------------
# Config & constants
# ------------------------
CONFIG_PATH = "/config.json"
DEFAULT_IS_LEADER = False

# ROYGBIV color sequence for visibility testing
ROYGBIV_COLORS = [
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

# Adjust brightness for current safety
BRIGHTNESS_FACTOR = 0.3
OFF = (0, 0, 0)
NUM_PIXELS = 10
GLOBAL_BRIGHTNESS = 0.2

# Beat timing
BPM = 60
STEP_MS = int(1000 / NUM_PIXELS)  # 100 ms per index for 10 steps in 1s

# Follower timing
RX_BIAS_MS = 50  # estimate of radio/ISR delay; tweak after testing
LOSS_TIMEOUT_S = 3.0  # consider link "lost" if no packets for this long


# ------------------------
# Utils
# ------------------------
def load_config():
    try:
        with open(CONFIG_PATH, "r") as f:
            cfg = json.load(f)
            return bool(cfg.get("is_leader", DEFAULT_IS_LEADER))
    except Exception:
        return DEFAULT_IS_LEADER


def now_ms():
    return int(time.monotonic() * 1000)


def scale_color(rgb, factor):
    return tuple(int(c * factor) for c in rgb)


def set_ring_roygbiv(index):
    current_color = scale_color(ROYGBIV_COLORS[index], BRIGHTNESS_FACTOR)
    for i in range(NUM_PIXELS):
        cp.pixels[i] = current_color if i == index else OFF
    cp.pixels.show()


def clear_ring():
    cp.pixels.fill(OFF)
    cp.pixels.show()


def flash_sync_indicator():
    """Flash all pixels white briefly to indicate sync"""
    cp.pixels.fill((50, 50, 50))  # Dim white
    cp.pixels.show()
    time.sleep(0.05)
    cp.pixels.fill(OFF)
    cp.pixels.show()


def parse_illo_name(name):
    """Parse ILLO advertisement name: ILLO_INDEX_SEQ_TNEXT_R_G_B"""
    if not name.startswith("ILLO_"):
        return None

    try:
        parts = name.split("_")
        if len(parts) != 7:  # ILLO, INDEX, SEQ, TNEXT, R, G, B
            return None

        index = int(parts[1])
        seq = int(parts[2])
        t_next_ms = int(parts[3])
        r = int(parts[4])
        g = int(parts[5])
        b = int(parts[6])

        if index >= NUM_PIXELS:
            return None

        return {
            "seq": seq,
            "index": index,
            "t_next_ms": t_next_ms,
            "rgb": (r, g, b)
        }
    except:
        return None


def create_illo_name(index, seq, t_next_ms, rgb):
    """Create ILLO advertisement name: ILLO_INDEX_SEQ_TNEXT_R_G_B"""
    r, g, b = rgb
    return f"ILLO_{index}_{seq}_{t_next_ms}_{int(r)}_{int(g)}_{int(b)}"


# ------------------------
# Roles
# ------------------------
def run_leader():
    print("🎯 LEADER: Starting ROYGBIV color sync...")
    ble = BLERadio()
    print(f"BLE radio initialized")

    # Visual safety
    cp.pixels.auto_write = False
    cp.pixels.brightness = GLOBAL_BRIGHTNESS

    # Timing init
    seq = 0
    index = 0
    last_tick_ms = now_ms()
    next_tick_ms = last_tick_ms + STEP_MS
    last_adv_time = 0

    # Show the ring locally
    set_ring_roygbiv(index)
    color_names = ["Red", "Orange-Red", "Orange", "Gold", "Yellow", "Green-Yellow",
                   "Green", "Cyan", "Dodger-Blue", "Royal-Blue"]

    print("🎯 LEADER: Starting ROYGBIV broadcast...")

    while True:
        t = now_ms()

        # Advance index on tick
        if t >= next_tick_ms:
            index = (index + 1) % NUM_PIXELS
            set_ring_roygbiv(index)
            last_tick_ms = next_tick_ms
            next_tick_ms = last_tick_ms + STEP_MS
            print(f"🎨 LEADER: Step {index} - {color_names[index]}")

        # Advertise every 200ms
        if t - last_adv_time > 200:
            try:
                seq = (seq + 1) % 256
                current_color = scale_color(ROYGBIV_COLORS[index], BRIGHTNESS_FACTOR)
                t_to_next = max(0, next_tick_ms - t)

                # Create advertisement name with sync data
                adv_name = create_illo_name(index, seq, t_to_next, current_color)

                # Create and send advertisement
                adv = Advertisement()
                adv.complete_name = adv_name

                try:
                    ble.stop_advertising()
                except:
                    pass

                ble.start_advertising(adv)
                print(
                    f"📡 LEADER: Broadcast seq={seq}, index={index}, t_next={t_to_next}ms")

                last_adv_time = t

            except Exception as e:
                print(f"❌ LEADER: Error: {e}")

        time.sleep(0.01)


def run_follower():
    print("🔍 FOLLOWER: Starting sync scan...")
    ble = BLERadio()

    # Visual safety
    cp.pixels.auto_write = False
    cp.pixels.brightness = GLOBAL_BRIGHTNESS
    clear_ring()

    last_seen_t = None
    last_seq = None
    sync_count = 0
    scan_count = 0

    # Local tick scheduling
    index = 0
    next_tick_ms = None
    tick_period_ms = STEP_MS
    color_names = ["Red", "Orange-Red", "Orange", "Gold", "Yellow", "Green-Yellow",
                   "Green", "Cyan", "Dodger-Blue", "Royal-Blue"]

    while True:
        found_leader = False
        scan_count += 1
        print(f"🔍 FOLLOWER: Scan #{scan_count}...")

        for adv in ble.start_scan(Advertisement, timeout=1.0, minimum_rssi=-120):
            # Get advertisement name
            adv_name = ''
            if hasattr(adv, 'complete_name') and adv.complete_name:
                adv_name = adv.complete_name
            elif hasattr(adv, 'short_name') and adv.short_name:
                adv_name = adv.short_name

            # Look for ILLO advertisements
            if adv_name.startswith("ILLO_"):
                parsed = parse_illo_name(adv_name)
                if parsed:
                    print(
                        f"📡 SYNC DATA: seq={parsed['seq']}, index={parsed['index']} ({color_names[parsed['index']]}), t_next={parsed['t_next_ms']}ms")

                    found_leader = True
                    current_time = time.monotonic()
                    last_seen_t = current_time

                    # Check if this is a new sequence (new sync event)
                    if last_seq is None or parsed["seq"] != last_seq:
                        sync_count += 1
                        flash_sync_indicator()  # Visual sync indicator
                        print(f"🎯 SYNC #{sync_count}: New sequence from leader!")
                        last_seq = parsed["seq"]

                    # IMMEDIATELY adopt leader's state - this is the key fix!
                    index = parsed["index"]
                    received_color = parsed["rgb"]
                    tnext = parsed["t_next_ms"]

                    # Show the leader's current state immediately
                    print(f"🎨 FOLLOWER: Syncing to Step {index} - {color_names[index]}")
                    for i in range(NUM_PIXELS):
                        cp.pixels[i] = received_color if i == index else OFF
                    cp.pixels.show()

                    # Calculate when the NEXT step should happen
                    t_now_ms = now_ms()
                    next_tick_ms = t_now_ms + max(50,
                                                  int(tnext) - RX_BIAS_MS)  # Ensure at least 50ms

                    print(f"⏰ FOLLOWER: Next step in {int(tnext) - RX_BIAS_MS}ms")

                    # Once we've found our leader, break out of scan
                    break

        ble.stop_scan()

        if not found_leader:
            print("🔍 FOLLOWER: No leader found")

        # If we've locked at least once, run the local schedule
        if next_tick_ms is not None:
            t = now_ms()
            if t >= next_tick_ms:
                # Step to next index locally
                index = (index + 1) % NUM_PIXELS
                current_color = scale_color(ROYGBIV_COLORS[index], BRIGHTNESS_FACTOR)
                for i in range(NUM_PIXELS):
                    cp.pixels[i] = current_color if i == index else OFF
                cp.pixels.show()
                next_tick_ms = t + tick_period_ms
                print(f"⏰ LOCAL: Step {index} - {color_names[index]}")

        # Detect temporary loss
        if last_seen_t is not None and (
                time.monotonic() - last_seen_t) >= LOSS_TIMEOUT_S:
            print("❌ FOLLOWER: Lost leader signal")
            clear_ring()
            next_tick_ms = None  # stop local ticks until re-lock
            last_seq = None  # Reset sequence tracking

        time.sleep(0.5)

# ------------------------
# Entry
# ------------------------
def main():
    is_leader = load_config()
    print(f"🚀 Starting in {'LEADER' if is_leader else 'FOLLOWER'} mode")

    try:
        if is_leader:
            run_leader()
        else:
            run_follower()
    except Exception as e:
        clear_ring()
        print("Exception:", e)
        time.sleep(0.5)
        supervisor.reload()


if __name__ == "__main__":
    main()