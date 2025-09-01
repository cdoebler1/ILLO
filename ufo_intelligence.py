# Charles Doebler at Feral Cat AI
# Autonomous UFO Intelligence - College-Aware AI System

from base_routine import BaseRoutine
from audio_processor import AudioProcessor
import time

# Import protection for json module
try:
    import json
except ImportError:
    json = None


class UFOIntelligence(BaseRoutine):
    def __init__(self, device_name=None, debug_bluetooth=False, debug_audio=False,
                 persistent_memory=False, college_spirit_enabled=True,
                 college="penn_state"):
        super().__init__()

        # Core components - initialize audio processor early
        self.audio = AudioProcessor()
        self.device_name = device_name or "UFO"
        self.debug_bluetooth = debug_bluetooth
        self.debug_audio = debug_audio

        # Initialize subsystem containers for lazy loading
        self.memory_manager = None
        self.college_system = None
        self.ai_core = None
        self.behaviors = None
        self.learning = None

        # Store initialization parameters for lazy loading
        self._persistent_memory = persistent_memory
        self._college_spirit_enabled = college_spirit_enabled
        self._college = college

        # Load configuration using ConfigManager consistently
        self.chant_detection_enabled = self._load_chant_detection_setting()

        # Initialize subsystems lazily to reduce memory pressure
        self._initialize_subsystems()

        # Validate initialization
        if not self.validate_initialization():
            print("[UFO AI] ❌ Warning: Some subsystems failed to initialize")

        print("[UFO AI] 🛸 %s Intelligence System Online" % self.device_name)
        if college_spirit_enabled and self.college_system:
            college_name = "Unknown"
            try:
                if hasattr(self.college_system,
                           'college_manager') and self.college_system.college_manager:
                    college_name = self.college_system.college_manager.get_college_name()
            except Exception as e:
                print("[UFO AI] ⚠️ Could not get college name: %s" % str(e))
                college_name = "Generic"

            print("[UFO AI] 🏈 College spirit: %s" % college_name)
            if self.chant_detection_enabled:
                print("[UFO AI] 🎤 Chant detection: ENABLED")
            else:
                print(
                    "[UFO AI] 🎤 Chant detection: DISABLED (random college behaviors active)")

    def _load_chant_detection_setting(self):
        """Load chant detection setting using ConfigManager consistently."""
        try:
            from config_manager import ConfigManager
            config_mgr = ConfigManager()
            config = config_mgr.load_config()
            return config.get('college_chant_detection_enabled', False)
        except Exception as e:
            print("[UFO AI] Config load error: %s" % str(e))
            return False  # Default to disabled for safety

    def _initialize_subsystems(self):
        """Initialize AI subsystems with lazy loading and error handling."""
        try:
            # Initialize memory manager first (required by others)
            if not self.memory_manager:
                from ufo_memory_manager import UFOMemoryManager
                self.memory_manager = UFOMemoryManager(self._persistent_memory)
                print("[UFO AI] ✅ Memory manager initialized")
        except Exception as e:
            print("[UFO AI] ❌ Memory manager init failed: %s" % str(e))
            return False

        try:
            # Initialize college system - ALWAYS initialize, even when disabled
            if not self.college_system:
                from ufo_college_system import UFOCollegeSystem
                self.college_system = UFOCollegeSystem(self._college_spirit_enabled,
                                                       self._college)
                if self._college_spirit_enabled:
                    print("[UFO AI] ✅ College system initialized (enabled)")
                else:
                    print("[UFO AI] ✅ College system initialized (disabled)")
        except Exception as e:
            print("[UFO AI] ❌ College system init failed: %s" % str(e))

        try:
            # Initialize AI core (requires memory and college systems)
            if not self.ai_core and self.memory_manager:
                from ufo_ai_core import UFOAICore
                self.ai_core = UFOAICore(self.memory_manager, self.college_system)
                print("[UFO AI] ✅ AI core initialized")
        except Exception as e:
            print("[UFO AI] ❌ AI core init failed: %s" % str(e))

        try:
            # Initialize behaviors (requires hardware and college system)
            if not self.behaviors:
                from ufo_ai_behaviors import UFOAIBehaviors
                self.behaviors = UFOAIBehaviors(self.hardware, self.college_system)
                print("[UFO AI] ✅ Behaviors initialized")
        except Exception as e:
            print("[UFO AI] ❌ Behaviors init failed: %s" % str(e))

        try:
            # Initialize learning system (requires memory and college systems)
            if not self.learning and self.memory_manager:
                from ufo_learning import UFOLearningSystem
                self.learning = UFOLearningSystem(self.memory_manager,
                                                  self.college_system)
                print("[UFO AI] ✅ Learning system initialized")
        except Exception as e:
            print("[UFO AI] ❌ Learning system init failed: %s" % str(e))

        return True

    def validate_initialization(self):
        """Validate that critical subsystems initialized successfully."""
        critical_systems = [
            ('memory_manager', self.memory_manager),
            ('ai_core', self.ai_core),
            ('behaviors', self.behaviors),
            ('learning', self.learning)
        ]

        failed_systems = []
        for name, system in critical_systems:
            if system is None:
                failed_systems.append(name)

        if failed_systems:
            print("[UFO AI] ❌ Failed systems: %s" % ", ".join(failed_systems))
            return False

        return True

    def run(self, mode, sound_enabled):
        """Main AI routine with separated sound output and audio input."""
        # Validate critical systems are available before running
        if not self.ai_core or not self.behaviors or not self.learning:
            print("[UFO AI] ❌ Critical systems not initialized, skipping AI processing")
            return

        try:
            current_time = time.monotonic()
            color_func = self.get_color_function(mode)

            # Enhanced sensor data collection - audio input ALWAYS active
            college_celebration = self.learning.collect_sensor_data_enhanced(
                self.audio, self.hardware, sound_enabled, self.chant_detection_enabled)

            # Check for random college behaviors (when chant detection is off)
            random_college_event = False
            if self.college_system:
                random_college_event = self.college_system.check_for_random_college_behavior(
                    self.hardware, sound_enabled, self.chant_detection_enabled)

            # Skip normal AI processing during college events
            if college_celebration or random_college_event:
                return

            # Normal AI decision making
            if self.ai_core.should_make_decision():
                self.ai_core.make_intelligent_decision(
                    self.learning.audio_history,
                    self.learning.movement_history,
                    self.learning.environment_baseline
                )

            # Execute current behavior - pass audio processor to avoid double recording
            self.behaviors.execute_behavior(
                self.ai_core.mood, color_func, sound_enabled, current_time,
                self.ai_core.curiosity_level, self.ai_core.energy_level,
                self.audio
            )

            # Update learning systems
            self.learning.update_learning(self.ai_core)

            # Periodic memory saves
            if self.memory_manager and current_time - self.memory_manager.last_memory_save > 60:
                self.memory_manager.update_memory(
                    self.ai_core.curiosity_level,
                    self.ai_core.energy_level,
                    self.learning.environment_baseline
                )

        except MemoryError:
            print("[UFO AI] Low memory - performing cleanup")
            self._cleanup_memory()
        except Exception as e:
            print("[UFO AI] Runtime error: %s" % str(e))
            if self.ai_core:
                self.ai_core.mood = "neutral"

    def record_successful_attention(self):
        """Called when attention-seeking behavior gets user interaction."""
        if self.ai_core:
            self.ai_core.record_successful_attention()

    def cleanup(self):
        """Clean up UFO Intelligence resources and subsystems."""
        try:
            print("[UFO AI] 🧹 Cleaning up UFO Intelligence...")

            # Clean up each subsystem
            if self.learning:
                self.learning.cleanup_memory()
            if self.memory_manager:
                self.memory_manager.cleanup_memory()
            if self.behaviors:
                # Clear any cached audio processors
                self.behaviors._shared_audio_processor = None
                self.behaviors._audio_processor = None

            # Clear references to heavy objects
            self.memory_manager = None
            self.college_system = None
            self.ai_core = None
            self.behaviors = None
            self.learning = None

            print("[UFO AI] ✅ UFO Intelligence cleanup completed")

        except Exception as e:
            print("[UFO AI] ❌ Cleanup error: %s" % str(e))

    def _cleanup_memory(self):
        """Clean up memory when running low."""
        if self.memory_manager:
            self.memory_manager.cleanup_memory()
        if self.learning:
            self.learning.cleanup_memory()

        # Force garbage collection
        import gc
        gc.collect()

    # Expose key properties for compatibility with existing code
    @property
    def mood(self):
        return self.ai_core.mood if self.ai_core else "neutral"

    @mood.setter
    def mood(self, value):
        if self.ai_core:
            self.ai_core.mood = value

    @property
    def energy_level(self):
        return self.ai_core.energy_level if self.ai_core else 0.5

    @energy_level.setter
    def energy_level(self, value):
        if self.ai_core:
            self.ai_core.energy_level = value

    @property
    def last_interaction(self):
        return self.ai_core.last_interaction if self.ai_core else 0.0

    @last_interaction.setter
    def last_interaction(self, value):
        if self.ai_core:
            self.ai_core.last_interaction = value
