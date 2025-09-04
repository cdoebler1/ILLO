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
from scheduler import Scheduler, Task
import os

# Debug Configuration - Set these flags to enable debug output
debug_bluetooth = False  # Enable Bluetooth debug messages
debug_audio = False  # Enable audio processing debug messages
debug_memory = True  # Enable memory usage monitoring
debug_interactions = False  # Enable interaction debug messages

# Centralized shared state for cross-task communication
class SharedState:
    """Centralized state container for data that multiple tasks need to access."""
    def __init__(self):
        # Configuration state (shared across tasks)
        self.routine = 1
        self.mode = 1
        self.volume = False
        self.name = 'UFO'
        self.college_spirit_enabled = False
        self.college = ''
        self.ufo_persistent_memory = False
        self.college_chant_detection_enabled = False
        self.bluetooth_enabled = True
        
        # Button state (shared between button task and config task)
        self.last_button_a_time = 0
        self.last_button_b_time = 0
        self.button_debounce_delay = 0.3
        
        # Config management state
        self.config_save_timer = 0
        self.config_changed = False
        
        # Routine management state
        self.current_routine_instance = None
        self.active_routine_number = 0


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
        2: {"color": (255, 0, 255), "name": "Pink Nebula"},  # Pink base
        3: {"color": (0, 0, 255), "name": "Deep Space Blue"},  # Blue base
        4: {"color": (0, 255, 0), "name": "Forest Canopy"}  # Green base
    }

    info = mode_info.get(mode, {"color": (255, 255, 255), "name": "Unknown"})

    # Show mode with different patterns - spread pixels around the ring
    positions = [0, 3, 6, 9]  # Spread around a 10-pixel ring
    for i in range(mode):
        if i < len(positions):
            cp.pixels[positions[i]] = info["color"]

    cp.pixels.show()
    print("🎨 Mode %d: %s" % (mode, info["name"]))


# Task implementations for scheduler
class ButtonHandlerTask(Task):
    """Handles button A and B interactions with debouncing."""
    name = "buttons"
    priority = 1  # High priority for responsiveness
    period_ms = 20  # 50Hz for good button response
    budget_ms = 5  # Should be quick

    def __init__(self, shared_state):
        super().__init__()
        self.shared_state = shared_state

    def step(self, now):
        """Check buttons and update shared state."""
        routine, mode, last_a, last_b, config_changed = handle_button_interactions(
            self.shared_state['routine'],
            self.shared_state['mode'],
            self.shared_state['last_button_a_time'],
            self.shared_state['last_button_b_time'],
            self.shared_state['button_debounce_delay'],
            now
        )

        # Update shared state
        self.shared_state['routine'] = routine
        self.shared_state['mode'] = mode
        self.shared_state['last_button_a_time'] = last_a
        self.shared_state['last_button_b_time'] = last_b

        if config_changed:
            self.shared_state['config_changed'] = True
            self.shared_state['config_save_timer'] = now


class MaintenanceTask(Task):
    """Handles periodic maintenance like memory cleanup and config saving."""
    name = "maintenance"
    priority = 9  # Low priority - runs when nothing else needs to
    period_ms = 1000  # 1Hz - once per second
    budget_ms = 100  # Allow more time for cleanup operations

    def __init__(self, shared_state, memory_mgr, config_mgr, config):
        super().__init__()
        self.shared_state = shared_state
        self.memory_mgr = memory_mgr
        self.config_mgr = config_mgr
        self.config = config

    def step(self, now):
        """Perform periodic maintenance tasks."""
        # Memory cleanup
        self.memory_mgr.periodic_cleanup()

        # Config saving (with 2-second delay after last change)
        if (self.shared_state['config_changed'] and
                (now - self.shared_state['config_save_timer'] > 2.0)):
            # Update config with current values
            self.config.update({
                'routine': self.shared_state['routine'],
                'mode': self.shared_state['mode'],
                'name': self.shared_state['name'],
                'college_spirit_enabled': self.shared_state['college_spirit_enabled'],
                'college': self.shared_state['college'],
                'ufo_persistent_memory': self.shared_state['ufo_persistent_memory'],
                'college_chant_detection_enabled': self.shared_state['college_chant_detection_enabled'],
                'bluetooth_enabled': self.shared_state['bluetooth_enabled']
            })

            self.config_mgr.save_config(self.config)
            self.shared_state['config_changed'] = False
            print("[SCHEDULER] 💾 Configuration saved")


