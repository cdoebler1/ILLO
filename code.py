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


class TaskScheduler:
    """
    Simple task scheduler for managing periodic operations.
    Optimizes performance by controlling when different operations run.
    """

    def __init__(self):
        """Initialize the task scheduler."""
        self.tasks = {}
        self.last_run = {}

    def add_task(self, name, interval, callback, enabled=True):
        """
        Add a scheduled task.
        
        Args:
            name: Task identifier
            interval: Seconds between executions
            callback: Function to call
            enabled: Whether a task is initially enabled
        """
        self.tasks[name] = {
            'interval': interval,
            'callback': callback,
            'enabled': enabled
        }
        self.last_run[name] = 0

    def enable_task(self, name):
        """Enable a scheduled task."""
        if name in self.tasks:
            self.tasks[name]['enabled'] = True

    def disable_task(self, name):
        """Disable a scheduled task."""
        if name in self.tasks:
            self.tasks[name]['enabled'] = False

    def run_due_tasks(self, current_time):
        """
        Run all tasks that are due to execute.
        
        Args:
            current_time: Current monotonic time
            
        Returns:
            List of task names that were executed
        """
        executed_tasks = []

        for name, task in self.tasks.items():
            if not task['enabled']:
                continue

            if current_time - self.last_run[name] >= task['interval']:
                try:
                    task['callback']()
                    self.last_run[name] = current_time
                    executed_tasks.append(name)
                except Exception as e:
                    print("[SCHEDULER] ❌ Task %s failed: %s" % (name, str(e)))

        return executed_tasks


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
    """Main application loop with task scheduling."""
    # Initialize managers
    config_mgr = ConfigManager()
    config = config_mgr.load_config()
    memory_mgr = MemoryManager(enable_debug=debug_memory)
    interaction_mgr = InteractionManager(enable_debug=debug_interactions)

    # Initialize scheduler
    scheduler = TaskScheduler()

    # Extract all configuration values upfront
    routine = config.get('routine', 1)
    mode = config.get('mode', 1)
    _name = config.get('name', 'ILLO')  # Passed via config dict to routines
    _bluetooth_enabled = config.get('bluetooth_enabled', True)  # Passed via config dict
    _college = config.get('college', 'none')  # Passed via config dict
    _college_spirit_enabled = config.get('college_spirit_enabled', False)  # Passed via config dict
    ufo_persistent_memory = config.get('ufo_persistent_memory', False)
    _meditate_adaptive_timing = config.get('meditate_adaptive_timing', True)  # Passed via config dict
    _meditate_ultra_dim = config.get('meditate_ultra_dim', True)  # Passed via config dict
    _college_chant_detection_enabled = config.get('college_chant_detection_enabled', False)  # Reserved for future use

    # System initialization
    _fs_is_writable = _fs_writable_check()
    _persist_this_run = bool(ufo_persistent_memory and _fs_is_writable)

    # State variables
    current_routine_instance = None
    active_routine_number = 0
    last_button_a_time = 0
    last_button_b_time = 0
    button_debounce_delay = 0.3
    config_changed = False

    # Scheduled task functions
    def memory_cleanup_task():
        """Periodic memory cleanup task."""
        memory_mgr.periodic_cleanup()

    def config_save_task():
        """Save configuration if changes are pending."""
        nonlocal config_changed, config
        if config_changed:
            # Update the config dictionary with current values before saving
            config['routine'] = routine
            config['mode'] = mode
            # ConfigManager.save_config() handles field extraction and defaults
            config_mgr.save_config(config)
            config_changed = False
            print("[SCHEDULER] 💾 Config auto-saved")

    def system_status_task():
        """Periodic system status reporting."""
        import gc
        print("[SCHEDULER] 📊 Memory: %d bytes free, Routine: %d, Mode: %d" %
              (gc.mem_free(), routine, mode))

    # Setup of scheduled tasks
    scheduler.add_task('memory_cleanup', 30.0, memory_cleanup_task)  # Every 30 seconds
    scheduler.add_task('config_save', 3.0, config_save_task)  # Every 3 seconds
    scheduler.add_task('system_status', 60.0, system_status_task, enabled=debug_memory)  # Every minute if debug enabled

    # Display startup status
    actual_volume = cp.switch
    print("🛸 UFO System Initialized with Task Scheduler")
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

    # Performance monitoring
    loop_start_time = time.monotonic()
    loop_count = 0
    performance_report_interval = 100  # Report every 100 loops

    # Main loop with scheduling
    while True:
        current_time = time.monotonic()
        volume = cp.switch
        loop_count += 1

        # Routine management - lazy instantiation
        if routine != active_routine_number:
            if current_routine_instance:
                # Call a cleanup method if available
                if hasattr(current_routine_instance, 'cleanup'):
                    current_routine_instance.cleanup()

                memory_mgr.cleanup_before_routine_change()
                del current_routine_instance

                # Force garbage collection after deleting a heavy routine
                import gc
                gc.collect()
                print("[SYSTEM] Memory freed, available: %d bytes" % gc.mem_free())

            interaction_mgr.setup_for_routine(routine)
            current_routine_instance = create_routine_instance(
                routine, config, debug_bluetooth, debug_audio
            )

            if current_routine_instance:
                active_routine_number = routine
                print("✅ Loaded routine %d" % routine)

                # Adjust task scheduling based on routine
                if routine == 1:  # UFO Intelligence - more frequent cleanup
                    scheduler.tasks['memory_cleanup']['interval'] = 20.0
                else:  # Other routines - standard cleanup
                    scheduler.tasks['memory_cleanup']['interval'] = 30.0
            else:
                print("❌ Failed to load routine %d" % routine)

        # Interaction detection (high priority - run every loop)
        interactions = interaction_mgr.check_interactions(routine, volume, cp.pixels)
        handle_ufo_intelligence_learning(routine, current_routine_instance,
                                         interactions)

        # Button handling (high priority - run every loop)
        new_routine, new_mode, last_button_a_time, last_button_b_time, button_config_changed = handle_button_interactions(
            routine, mode, last_button_a_time, last_button_b_time,
            button_debounce_delay, current_time
        )

        # Update variables if changed (Button A will reboot, so this mainly handles Button B)
        if new_routine != routine:
            # This should rarely execute since Button A reboots
            routine = new_routine
            config['routine'] = routine  # Update config dict

        if new_mode != mode:
            mode = new_mode
            config['mode'] = mode  # Update config dict

        if button_config_changed:
            config_changed = True

        # Execute routine (high priority - run every loop)
        if current_routine_instance:
            current_routine_instance.run(mode, volume)

        # Performance reporting (low priority - scheduled)
        if debug_memory and loop_count % performance_report_interval == 0:
            elapsed = current_time - loop_start_time
            if elapsed > 0:
                loops_per_second = performance_report_interval / elapsed
                print("[SCHEDULER] 🚀 Performance: %.1f loops/sec" % loops_per_second)
            loop_start_time = current_time


