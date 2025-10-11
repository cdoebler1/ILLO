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
debug_bluetooth = False
debug_audio = False
debug_memory = True
debug_interactions = False


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
        return True


def show_routine_feedback(routine):
    """Display visual feedback for routine selection."""
    cp.pixels.fill((0, 0, 0))

    routine_info = {
        1: {"color": (100, 0, 255), "name": "UFO Intelligence"},
        2: {"color": (0, 255, 100), "name": "Intergalactic Cruising"},
        3: {"color": (0, 100, 255), "name": "Meditate"},
        4: {"color": (255, 100, 0), "name": "Dance Party"}
    }

    info = routine_info.get(routine, {"color": (255, 255, 255), "name": "Unknown"})

    for i in range(routine):
        cp.pixels[i] = info["color"]

    cp.pixels.show()
    print("🚀 Routine %d: %s" % (routine, info["name"]))


def show_mode_feedback(mode):
    """Display visual feedback for mode selection."""
    cp.pixels.fill((0, 0, 0))

    mode_info = {
        1: {"color": (255, 0, 0), "name": "Rainbow Wheel"},
        2: {"color": (255, 0, 255), "name": "Pink Theme"},
        3: {"color": (0, 0, 255), "name": "Blue Theme"},
        4: {"color": (0, 255, 0), "name": "Green Theme"}
    }

    info = mode_info.get(mode, {"color": (255, 255, 255), "name": "Unknown"})

    positions = [0, 3, 6, 9]
    for i in range(mode):
        if i < len(positions):
            cp.pixels[positions[i]] = info["color"]

    cp.pixels.show()
    print("🎨 Mode %d: %s" % (mode, info["name"]))


