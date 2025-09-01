# Charles Doebler at Feral Cat AI

# Button A cycles through routines (1-4)
# Button B cycles through color modes (1-4) 
# Switch position controls volume (True/False)
# NeoPixel ring represents UFO lighting effects
# Microphone input creates reactive light patterns
# Accelerometer shake detection for "turbulence" effects

from adafruit_circuitplayground import cp
import time
from config_manager import ConfigManager
from memory_manager import MemoryManager
from interaction_manager import InteractionManager
import os

# Debug Configuration - Set these flags to enable debug output
debug_bluetooth = False  # Enable Bluetooth debug messages
debug_audio = False  # Enable audio processing debug messages
debug_memory = True  # Enable memory usage monitoring
debug_interactions = False  # Enable interaction debug messages

def _fs_writable_check():
    """Return True if CIRCUITPY is writable, False if USB RO is active."""
    test_path = "._writetest.tmp"
    try:
        with open(test_path, "wb") as f:
            f.write(b"x")
        os.remove(test_path)
        return True
    except OSError:
        return False


def show_routine_feedback(routine):
    """Display visual feedback for routine selection."""
    cp.pixels.fill((0, 0, 0))  # Clear all pixels

    # Define routine colors and names
    routine_info = {
        1: {"color": (100, 0, 255), "name": "UFO Intelligence"},  # Purple
        2: {"color": (0, 255, 100), "name": "Intergalactic Cruising"},  # Green
        3: {"color": (0, 100, 255), "name": "Meditate"},  # Blue
        4: {"color": (255, 100, 0), "name": "Dance Party"}  # Orange
    }

    info = routine_info.get(routine, {"color": (255, 255, 255), "name": "Unknown"})

    # Light up pixels equal to the routine number
    for i in range(routine):
        cp.pixels[i] = info["color"]

    cp.pixels.show()
    print("🚀 Routine %d: %s" % (routine, info["name"]))


def show_mode_feedback(mode):
    """Display visual feedback for mode selection."""
    cp.pixels.fill((0, 0, 0))  # Clear all pixels

    # Define mode colors and names
    mode_info = {
        1: {"color": (255, 0, 0), "name": "Rainbow Wheel"},  # Red base
        2: {"color": (255, 0, 255), "name": "Pink Theme"},  # Pink base
        3: {"color": (0, 0, 255), "name": "Blue Theme"},  # Blue base
        4: {"color": (0, 255, 0), "name": "Green Theme"}  # Green base
    }

    info = mode_info.get(mode, {"color": (255, 255, 255), "name": "Unknown"})

    # Show mode with different patterns - spread pixels around the ring
    positions = [0, 3, 6, 9]  # Spread around a 10-pixel ring
    for i in range(mode):
        if i < len(positions):
            cp.pixels[positions[i]] = info["color"]

    cp.pixels.show()
    print("🎨 Mode %d: %s" % (mode, info["name"]))


def main():
    """Main application loop."""
    # Initialize managers
    config_mgr = ConfigManager()
    config = config_mgr.load_config()
    memory_mgr = MemoryManager(enable_debug=debug_memory)
    interaction_mgr = InteractionManager(enable_debug=debug_interactions)

    # Extract configuration values
    routine = config['routine']
    mode = config['mode']
    name = config['name']
    college_spirit_enabled = config['college_spirit_enabled']
    college = config['college']
    ufo_persistent_memory = config['ufo_persistent_memory']
    college_chant_detection_enabled = config['college_chant_detection_enabled']
    bluetooth_enabled = config['bluetooth_enabled']

    # System initialization
    _fs_is_writable = _fs_writable_check()
    _persist_this_run = bool(ufo_persistent_memory and _fs_is_writable)

    # State variables
    current_routine_instance = None
    active_routine_number = 0
    last_button_a_time = 0
    last_button_b_time = 0
    button_debounce_delay = 0.3
    config_save_timer = 0
    config_changed = False

    # Display startup status
    actual_volume = cp.switch
    print("🛸 UFO System Initialized")
    print("📋 Current: Routine %d, Mode %d, Sound %s" % (routine, mode,
                                                        "ON" if actual_volume else "OFF"))

    # Show persistent memory status
    if ufo_persistent_memory and not _fs_is_writable:
        print("💾 Persistent memory REQUESTED but DISABLED (USB write-protect detected)")
    elif _persist_this_run:
        print(
            "💾 Persistent memory ENABLED — Illo will remember personality across sessions")
    else:
        print("💾 Persistent memory DISABLED — Illo resets personality each session")

    cp.detect_taps = 1

    # Main loop
    while True:
        current_time = time.monotonic()
        volume = cp.switch

        # Routine management - lazy instantiation
        if routine != active_routine_number:
            if current_routine_instance:
                memory_mgr.cleanup_before_routine_change()
                del current_routine_instance
                
                # Force garbage collection after deleting heavy routine
                import gc
                gc.collect()
                print("[SYSTEM] Memory freed, available: %d bytes" % gc.mem_free())

            interaction_mgr.setup_for_routine(routine)
            current_routine_instance = create_routine_instance(
                routine, name, _persist_this_run, college_spirit_enabled, 
                college, bluetooth_enabled, debug_bluetooth, debug_audio
            )
            
            if current_routine_instance:
                active_routine_number = routine
                print(" Loaded routine %d" % routine)
            else:
                print(" Failed to load routine %d" % routine)

        # Interaction detection
        interactions = interaction_mgr.check_interactions(routine, volume, cp.pixels)
        handle_ufo_intelligence_learning(routine, current_routine_instance,
                                         interactions)

        # Button handling
        routine, mode, last_button_a_time, last_button_b_time, button_config_changed = handle_button_interactions(
            routine, mode, last_button_a_time, last_button_b_time,
            button_debounce_delay, current_time
        )

        if button_config_changed:
            config_changed = True
            config_save_timer = current_time

        # Configuration saving
        if config_changed and (current_time - config_save_timer > 2.0):
            config.update({
                'routine': routine,
                'mode': mode,
                'name': name,
                'college_spirit_enabled': college_spirit_enabled,
                'college': college,
                'ufo_persistent_memory': ufo_persistent_memory,
                'college_chant_detection_enabled': college_chant_detection_enabled,
                'bluetooth_enabled': bluetooth_enabled
            })
            config_mgr.save_config(config)
            config_changed = False

        # System maintenance
        memory_mgr.periodic_cleanup()

        # Execute routine
        if current_routine_instance:
            current_routine_instance.run(mode, volume)