def create_routine_instance(routine, config, bt_debug, audio_debug):
    """
    Create a routine instance based on a routine number.
    Uses lazy imports to save memory by only loading the necessary routines.
    
    Args:
        routine: Routine number (1-4)
        config: Configuration dictionary with all settings
        bt_debug: Bluetooth debug flag
        audio_debug: Audio debug flag
    
    Returns:
        routine instance or None
    """
    instance = None

    # Extract configuration values needed by routines
    name = config.get('name', 'ILLO')
    bluetooth_enabled = config.get('bluetooth_enabled', True)
    college_spirit_enabled = config.get('college_spirit_enabled', False)
    college = config.get('college', 'none')
    ufo_persistent_memory = config.get('ufo_persistent_memory', False)
    meditate_adaptive_timing = config.get('meditate_adaptive_timing', True)
    meditate_ultra_dim = config.get('meditate_ultra_dim', True)
    # Note: is_leader removed - Dance Party now uses mode value

    # System initialization for UFO Intelligence
    _fs_is_writable = _fs_writable_check() if routine == 1 else False
    _persist_this_run = bool(ufo_persistent_memory and _fs_is_writable)

    try:
        if routine == 1:
            print("[SYSTEM] Loading UFO Intelligence (heavy memory usage)...")
            from ufo_intelligence import UFOIntelligence
            instance = UFOIntelligence(
                device_name=name,
                debug_bluetooth=bt_debug,
                debug_audio=audio_debug,
                persistent_memory=_persist_this_run,
                college_spirit_enabled=college_spirit_enabled,
                college=college
            )
            # Check if instance initialized properly using hasattr to avoid method dependency
            if hasattr(instance, 'ai_core') and hasattr(instance,
                                                        'behaviors') and hasattr(
                instance, 'learning'):
                if instance.ai_core is None or instance.behaviors is None or instance.learning is None:
                    print(
                        "[SYSTEM] ❌ UFO Intelligence failed to initialize critical systems")
                    if hasattr(instance, 'cleanup'):
                        instance.cleanup()
                    return None
        elif routine == 2:
            print("[SYSTEM] Loading Intergalactic Cruising...")
            from intergalactic_cruising import IntergalacticCruising
            instance = IntergalacticCruising()

            # Only enable Bluetooth if the config allows it AND it was initialized
            if bluetooth_enabled and hasattr(instance,
                                             'bluetooth') and instance.bluetooth:
                print("[SYSTEM] 📱 Enabling Bluetooth control...")
                instance.enable_bluetooth()
            else:
                print("[SYSTEM] 🏃 High-performance mode (Bluetooth disabled)")

        elif routine == 3:
            print("[SYSTEM] Loading Meditate...")
            from meditate import Meditate
            instance = Meditate(
                adaptive_timing=meditate_adaptive_timing,
                ultra_dim=meditate_ultra_dim
            )

        elif routine == 4:
            print("[SYSTEM] Loading Dance Party...")
            from dance_party import DanceParty
            # Dance Party now determines leader/follower from mode value
            instance = DanceParty(
                name,
                bt_debug,
                audio_debug
            )

            # Enable Bluetooth for Dance Party if configured and available
            if bluetooth_enabled and hasattr(instance, 'enable_bluetooth'):
                print("[SYSTEM] 📱 Enabling Bluetooth for Dance Party sync...")
                success = instance.enable_bluetooth()
                if success:
                    print("[SYSTEM] ✅ Dance Party Bluetooth sync enabled")
                    print("[SYSTEM] 💃 Role will be determined by Button B (Mode 1=Leader, Mode 2=Follower)")
                else:
                    print("[SYSTEM] ❌ Failed to enable Dance Party Bluetooth")
            else:
                print("[SYSTEM] 🏃 Dance Party in standalone mode (Bluetooth disabled)")
                if not bluetooth_enabled:
                    print("[SYSTEM]   Reason: Bluetooth disabled in config")

            # Show dance configuration if debug enabled
            if bt_debug:
                print("[SYSTEM] Dance Party ready with beat detection")

        return instance

    except MemoryError as e:
        print("[SYSTEM] ❌ Memory error loading routine %d: %s" % (routine, str(e)))
        print("[SYSTEM] 💡 Try restarting or using a simpler routine")
        if instance and hasattr(instance, 'cleanup'):
            instance.cleanup()
        return None
    except Exception as e:
        print("[SYSTEM] ❌ Error loading routine %d: %s" % (routine, str(e)))
        if instance and hasattr(instance, 'cleanup'):
            instance.cleanup()
        return None