def main():
    """Main application loop with task scheduling."""
    config_mgr = ConfigManager()
    config = config_mgr.load_config()
    memory_mgr = MemoryManager(enable_debug=debug_memory)
    interaction_mgr = InteractionManager(enable_debug=debug_interactions)

    scheduler = TaskScheduler()

    routine = config.get('routine', 1)
    mode = config.get('mode', 1)
    _name = config.get('name', 'ILLO')
    _bluetooth_enabled = config.get('bluetooth_enabled', True)
    _college = config.get('college', 'none')
    _college_spirit_enabled = config.get('college_spirit_enabled', False)
    ufo_persistent_memory = config.get('ufo_persistent_memory', False)
    _meditate_adaptive_timing = config.get('meditate_adaptive_timing', True)
    _meditate_ultra_dim = config.get('meditate_ultra_dim', True)
    _college_chant_detection_enabled = config.get('college_chant_detection_enabled',
                                                  False)

    _fs_is_writable = _fs_writable_check()
    _persist_this_run = bool(ufo_persistent_memory and _fs_is_writable)

    current_routine_instance = None
    active_routine_number = 0
    last_button_a_time = 0
    last_button_b_time = 0
    button_debounce_delay = 0.3
    config_changed = False

    def memory_cleanup_task():
        """Periodic memory cleanup task."""
        memory_mgr.periodic_cleanup()

    def config_save_task():
        """Save configuration if changes are pending."""
        nonlocal config_changed, config, routine, mode
        if config_changed:
            config['routine'] = routine
            config['mode'] = mode
            config_mgr.save_config(config)
            config_changed = False
            print("[SCHEDULER] 💾 Config auto-saved")

    def system_status_task():
        """Periodic system status reporting."""
        import gc
        print("[SCHEDULER] 📊 Memory: %d bytes free, Routine: %d, Mode: %d" %
              (gc.mem_free(), routine, mode))

    scheduler.add_task('memory_cleanup', 30.0, memory_cleanup_task)
    scheduler.add_task('config_save', 3.0, config_save_task)
    scheduler.add_task('system_status', 60.0, system_status_task, enabled=debug_memory)

    actual_volume = cp.switch
    print("🛸 UFO System Initialized with Task Scheduler")
    print("📋 Current: Routine %d, Mode %d, Sound %s" % (routine, mode,
                                                        "ON" if actual_volume else "OFF"))

    if ufo_persistent_memory and not _fs_is_writable:
        print("💾 Persistent memory REQUESTED but DISABLED (USB write-protect detected)")
    elif _persist_this_run:
        print(
            "💾 Persistent memory ENABLED — Illo will remember personality across sessions")
    else:
        print("💾 Persistent memory DISABLED — Illo resets personality each session")

    cp.detect_taps = 1

    loop_start_time = time.monotonic()
    loop_count = 0
    performance_report_interval = 100

    while True:
        current_time = time.monotonic()
        volume = cp.switch
        loop_count += 1

        if routine != active_routine_number:
            if current_routine_instance:
                if hasattr(current_routine_instance, 'cleanup'):
                    current_routine_instance.cleanup()

                memory_mgr.cleanup_before_routine_change()
                del current_routine_instance

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

                if routine == 1:
                    scheduler.tasks['memory_cleanup']['interval'] = 20.0
                else:
                    scheduler.tasks['memory_cleanup']['interval'] = 30.0
            else:
                print("❌ Failed to load routine %d" % routine)

        interactions = interaction_mgr.check_interactions(routine, volume, cp.pixels)
        handle_ufo_intelligence_learning(routine, current_routine_instance,
                                         interactions)

        new_routine, new_mode, last_button_a_time, last_button_b_time, button_config_changed = handle_button_interactions(
            routine, mode, last_button_a_time, last_button_b_time,
            button_debounce_delay, current_time
        )

        if new_routine != routine:
            routine = new_routine
            config['routine'] = routine

        if new_mode != mode:
            mode = new_mode
            config['mode'] = mode

        if button_config_changed:
            config_changed = True

        if current_routine_instance:
            current_routine_instance.run(mode, volume)

        scheduler.run_due_tasks(current_time)

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

    name = config.get('name', 'ILLO')
    bluetooth_enabled = config.get('bluetooth_enabled', True)
    college_spirit_enabled = config.get('college_spirit_enabled', False)
    college = config.get('college', 'none')
    ufo_persistent_memory = config.get('ufo_persistent_memory', False)
    meditate_adaptive_timing = config.get('meditate_adaptive_timing', True)
    meditate_ultra_dim = config.get('meditate_ultra_dim', True)

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
            instance = DanceParty(name, bt_debug, audio_debug)

            if bluetooth_enabled and hasattr(instance, 'enable_bluetooth'):
                print("[SYSTEM] 📱 Enabling Bluetooth for Dance Party sync...")
                success = instance.enable_bluetooth()
                if success:
                    print("[SYSTEM] ✅ Dance Party Bluetooth sync enabled")
                    print(
                        "[SYSTEM] 💃 Role will be determined by Button B (Mode 1=Leader, Mode 2=Follower)")
                else:
                    print("[SYSTEM] ❌ Failed to enable Dance Party Bluetooth")
            else:
                print("[SYSTEM] 🏃 Dance Party in standalone mode (Bluetooth disabled)")
                if not bluetooth_enabled:
                    print("[SYSTEM]   Reason: Bluetooth disabled in config")

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

    if cp.button_a and (current_time - last_button_a_time > button_debounce_delay):
        routine = (routine % 4) + 1

        show_routine_feedback(routine)
        print("🔄 Switching to routine %d - saving and rebooting..." % routine)

        try:
            from config_manager import ConfigManager
            config_mgr = ConfigManager()
            config = config_mgr.load_config()

            config['routine'] = routine
            success = config_mgr.save_config(config)

            if success:
                print("💾 Routine %d saved to config successfully" % routine)
                time.sleep(1.5)

                cp.pixels.fill((0, 0, 0))
                cp.pixels.show()

                print("🚀 Rebooting for clean routine switch...")
                time.sleep(0.5)

                import microcontroller
                microcontroller.reset()

            else:
                print("❌ Failed to save routine, continuing without reboot")
                config_changed = True

        except Exception as e:
            print("❌ Error during routine save: %s" % str(e))
            print("Continuing without reboot...")
            config_changed = True

        last_button_a_time = current_time
        time.sleep(0.8)
        cp.pixels.fill((0, 0, 0))
        cp.pixels.show()

    if cp.button_b and (current_time - last_button_b_time > button_debounce_delay):
        mode = (mode % 4) + 1
        show_mode_feedback(mode)
        config_changed = True

        if routine == 3:
            show_breathing_pattern_feedback(mode)
            print("[MEDITATE] 🧘 Mode %d = %s" % (mode, {
                1: "4-7-8 Breathing",
                2: "Box Breathing",
                3: "Triangle Breathing",
                4: "Deep Relaxation"
            }.get(mode, "Unknown")))

        time.sleep(0.8)
        cp.pixels.fill((0, 0, 0))
        cp.pixels.show()

        last_button_b_time = current_time

    return routine, mode, last_button_a_time, last_button_b_time, config_changed


def show_breathing_pattern_feedback(pattern):
    """Display visual feedback for breathing pattern selection."""
    cp.pixels.fill((0, 0, 0))

    pattern_info = {
        1: {"color": (0, 150, 255), "name": "4-7-8 Breathing"},
        2: {"color": (100, 200, 100), "name": "Box Breathing"},
        3: {"color": (200, 100, 200), "name": "Triangle Breathing"},
        4: {"color": (255, 150, 0), "name": "Deep Relaxation"}
    }

    info = pattern_info.get(pattern, {"color": (255, 255, 255), "name": "Unknown"})

    center_pixels = [4, 5]
    for pos in center_pixels:
        cp.pixels[pos] = info["color"]

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
    time.sleep(1.2)

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

    if interactions['tap'] or interactions['shake']:
        current_routine_instance.last_interaction = time.monotonic()
        if current_routine_instance.mood == "curious":
            current_routine_instance.record_successful_attention()

    if interactions['shake']:
        current_routine_instance.energy_level = min(100,
                                                    current_routine_instance.energy_level + 15)

    if interactions.get('light_interaction', False):
        print("[UFO AI] 💡 Light interaction detected via InteractionManager!")
        current_routine_instance.last_interaction = time.monotonic()


if __name__ == "__main__":
    main()