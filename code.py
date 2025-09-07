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
import gc

# Debug Configuration - Set these flags to enable debug output
debug_bluetooth = False  # Enable Bluetooth debug messages
debug_audio = False  # Enable audio processing debug messages
debug_memory = True  # Enable memory usage monitoring
debug_interactions = False  # Enable interaction debug messages

# Timing constants for different update rates
BUTTON_CHECK_MS = 20  # 50Hz for responsiveness
VOLUME_CHECK_MS = 50  # 20Hz for volume
INTERACTION_CHECK_MS = 25  # 40Hz for interactions
ROUTINE_CHECK_MS = 100  # 10Hz for routine switching
MAINTENANCE_MS = 1000  # 1Hz for maintenance
GC_INTERVAL_MS = 2000  # GC every 2 seconds


class LightweightController:
    """Memory-efficient controller without task overhead."""

    def __init__(self):
        # Core managers
        self.config_mgr = ConfigManager()
        config = self.config_mgr.load_config()
        self.memory_mgr = MemoryManager(enable_debug=debug_memory)
        self.interaction_mgr = InteractionManager(enable_debug=debug_interactions)

        # State variables (minimal memory footprint)
        self.routine = config.get('routine', 1)
        self.mode = config.get('mode', 1)
        self.volume = False
        self.name = config.get('name', 'UFO')
        self.college_spirit_enabled = config.get('college_spirit_enabled', False)
        self.college = config.get('college', '')
        self.ufo_persistent_memory = config.get('ufo_persistent_memory', False)
        self.college_chant_detection_enabled = config.get(
            'college_chant_detection_enabled', False)
        self.bluetooth_enabled = config.get('bluetooth_enabled', True)

        # Button state
        self.last_button_a_time = 0
        self.last_button_b_time = 0
        self.button_debounce_delay = 0.3

        # Feedback state
        self.feedback_clear_time = None
        self.showing_feedback = False

        # Config management
        self.config_save_timer = 0
        self.config_changed = False

        # Routine management
        self.current_routine_instance = None
        self.active_routine_number = 0
        self.switching_routine = False

        # Timing state
        self.last_times = {
            'button': 0,
            'volume': 0,
            'interaction': 0,
            'routine': 0,
            'maintenance': 0,
            'gc': 0
        }

        # System initialization
        self._fs_is_writable = self._fs_writable_check()
        self._persist_this_run = bool(
            self.ufo_persistent_memory and self._fs_is_writable)

        print("🛸 UFO System with Lightweight Control Initialized")
        print("   Current: Routine %d, Mode %d, Sound %s" % (
            self.routine, self.mode, "ON" if self.volume else "OFF"))

        if self.ufo_persistent_memory and not self._fs_is_writable:
            print(
                "⚠️ Persistent memory REQUESTED but DISABLED (USB write-protect detected)")
        elif self._persist_this_run:
            print(
                "💾 Persistent memory ENABLED — Illo will remember personality across sessions")
        else:
            print("🔄 Persistent memory DISABLED — Illo resets personality each session")

        cp.detect_taps = 1

    @staticmethod
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

    def check_buttons(self, now):
        """Handle button presses with debouncing."""
        # Handle feedback clearing if needed
        if self.feedback_clear_time and now >= self.feedback_clear_time:
            cp.pixels.fill((0, 0, 0))
            cp.pixels.show()
            self.feedback_clear_time = None
            self.showing_feedback = False

        # Skip button checking while showing feedback
        if self.showing_feedback:
            return

        # Check for button presses with debouncing
        button_a_pressed = cp.button_a and (
                    now - self.last_button_a_time > self.button_debounce_delay)
        button_b_pressed = cp.button_b and (
                    now - self.last_button_b_time > self.button_debounce_delay)

        if button_a_pressed:
            new_routine = (self.routine % 4) + 1
            
            # CRITICAL: Save IMMEDIATELY before changing routine using ConfigManager
            try:
                # Get current config and update routine
                current_config = self._get_current_config()
                current_config['routine'] = new_routine
            
                save_success = self.config_mgr.save_config(current_config)
                if save_success:
                    print("💾 EMERGENCY SAVE: Routine %d saved before switch" % new_routine)
                    self.routine = new_routine
                    self.config_changed = False  # Already saved
                else:
                    print("❌ EMERGENCY SAVE FAILED - keeping routine %d" % self.routine)
                    return  # Don't change routine if save failed
                
            except Exception as e:
                print("❌ EMERGENCY SAVE ERROR: %s - keeping routine %d" % (str(e), self.routine))
                return
        
            self.last_button_a_time = now
            show_routine_feedback(self.routine)
            self.feedback_clear_time = now + 0.8
            self.showing_feedback = True

        if button_b_pressed:
            self.mode = (self.mode % 4) + 1
            self.last_button_b_time = now
            self.config_changed = True
            self.config_save_timer = now
            show_mode_feedback(self.mode)
            self.feedback_clear_time = now + 0.8
            self.showing_feedback = True

    def _get_current_config(self):
        """Get current configuration state as a dictionary."""
        return {
            'routine': self.routine,
            'mode': self.mode,
            'name': self.name,
            'college_spirit_enabled': self.college_spirit_enabled,
            'college': self.college,
            'ufo_persistent_memory': self.ufo_persistent_memory,
            'college_chant_detection_enabled': self.college_chant_detection_enabled,
            'bluetooth_enabled': self.bluetooth_enabled
        }

    def check_volume(self):
        """Update volume state from switch."""
        self.volume = cp.switch

    def check_routine_switching(self):
        """Handle routine switching logic."""
        if self.switching_routine:
            return

        if self.routine != self.active_routine_number:
            self.switching_routine = True
            print("[ROUTINE] Switching from routine %d to %d" %
                  (self.active_routine_number, self.routine))

            try:
                # Cleanup old routine
                if self.current_routine_instance:
                    if hasattr(self.current_routine_instance, 'cleanup'):
                        self.current_routine_instance.cleanup()
                    del self.current_routine_instance
                    self.current_routine_instance = None
                    gc.collect()
                    if debug_memory:
                        print(
                            "[ROUTINE] Memory freed, available: %d bytes" % gc.mem_free())

                # Setup new routine
                self.interaction_mgr.setup_for_routine(self.routine)
                self.current_routine_instance = create_routine_instance(
                    self.routine, self.name, self._persist_this_run,
                    self.college_spirit_enabled, self.college,
                    self.bluetooth_enabled, debug_bluetooth, debug_audio
                )

                if self.current_routine_instance:
                    self.active_routine_number = self.routine
                    print("✅ Loaded routine %d successfully" % self.routine)
                else:
                    print("❌ Failed to load routine %d" % self.routine)

            except Exception as e:
                print("❌ Error during routine switch: %s" % str(e))
                self.current_routine_instance = None
            finally:
                self.switching_routine = False

    def check_interactions(self, now):
        """Handle interaction detection."""
        if not self.current_routine_instance:
            return

        # Detect interactions
        interactions = self.interaction_mgr.check_interactions(
            self.routine, self.volume, cp.pixels
        )

        # Handle UFO Intelligence learning (only for routine 1)
        if self.routine == 1:
            self._handle_ufo_intelligence_learning(interactions, now)

    def _handle_ufo_intelligence_learning(self, interactions, now):
        """Handle UFO Intelligence learning from interactions."""
        current_routine = self.current_routine_instance
        if not current_routine:
            return

        # Pass interactions to UFO Intelligence for learning
        if interactions['tap'] or interactions['shake']:
            current_routine.last_interaction = now
            if hasattr(current_routine, 'mood') and current_routine.mood == "curious":
                if hasattr(current_routine, 'record_successful_attention'):
                    current_routine.record_successful_attention()

        if interactions['shake']:
            if hasattr(current_routine, 'energy_level'):
                current_routine.energy_level = min(100,
                                                   current_routine.energy_level + 15)

        # Handle light interactions
        if interactions.get('light_interaction', False):
            if debug_interactions:
                print("[INTERACTIONS] Light interaction detected!")
            current_routine.last_interaction = now

    def run_routine(self):
        """Execute the current routine."""
        if not self.current_routine_instance:
            return

        try:
            self.current_routine_instance.run(self.mode, self.volume)
        except Exception as e:
            print("❌ Routine execution error: %s" % str(e))

    def maintenance(self, now):
        """Perform periodic maintenance tasks."""
        # Memory cleanup
        if self.memory_mgr:
            self.memory_mgr.periodic_cleanup()

        # Config saving with 2-second delay after changes using ConfigManager
        if self.config_changed and (now - self.config_save_timer > 2.0):
            current_config = self._get_current_config()

            try:
                save_success = self.config_mgr.save_config(current_config)
                if save_success:
                    self.config_changed = False
                    print("💾 Configuration saved (routine: %d, mode: %d)" % (self.routine, self.mode))
                else:
                    print("❌ Config save failed")
            except Exception as e:
                print("❌ Config save failed: %s" % str(e))

    def run_forever(self):
        """Main loop with time-based execution."""
        print("🚀 Lightweight controller starting...")

        while True:
            try:
                now = time.monotonic()
                now_ms = int(now * 1000)

                # Garbage collection
                if now_ms - self.last_times['gc'] >= GC_INTERVAL_MS:
                    gc.collect()
                    self.last_times['gc'] = now_ms

                # Button checking (highest frequency)
                if now_ms - self.last_times['button'] >= BUTTON_CHECK_MS:
                    self.check_buttons(now)
                    self.last_times['button'] = now_ms

                # Volume checking
                if now_ms - self.last_times['volume'] >= VOLUME_CHECK_MS:
                    self.check_volume()
                    self.last_times['volume'] = now_ms

                # Routine switching
                if now_ms - self.last_times['routine'] >= ROUTINE_CHECK_MS:
                    self.check_routine_switching()
                    self.last_times['routine'] = now_ms

                # Interaction checking
                if now_ms - self.last_times['interaction'] >= INTERACTION_CHECK_MS:
                    self.check_interactions(now)
                    self.last_times['interaction'] = now_ms

                # Always run the current routine (this is the most important)
                self.run_routine()

                # Maintenance (lowest frequency)
                if now_ms - self.last_times['maintenance'] >= MAINTENANCE_MS:
                    self.maintenance(now)
                    self.last_times['maintenance'] = now_ms

                # Small sleep to prevent CPU spinning
                time.sleep(0.002)  # 2ms

            except KeyboardInterrupt:
                print("🛸 UFO System shutting down...")
                break
            except Exception as e:
                print("❌ Controller error: %s" % str(e))
                time.sleep(0.1)  # Brief pause on error

        # Cleanup
        if self.current_routine_instance and hasattr(self.current_routine_instance,
                                                     'cleanup'):
            self.current_routine_instance.cleanup()


# Utility functions (unchanged)
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
    print("🎯 Routine %d: %s" % (routine, info["name"]))


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


def main():
    """Main application loop - lightweight control."""
    controller = LightweightController()
    controller.run_forever()


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
                if bt_debug:
                    instance.enable_debug()
            else:
                print("[SYSTEM] ⚡ High-performance mode (Bluetooth disabled)")

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
                if bluetooth_enabled and hasattr(instance,
                                                 'bluetooth') and instance.bluetooth:
                    print("[SYSTEM] 📱 Enabling Bluetooth for Dance Party...")
                    success = instance.enable_bluetooth()
                    if success:
                        print("[SYSTEM] ✅ Dance Party Bluetooth enabled")
                    else:
                        print("[SYSTEM] ❌ Failed to enable Dance Party Bluetooth")
                else:
                    print(
                        "[SYSTEM] 🎵 Dance Party in standalone mode (Bluetooth disabled)")

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