def handle_meditation_pattern_change():
    """DEPRECATED: Handle Button B press during meditation to change breathing patterns."""
    # This function is deprecated as meditation now uses standard mode changes via Button B
    # Kept for backward compatibility but does nothing
    print("[MEDITATE] ⚠️ Breathing pattern now controlled by standard mode selection (Button B)")
    return None


def handle_button_interactions(routine, mode, last_button_a_time, last_button_b_time,
                               button_debounce_delay, current_time):
    """
    Handle button A and B interactions with debouncing.
    Button A now saves config and reboots for clean routine switching.
    Button B cycles through color modes (1-4) for ALL routines including Meditation.

    Returns:
        tuple: (new_routine, new_mode, new_last_button_a_time, new_last_button_b_time, config_changed)
    """
    config_changed = False

    # Handle button A: cycle through routines with immediate save and reboot
    if cp.button_a and (current_time - last_button_a_time > button_debounce_delay):
        new_routine = (routine % 4) + 1  # Cycle through routines 1-4

        # Show feedback for the new routine selection
        show_routine_feedback(new_routine)
        print("🔄 Switching to routine %d - saving and rebooting..." % new_routine)

        # Immediately save the new routine to config
        try:
            from config_manager import ConfigManager
            config_mgr = ConfigManager()
            config = config_mgr.load_config()

            # Update routine in config
            config['routine'] = new_routine
            success = config_mgr.save_config(config)

            if success:
                print("💾 Routine %d saved to config successfully" % new_routine)

                # Brief pause to show feedback and ensure save completes
                time.sleep(1.5)

                # Clear pixels before reboot
                cp.pixels.fill((0, 0, 0))
                cp.pixels.show()

                print("🚀 Rebooting for clean routine switch...")
                time.sleep(0.5)  # Brief pause for the user to see a message

                # Perform soft reset
                import microcontroller
                microcontroller.reset()

            else:
                print("❌ Failed to save routine, continuing without reboot")
                config_changed = True  # Fall back to normal config save behavior

        except Exception as e:
            print("❌ Error during routine save: %s" % str(e))
            print("Continuing without reboot...")
            config_changed = True  # Fall back to normal behavior

        last_button_a_time = current_time

        # If we reach here, the save failed, and we're falling back to normal behavior
        time.sleep(0.8)
        cp.pixels.fill((0, 0, 0))
        cp.pixels.show()
        routine = new_routine

    # Handle button B: change color modes for ALL routines (including Meditation)
    if cp.button_b and (current_time - last_button_b_time > button_debounce_delay):
        mode = (mode % 4) + 1  # Cycle through modes 1-4
        show_mode_feedback(mode)
        config_changed = True

        # For Meditation routine, show breathing pattern feedback
        if routine == 3:
            show_breathing_pattern_feedback(mode)
            print("[MEDITATE] 🧘 Mode %d = %s" % (mode, {
                1: "4-7-8 Breathing",
                2: "Box Breathing",
                3: "Triangle Breathing",
                4: "Deep Relaxation"
            }.get(mode, "Unknown")))

        # Brief delay to show feedback, then clear
        time.sleep(0.8)
        cp.pixels.fill((0, 0, 0))
        cp.pixels.show()

        last_button_b_time = current_time

    return routine, mode, last_button_a_time, last_button_b_time, config_changed