class SystemMonitorTask(Task):
    """Optional task to monitor system performance."""
    name = "monitor"
    priority = 10  # Lowest priority
    period_ms = 5000  # Every 5 seconds
    budget_ms = 20
    enabled = False  # Disabled by default, enable for debugging

    def __init__(self, scheduler):
        super().__init__()
        self.scheduler = scheduler

    def step(self, now):
        """Print scheduler performance stats."""
        stats = self.scheduler.stats()
        print("[SCHEDULER] Performance Stats:")
        for stat in stats:
            if stat['overruns'] > 0 or stat['jitter_max_ms'] > stat['period_ms'] / 2:
                print("  ⚠️  %s: %d overruns, %.1fms max jitter" %
                      (stat['name'], stat['overruns'], stat['jitter_max_ms']))


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
    instance = None

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

            # Only enable Bluetooth if both config allows it AND it was initialized
            if bluetooth_enabled and hasattr(instance,
                                             'bluetooth') and instance.bluetooth:
                print("[SYSTEM] 📱 Enabling Bluetooth control...")
                instance.enable_bluetooth()
                instance.enable_debug()  # This enables debug for both cruiser and bluetooth
            else:
                print("[SYSTEM] 🏃 High-performance mode (Bluetooth disabled)")

        elif routine == 3:
            print("[SYSTEM] Loading Meditate...")
            from meditate import Meditate
            instance = Meditate()

        elif routine == 4:
            print("[SYSTEM] ===== Loading Dance Party =====")
            try:
                from dance_party import DanceParty
                print("[SYSTEM] DanceParty import successful")

                print("[SYSTEM] Creating DanceParty instance with:")
                print("[SYSTEM]   name: %s" % name)
                print("[SYSTEM]   bt_debug: %s" % bt_debug)
                print("[SYSTEM]   audio_debug: %s" % audio_debug)

                instance = DanceParty(name, bt_debug, audio_debug)
                print("[SYSTEM] DanceParty instance created: %s" % str(instance))

                # Check if instance has bluetooth attribute
                print("[SYSTEM] Checking instance attributes...")
                print(
                    "[SYSTEM]   hasattr(instance, 'bluetooth'): %s" % hasattr(instance,
                                                                              'bluetooth'))
                if hasattr(instance, 'bluetooth'):
                    print("[SYSTEM]   instance.bluetooth: %s" % str(instance.bluetooth))
                    print("[SYSTEM]   instance.bluetooth is not None: %s" % (
                            instance.bluetooth is not None))

                print("[SYSTEM] bluetooth_enabled from config: %s" % bluetooth_enabled)

                # Enable Bluetooth for Dance Party like we do for Intergalactic Cruising
                if bluetooth_enabled and hasattr(instance,
                                                 'bluetooth') and instance.bluetooth:
                    print("[SYSTEM] ===== Enabling Bluetooth for Dance Party =====")
                    success = instance.enable_bluetooth()
                    if success:
                        print("[SYSTEM] ✅ Dance Party Bluetooth enabled")
                    else:
                        print("[SYSTEM] ❌ Failed to enable Dance Party Bluetooth")
                else:
                    print(
                        "[SYSTEM] 🏃 Dance Party in standalone mode (Bluetooth disabled)")
                    print("[SYSTEM] Bluetooth diagnostic:")
                    if not bluetooth_enabled:
                        print("[SYSTEM]   Reason: Bluetooth disabled in config")
                    elif not hasattr(instance, 'bluetooth'):
                        print("[SYSTEM]   Reason: No bluetooth attribute")
                    elif not instance.bluetooth:
                        print("[SYSTEM]   Reason: bluetooth attribute is None")

            except Exception as e:
                print("[SYSTEM] ❌ Error in Dance Party setup: %s" % str(e))
                print("[SYSTEM] Error type: %s" % type(e).__name__)
                instance = None

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

    # Handle light interactions for UFO Intelligence learning
    if interactions.get('light_interaction', False):
        print("[UFO AI] 💡 Light interaction detected via InteractionManager!")
        current_routine_instance.last_interaction = time.monotonic()
        # You could add specific light interaction learning here