def create_routine_instance(routine, name, _persist_this_run, college_spirit_enabled,
                            college, bluetooth_enabled, bt_debug, audio_debug):
    """
    Create a routine instance based on routine number.
    Uses lazy imports to save memory by only loading needed routines.
    
    Args:
        routine: Routine number (1-4)
        name: Device name
        _persist_this_run: Whether to enable persistent memory
        college_spirit_enabled: Whether college spirit is enabled
        college: College name
        bluetooth_enabled: Whether Bluetooth is enabled in config
        bt_debug: Bluetooth debug flag
        audio_debug: Audio debug flag
    
    Returns:
        routine instance or None
    """
    try:
        if routine == 1:
            print("[SYSTEM] Loading UFO Intelligence (heavy memory usage)...")
            from ufo_intelligence import UFOIntelligence
            return UFOIntelligence(
                device_name=name,
                persistent_memory=_persist_this_run,
                college_spirit_enabled=college_spirit_enabled,
                college=college
            )
        elif routine == 2:
            print("[SYSTEM] Loading Intergalactic Cruising...")
            from intergalactic_cruising import IntergalacticCruising
            instance = IntergalacticCruising()
            
            # Only enable Bluetooth if both config allows it AND it was initialized
            if bluetooth_enabled and hasattr(instance, 'bluetooth') and instance.bluetooth:
                print("[SYSTEM] 📱 Enabling Bluetooth control...")
                instance.enable_bluetooth()
                instance.enable_debug()  # This enables debug for both cruiser and bluetooth
            else:
                print("[SYSTEM] 🏃 High-performance mode (Bluetooth disabled)")
            
            return instance
        elif routine == 3:
            print("[SYSTEM] Loading Meditate...")
            from meditate import Meditate
            return Meditate()
        elif routine == 4:
            print("[SYSTEM] Loading Dance Party...")
            from dance_party import DanceParty
            return DanceParty(name, bt_debug, audio_debug)
        else:
            return None
    except MemoryError as e:
        print("[SYSTEM] ❌ Memory error loading routine %d: %s" % (routine, str(e)))
        print("[SYSTEM] 💡 Try restarting or using a simpler routine")
        return None
    except Exception as e:
        print("[SYSTEM] ❌ Error loading routine %d: %s" % (routine, str(e)))
        return None


def handle_button_interactions(routine, mode, last_button_a_time, last_button_b_time,
                               button_debounce_delay, current_time):
    """
    Handle button A and B interactions with debouncing.
    
    Returns:
        tuple: (new_routine, new_mode, new_last_button_a_time, new_last_button_b_time, config_changed)
    """
    config_changed = False

    # Handle button A: cycle through routines with debouncing
    if cp.button_a and (current_time - last_button_a_time > button_debounce_delay):
        routine = (routine % 4) + 1  # Cycle through routines 1-4
        show_routine_feedback(routine)
        last_button_a_time = current_time
        config_changed = True

        # Brief delay to show feedback, then clear
        time.sleep(0.8)
        cp.pixels.fill((0, 0, 0))
        cp.pixels.show()

    # Handle button B: cycle through color modes with debouncing
    if cp.button_b and (current_time - last_button_b_time > button_debounce_delay):
        mode = (mode % 4) + 1  # Cycle through modes 1-4
        show_mode_feedback(mode)
        last_button_b_time = current_time
        config_changed = True

        # Brief delay to show feedback, then clear
        time.sleep(0.8)
        cp.pixels.fill((0, 0, 0))
        cp.pixels.show()

    return routine, mode, last_button_a_time, last_button_b_time, config_changed


def handle_ufo_intelligence_learning(routine, current_routine_instance, interactions):
    """
    Handle UFO Intelligence learning from interactions.
    
    Args:
        routine: Current routine number
        current_routine_instance: The active routine instance
        interactions: Dictionary of detected interactions
    """
    if routine != 1 or not current_routine_instance:
        return

    # Pass interactions to UFO Intelligence for learning
    if interactions['tap'] or interactions['shake']:
        current_routine_instance.last_interaction = time.monotonic()
        if current_routine_instance.mood == "curious":
            current_routine_instance.record_successful_attention()

    if interactions['shake']:
        current_routine_instance.energy_level = min(100,
                                                    current_routine_instance.energy_level + 15)


if __name__ == "__main__":
    main()