def show_breathing_pattern_feedback(pattern):
    """Display visual feedback for breathing pattern selection."""
    cp.pixels.fill((0, 0, 0))  # Clear all pixels

    # Define breathing pattern colors and names
    pattern_info = {
        1: {"color": (0, 150, 255), "name": "4-7-8 Breathing"},  # Soft blue
        2: {"color": (100, 200, 100), "name": "Box Breathing"},  # Soft green
        3: {"color": (200, 100, 200), "name": "Triangle Breathing"},  # Soft purple
        4: {"color": (255, 150, 0), "name": "Deep Relaxation"}  # Soft orange
    }

    info = pattern_info.get(pattern, {"color": (255, 255, 255), "name": "Unknown"})

    # Show breathing pattern with unique visual - expand from the center
    center_pixels = [4, 5]
    for pos in center_pixels:
        cp.pixels[pos] = info["color"]

    # Add pattern-specific visual indicators
    if pattern >= 2:
        ring1_pixels = [3, 6]
        for pos in ring1_pixels:
            cp.pixels[pos] = tuple(int(c * 0.6) for c in info["color"])

    if pattern >= 3:
        ring2_pixels = [2, 7]
        for pos in ring2_pixels:
            cp.pixels[pos] = tuple(int(c * 0.4) for c in info["color"])

    if pattern == 4:
        ring3_pixels = [1, 8, 0, 9]
        for pos in ring3_pixels:
            cp.pixels[pos] = tuple(int(c * 0.2) for c in info["color"])

    cp.pixels.show()
    print("🧘 Pattern %d: %s" % (pattern, info["name"]))

    # Hold the pattern display longer for meditation feedback
    time.sleep(1.2)

    # Gentle fade out instead of abrupt clear
    for fade_step in range(10):
        for i in range(10):
            current_color = cp.pixels[i]
            if current_color != (0, 0, 0):
                faded_color = tuple(int(c * 0.8) for c in current_color)
                cp.pixels[i] = faded_color
        cp.pixels.show()
        time.sleep(0.1)

    cp.pixels.fill((0, 0, 0))
    cp.pixels.show()


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

    # Handle light interactions for UFO Intelligence learning
    if interactions.get('light_interaction', False):
        print("[UFO AI] 💡 Light interaction detected via InteractionManager!")
        current_routine_instance.last_interaction = time.monotonic()
        # You could add specific light interaction learning here


if __name__ == "__main__":
    main()