def main():
    """Main application loop - full scheduler control."""
    # Initialize managers
    config_mgr = ConfigManager()
    config = config_mgr.load_config()
    memory_mgr = MemoryManager(enable_debug=debug_memory)
    interaction_mgr = InteractionManager(enable_debug=debug_interactions)

    # Initialize shared state with config values
    shared_state = SharedState()
    shared_state.routine = config.get('routine', 1)
    shared_state.mode = config.get('mode', 1)
    shared_state.name = config.get('name', 'UFO')
    shared_state.college_spirit_enabled = config.get('college_spirit_enabled', False)
    shared_state.college = config.get('college', '')
    shared_state.ufo_persistent_memory = config.get('ufo_persistent_memory', False)
    shared_state.college_chant_detection_enabled = config.get('college_chant_detection_enabled', False)
    shared_state.bluetooth_enabled = config.get('bluetooth_enabled', True)

    # System initialization
    _fs_is_writable = _fs_writable_check()
    _persist_this_run = bool(shared_state.ufo_persistent_memory and _fs_is_writable)

    # Display startup status
    print("🛸 UFO System with Full Scheduler Control Initialized")
    print("📋 Current: Routine %d, Mode %d, Sound %s" % (
        shared_state.routine, shared_state.mode,
        "ON" if shared_state.volume else "OFF"))

    # Show persistent memory status
    if shared_state.ufo_persistent_memory and not _fs_is_writable:
        print("💾 Persistent memory REQUESTED but DISABLED (USB write-protect detected)")
    elif _persist_this_run:
        print("💾 Persistent memory ENABLED — Illo will remember personality across sessions")
    else:
        print("💾 Persistent memory DISABLED — Illo resets personality each session")

    cp.detect_taps = 1

    # Create scheduler and add all tasks
    scheduler = Scheduler(min_idle_sleep_ms=2, gc_interval_ms=2000)
    
    # Add tasks in priority order (lower priority number = higher priority)
    scheduler.add(ButtonHandlerTask(shared_state))                                    # Priority 1
    scheduler.add(VolumeMonitorTask(shared_state))                                    # Priority 2  
    scheduler.add(RoutineManagerTask(shared_state, interaction_mgr, _persist_this_run)) # Priority 3
    scheduler.add(InteractionTask(shared_state, interaction_mgr))                     # Priority 4
    scheduler.add(RoutineExecutorTask(shared_state))                                  # Priority 5
    scheduler.add(MaintenanceTask(shared_state, memory_mgr, config_mgr))             # Priority 9

    print("⏰ Full scheduler starting with %d tasks:" % len(scheduler.tasks))
    for task in scheduler.tasks:
        print("   - %s (priority %d, %dms period)" % (task.name, task.priority, task.period_ms))

    # Let scheduler run everything - this blocks until stopped
    try:
        scheduler.run_forever()
    except KeyboardInterrupt:
        print("🛸 UFO System shutting down...")
    except Exception as e:
        print("❌ Scheduler error: %s" % str(e))
    finally:
        # Cleanup
        if shared_state.current_routine_instance and hasattr(shared_state.current_routine_instance, 'cleanup'):
            shared_state.current_routine_instance.cleanup()
        
        # Optional: Print performance stats if debug enabled
        if debug_memory:
            print("\n📊 Final Scheduler Performance:")
            stats = scheduler.stats()
            for stat in stats:
                print("   %s: %d overruns, %.1fms max jitter" % 
                      (stat['name'], stat['overruns'], stat['jitter_max_ms']))


# ... existing functions remain the same ...
def create_routine_instance(routine, name, _persist_this_run, college_spirit_enabled,
                            college, bluetooth_enabled, bt_debug, audio_debug):
    """
    Create a routine instance based on routine number.
    Uses lazy imports to save memory by only loading needed routines.
    """
    instance = None

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
            # Check if instance initialized properly
            if hasattr(instance, 'ai_core') and hasattr(instance, 'behaviors') and hasattr(instance, 'learning'):
                if instance.ai_core is None or instance.behaviors is None or instance.learning is None:
                    print("[SYSTEM] ❌ UFO Intelligence failed to initialize critical systems")
                    if hasattr(instance, 'cleanup'):
                        instance.cleanup()
                    return None
                    
        elif routine == 2:
            print("[SYSTEM] Loading Intergalactic Cruising...")
            from intergalactic_cruising import IntergalacticCruising
            instance = IntergalacticCruising()

            # Only enable Bluetooth if both config allows it AND it was initialized
            if bluetooth_enabled and hasattr(instance, 'bluetooth') and instance.bluetooth:
                print("[SYSTEM] 📱 Enabling Bluetooth control...")
                instance.enable_bluetooth()
                if bt_debug:
                    instance.enable_debug()
            else:
                print("[SYSTEM] 🏃 High-performance mode (Bluetooth disabled)")

        elif routine == 3:
            print("[SYSTEM] Loading Meditate...")
            from meditate import Meditate
            instance = Meditate()

        elif routine == 4:
            print("[SYSTEM] Loading Dance Party...")
            try:
                from dance_party import DanceParty
                instance = DanceParty(name, bt_debug, audio_debug)

                # Enable Bluetooth for Dance Party if configured
                if bluetooth_enabled and hasattr(instance, 'bluetooth') and instance.bluetooth:
                    print("[SYSTEM] 📱 Enabling Bluetooth for Dance Party...")
                    success = instance.enable_bluetooth()
                    if success:
                        print("[SYSTEM] ✅ Dance Party Bluetooth enabled")
                    else:
                        print("[SYSTEM] ❌ Failed to enable Dance Party Bluetooth")
                else:
                    print("[SYSTEM] 🏃 Dance Party in standalone mode (Bluetooth disabled)")

            except Exception as e:
                print("[SYSTEM] ❌ Error in Dance Party setup: %s" % str(e))
                instance = None

        return instance

    except MemoryError as e:
        print("[SYSTEM] ❌ Memory error loading routine %d: %s" % (routine, str(e)))
        if instance and hasattr(instance, 'cleanup'):
            instance.cleanup()
        return None
    except Exception as e:
        print("[SYSTEM] ❌ Error loading routine %d: %s" % (routine, str(e)))
        if instance and hasattr(instance, 'cleanup'):
            instance.cleanup()
        return None


if __name__ == "__main__":
    main()
