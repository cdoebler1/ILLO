# Charles Doebler at Feral Cat AI
# UFO Intelligence Routine - Advanced AI behaviors with learning and college spirit

import time
import math
import random
from base_routine import BaseRoutine
from audio_processor import AudioProcessor


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

        # Audio-reactive light pattern state
        self.light_pattern_state = {}
        self.audio_reactive_enabled = True  # Enable audio-reactive lights

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

    @staticmethod
    def _load_chant_detection_setting():
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
        """Main AI routine with audio-reactive light shows and separated sound output."""
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

            # Get audio samples for reactive light show
            audio_samples = []
            if self.audio_reactive_enabled and self.learning.audio_history:
                # Get recent audio samples for visualization
                try:
                    np_samples = self.audio.record_samples()
                    if len(np_samples) > 0:
                        audio_samples = np_samples
                except Exception as e:
                    if self.debug_audio:
                        print("[UFO AI] Audio sample error: %s" % str(e))

            # Audio-reactive light show (if audio is present)
            if audio_samples and len(audio_samples) > 10:
                self._audio_reactive_light_pattern(self.hardware, audio_samples,
                                                   self.light_pattern_state)
            else:
                # Normal AI decision making when no strong audio
                if self.ai_core.should_make_decision():
                    self.ai_core.make_intelligent_decision(
                        self.learning.audio_history,
                        self.learning.movement_history,
                        self.learning.environment_baseline
                    )

                # Execute current behavior
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

    def _audio_reactive_light_pattern(self, hardware, audio_samples, pattern_state):
        """
        Create exciting audio-reactive light patterns without heavy memory usage.
        Uses amplitude analysis instead of FFT for memory efficiency.

        Args:
            hardware: Hardware manager instance
            audio_samples: Raw audio samples from microphone
            pattern_state: Dictionary to maintain pattern state between calls
        """
        try:
            # Calculate audio energy (memory-efficient alternative to FFT)
            if len(audio_samples) > 0:
                # Simple amplitude analysis
                audio_energy = sum(abs(s) for s in audio_samples) / len(audio_samples)

                # Normalize energy to 0-1 range (adjust based on typical values)
                normalized_energy = min(1.0, audio_energy / 5000.0)

                # Detect beats by tracking sudden energy increases
                if 'last_energy' not in pattern_state:
                    pattern_state['last_energy'] = 0
                    pattern_state['beat_detected'] = False
                    pattern_state['pattern_mode'] = 0
                    pattern_state['hue_offset'] = 0
                    pattern_state['beat_cooldown'] = 0

                # Beat detection - energy spike above threshold
                energy_delta = normalized_energy - pattern_state['last_energy']
                beat_threshold = 0.15

                if pattern_state['beat_cooldown'] > 0:
                    pattern_state['beat_cooldown'] -= 1

                if energy_delta > beat_threshold and pattern_state[
                    'beat_cooldown'] == 0:
                    pattern_state['beat_detected'] = True
                    pattern_state['beat_cooldown'] = 5  # Prevent rapid re-triggering
                    pattern_state['pattern_mode'] = (pattern_state[
                                                         'pattern_mode'] + 1) % 4
                else:
                    pattern_state['beat_detected'] = False

                pattern_state['last_energy'] = normalized_energy

                # Choose visualization based on pattern mode and audio energy
                if pattern_state['pattern_mode'] == 0:
                    # Mode 0: Energy wave - pixels light up based on amplitude
                    self._energy_wave_pattern(hardware, normalized_energy,
                                              pattern_state)
                elif pattern_state['pattern_mode'] == 1:
                    # Mode 1: Spectrum spread - color shifts based on energy
                    self._spectrum_spread_pattern(hardware, normalized_energy,
                                                  pattern_state)
                elif pattern_state['pattern_mode'] == 2:
                    # Mode 2: Pulse ring - expanding circles on beats
                    self._pulse_ring_pattern(hardware, normalized_energy, pattern_state)
                else:
                    # Mode 3: Rainbow chase - speed varies with energy
                    self._rainbow_chase_pattern(hardware, normalized_energy,
                                                pattern_state)

        except Exception as e:
            print("[UFO AI] Audio-reactive pattern error: %s" % str(e))
            # Fallback to simple pattern
            for i in range(10):
                hardware.pixels[i] = (50, 50, 200)
            hardware.pixels.show()

    def _energy_wave_pattern(self, hardware, energy, state):
        """Wave pattern where brightness follows audio energy."""
        # Map energy to number of lit pixels (1-10)
        num_lit = max(1, int(energy * 10))

        # Create traveling wave effect
        if 'wave_pos' not in state:
            state['wave_pos'] = 0

        state['wave_pos'] = (state['wave_pos'] + 1) % 10

        for i in range(10):
            # Distance from wave position
            dist = min(abs(i - state['wave_pos']), 10 - abs(i - state['wave_pos']))

            if dist < num_lit / 2:
                # Energy-based color: blue to red spectrum
                intensity = 1.0 - (dist / (num_lit / 2 + 0.1))
                r = int(energy * 255 * intensity)
                g = int((1.0 - energy) * 150 * intensity)
                b = int((1.0 - energy) * 255 * intensity)
                hardware.pixels[i] = (r, g, b)
            else:
                # Dim background
                hardware.pixels[i] = (5, 5, 15)

        hardware.pixels.show()

    def _spectrum_spread_pattern(self, hardware, energy, state):
        """Color spectrum spreads from center based on energy."""
        if 'spectrum_phase' not in state:
            state['spectrum_phase'] = 0

        state['spectrum_phase'] = (state['spectrum_phase'] + int(energy * 15) + 1) % 360

        for i in range(10):
            # Create symmetric pattern from center (pixels 4 and 5)
            dist_from_center = abs(i - 4.5)

            # Hue based on position and phase
            hue = (state['spectrum_phase'] + int(dist_from_center * 30)) % 360

            # Brightness based on energy and distance
            brightness = energy * (1.0 - dist_from_center / 5.0)

            # HSV to RGB conversion (simplified)
            color = self._hsv_to_rgb(hue, 1.0, brightness)
            hardware.pixels[i] = color

        hardware.pixels.show()

    def _pulse_ring_pattern(self, hardware, energy, state):
        """Expanding ring pulses on beats."""
        if 'ring_radius' not in state:
            state['ring_radius'] = 0
            state['ring_active'] = False

        # Trigger new ring on beat
        if state.get('beat_detected', False) and not state['ring_active']:
            state['ring_active'] = True
            state['ring_radius'] = 0

        # Animate ring expansion
        if state['ring_active']:
            state['ring_radius'] += 0.5
            if state['ring_radius'] > 5:
                state['ring_active'] = False
                state['ring_radius'] = 0

        # Draw the ring
        for i in range(10):
            dist_from_center = abs(i - 4.5)

            # Check if pixel is on the ring edge
            if state['ring_active']:
                ring_dist = abs(dist_from_center - state['ring_radius'])
                if ring_dist < 0.8:
                    # On the ring - bright color
                    intensity = 1.0 - (state['ring_radius'] / 5.0)  # Fade as expands
                    r = int(255 * energy * intensity)
                    g = int(150 * intensity)
                    b = int(255 * (1.0 - energy) * intensity)
                    hardware.pixels[i] = (r, g, b)
                else:
                    # Background - energy glow
                    r = int(30 * energy)
                    g = int(20 * energy)
                    b = int(50 * energy)
                    hardware.pixels[i] = (r, g, b)
            else:
                # No active ring - just energy background
                intensity = energy * 0.3
                hardware.pixels[i] = (int(50 * intensity), int(30 * intensity),
                                      int(80 * intensity))

        hardware.pixels.show()

    def _rainbow_chase_pattern(self, hardware, energy, state):
        """Rainbow that chases around the ring, speed based on energy."""
        if 'chase_pos' not in state:
            state['chase_pos'] = 0

        # Speed increases with energy
        speed = 1 + int(energy * 10)
        state['chase_pos'] = (state['chase_pos'] + speed) % 360

        for i in range(10):
            # Hue based on position and chase offset
            hue = (state['chase_pos'] + i * 36) % 360

            # Brightness pulsates with energy
            brightness = 0.3 + (energy * 0.7)

            color = self._hsv_to_rgb(hue, 1.0, brightness)
            hardware.pixels[i] = color

        hardware.pixels.show()

    def _hsv_to_rgb(self, h, s, v):
        """
        Convert HSV to RGB (memory-efficient implementation).
        h: 0-360, s: 0-1, v: 0-1
        Returns: (r, g, b) tuple with values 0-255
        """
        h = h / 60.0
        i = int(h)
        f = h - i

        p = v * (1.0 - s)
        q = v * (1.0 - s * f)
        t = v * (1.0 - s * (1.0 - f))

        i = i % 6

        if i == 0:
            r, g, b = v, t, p
        elif i == 1:
            r, g, b = q, v, p
        elif i == 2:
            r, g, b = p, v, t
        elif i == 3:
            r, g, b = p, q, v
        elif i == 4:
            r, g, b = t, p, v
        else:
            r, g, b = v, p, q

        return (int(r * 255), int(g * 255), int(b * 255))

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
            self.light_pattern_state = {}

            print("[UFO AI] ✅ UFO Intelligence cleanup completed")

        except Exception as e:
            print("[UFO AI] ❌ Cleanup error: %s" % str(e))

    def _cleanup_memory(self):
        """Clean up memory when running low."""
        if self.memory_manager:
            self.memory_manager.cleanup_memory()
        if self.learning:
            self.learning.cleanup_memory()

        # Clear light pattern state to free memory
        self.light_pattern_state = {}

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