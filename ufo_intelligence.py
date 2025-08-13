# Charles Doebler at Feral Cat AI
# Enhanced UFO Intelligence with the Penn State spirit and audiovisual integration
# Refactored to eliminate code duplication

from base_routine import BaseRoutine
from audio_processor import AudioProcessor
import time
import json
import gc

class UFOIntelligence(BaseRoutine):
    def __init__(self, device_name=None, debug_bluetooth=False, debug_audio=False, persistent_memory=False, penn_state_enabled=True):
        super().__init__()
        self.device_name = device_name or "UFO"
        self.debug_bluetooth = debug_bluetooth
        self.debug_audio = debug_audio
        self.persistent_memory = persistent_memory
        self.penn_state_enabled = penn_state_enabled  # Add this line
        self.memory_file = "ufo_memory.json"
        
        # Core AI attributes
        self.mood = "neutral"
        self.curiosity_level = 50
        self.energy_level = 75
        self.attention_focus = "exploring"
        self.environment_baseline = 0
        self.interaction_memory = []
        self.long_term_memory = {}
        
        # Decision-making
        self.last_decision = time.monotonic()
        self.decision_interval = 3.0
        self.last_interaction = 0
        self.autonomy_timer = time.monotonic()
        self.last_memory_save = time.monotonic()
        
        # Audio processing and history
        self.audio = AudioProcessor()
        self.audio_history = []
        self.movement_history = []
        self.ambient_learning = True
        
        # Penn State spirit attributes
        self.school_spirit = 0  # 0-100 scale
        self.last_penn_state_trigger = 0
        self.penn_state_cooldown = 10.0  # Minimum seconds between triggers
        
        # Audio-visual integration
        self.audio_reactive_mode = False
        self.last_audio_update = time.monotonic()
        self.rotation_offset = 0
        
        # Penn State fight song notes (simplified main melody)
        self.fight_song_notes = [
            (294, 0.3), (330, 0.3), (370, 0.3), (392, 0.6), (370, 0.3),
            (330, 0.3), (294, 0.6), (392, 0.3), (440, 0.3), (494, 0.6)
        ]
        
        # Penn State colors
        self.penn_state_blue = (0, 50, 255)
        self.penn_state_white = (255, 255, 255)
        
        # Attention seeking behavior
        self.attention_start = 0
        self.current_attention_behavior = None
        
        print("[UFO_AI] 🧠 Enhanced UFO Intelligence initialized with Penn State spirit!")
        if persistent_memory:
            print("[UFO_AI] 💾 Persistent memory enabled")
        if not penn_state_enabled:
            print("[UFO_AI] 🏈 Penn State detection disabled")
        
        self._load_long_term_memory()
        self._apply_memory_on_startup()
    
    # ============================================================================
    # HELPER METHODS - Extracted to eliminate duplication
    # ============================================================================
    
    @staticmethod
    def _get_default_memory_structure():
        """Return default memory structure - a single source of truth."""
        return {
            'personality': {
                'base_curiosity': 0.5,
                'learned_environment': 50
            },
            'experiences': {
                'total_interactions': 0
            },
            'relationships': {
                'trust_level': 0.5
            },
            'audio_preferences': {},
            'penn_state_responses': 0
        }
    
    def _flash_pixels_pattern(self, color, flashes=3, flash_duration=0.1, pause_duration=0.1):
        """Common pixel flashing pattern - eliminates duplication."""
        for _ in range(flashes):
            # Flash on
            for i in range(10):
                self.hardware.pixels[i] = color
            self.hardware.pixels.show()
            time.sleep(flash_duration)
            
            # Flash off
            self.hardware.clear_pixels()
            self.hardware.pixels.show()
            time.sleep(pause_duration)
    
    def _pulse_pixels_pattern(self, color_func, intensity_range=(30, 255), steps=20, step_delay=0.15):
        """Common pulsing pattern - eliminates duplication."""
        min_intensity, max_intensity = intensity_range
        intensity_step = (max_intensity - min_intensity) // steps
        
        # Pulse up and down
        for direction in [1, -1]:
            intensity_values = range(min_intensity, max_intensity, intensity_step * direction)
            if direction == -1:
                intensity_values = reversed(list(intensity_values))
            
            for intensity in intensity_values:
                for i in range(10):
                    self.hardware.pixels[i] = color_func(intensity)
                self.hardware.pixels.show()
                time.sleep(step_delay)
    
    def _rotating_comet_pattern(self, color_func, main_intensity=120, trail_count=2, step_delay=0.1):
        """Common rotating comet pattern - eliminates duplication."""
        self.rotation_offset = (self.rotation_offset + 1) % 10
        self.hardware.clear_pixels()
        
        # Main pixel
        main_pos = int(self.rotation_offset)
        self.hardware.pixels[main_pos] = color_func(main_intensity)
        
        # Trail pixels
        for i in range(trail_count):
            trail_pos = (main_pos - (i + 1)) % 10
            trail_intensity = int(main_intensity * (0.6 ** (i + 1)))
            self.hardware.pixels[trail_pos] = color_func(trail_intensity)
        
        self.hardware.pixels.show()
        time.sleep(step_delay)
    
    def _safe_audio_processing(self, processor_func, fallback_result=None):
        """Safe audio processing with error handling - eliminates duplication."""
        try:
            return processor_func()
        except Exception as e:
            if self.debug_audio:
                print("[UFO_AI] Audio processing error: %s" % str(e))
            return fallback_result
    
    def _ensure_memory_structure(self, key_path):
        """Ensure memory structure exists - eliminates duplication."""
        keys = key_path.split('.')
        current = self.long_term_memory
        
        for key in keys[:-1]:
            if key not in current:
                current[key] = {}
            current = current[key]
        
        final_key = keys[-1]
        if final_key not in current:
            if final_key in ['total_interactions', 'penn_state_responses']:
                current[final_key] = 0
            elif final_key in ['trust_level', 'base_curiosity']:
                current[final_key] = 0.5
            else:
                current[final_key] = {}
    
    # ============================================================================
    # MEMORY MANAGEMENT - Refactored
    # ============================================================================
    
    def _set_experience_level(self, total_interactions):
        """Set UFO experience level and behavior timing based on interactions."""
        if total_interactions > 100:
            print("[UFO_AI] 🎓 Experienced UFO - enhanced behaviors active")
            self.decision_interval = 1.5
        elif total_interactions > 50:
            print("[UFO_AI] 🤖 Mature UFO - balanced behaviors")
            self.decision_interval = 2.0
        else:
            print("[UFO_AI] 👶 Young UFO - learning mode")
            self.decision_interval = 2.5

    def _apply_memory_on_startup(self):
        """Apply learned behaviors and preferences from memory."""
        memory = self.long_term_memory
        
        # Apply personality traits (convert from 0-1 scale to 0-100)
        personality = memory.get('personality', {})
        self.curiosity_level = int(personality.get('base_curiosity', 0.5) * 100)
        self.environment_baseline = personality.get('learned_environment', 50)
        
        # Set experience level - extracted to remove duplication
        experiences = memory.get('experiences', {})
        total_interactions = experiences.get('total_interactions', 0)
        self._set_experience_level(total_interactions)
        
        # Apply relationship data
        relationships = memory.get('relationships', {})
        trust_level = relationships.get('trust_level', 0.5)
        
        if trust_level > 0.8:
            self.energy_level = 80
            print("[UFO_AI] 💚 High trust relationship detected")
        elif trust_level < 0.3:
            self.energy_level = 40
            self.curiosity_level = max(70, self.curiosity_level)
            print("[UFO_AI] 🤔 Building trust relationship")
    
    def _load_long_term_memory(self):
        """Load AI memory from persistent storage."""
        default_memory = self._get_default_memory_structure()
        
        if not self.persistent_memory:
            self.long_term_memory = default_memory
            return
        
        try:
            with open(self.memory_file, 'r') as f:
                data = json.load(f)
                self.long_term_memory = data.get('memory', default_memory)
                self.school_spirit = data.get('school_spirit', 0)
                print("[UFO_AI] 📚 Memory loaded - School spirit: %d" % self.school_spirit)
        except (OSError, ValueError):
            print("[UFO_AI] ⚠️ No existing memory file")
            self.long_term_memory = default_memory
    
    def _save_long_term_memory(self):
        """Save AI memory to persistent storage."""
        if not self.persistent_memory:
            return
        
        current_time = time.monotonic()
        if current_time - self.last_memory_save < 30:
            return
        
        try:
            memory_data = {
                'memory': self.long_term_memory,
                'school_spirit': self.school_spirit,
                'last_save': current_time
            }
            
            with open(self.memory_file, 'w') as f:
                json.dump(memory_data, f)
            
            self.last_memory_save = current_time
            print("[UFO_AI] 💾 Memory saved")
        except OSError as e:
            print("[UFO_AI] ❌ Memory save failed: %s" % str(e))
    
    # ============================================================================
    # MAIN RUN LOOP - Refactored
    # ============================================================================
    
    def run(self, mode, volume):
        """Enhanced run method with audiovisual integration and Penn State features."""
        current_time = time.monotonic()
        color_func = self.get_color_function(mode)
        
        # Collect sensor data
        sensor_data = self._collect_sensor_data_enhanced()
        
        # Check for Penn State triggers first (the highest priority)
        if self._detect_penn_state_chant(sensor_data.get('audio_samples', [])):
            self._execute_penn_state_celebration(volume)
            return
        
        # Audiovisual processing or normal AI behavior
        if sensor_data.get('has_audio', False) and volume > 0:
            self._process_audio_visual(sensor_data, color_func, volume)
        else:
            self._process_normal_ai_behavior(sensor_data, color_func, volume, current_time)
        
        # Memory management
        self._update_long_term_memory(sensor_data)
        if current_time % 10 < 1:
            gc.collect()
    
    def _process_normal_ai_behavior(self, sensor_data, color_func, volume, current_time):
        """Process normal AI decision-making when no audio."""
        if current_time - self.last_decision > self.decision_interval:
            decision = self._make_intelligent_decision(sensor_data)
            self._execute_behavior(decision, color_func, volume)
            self.last_decision = current_time
    
    def _collect_sensor_data_enhanced(self):
        """Enhanced sensor data collection including audio analysis."""
        sensor_data = {
            'tap_detected': self.hardware.tap_detected(),
            'shake_detected': self.hardware.shake_detected(),
            'light_level': self.hardware.light,
            'temperature': self.hardware.temperature,
            'has_audio': False,
            'audio_samples': []
        }
        
        # Audio processing with error handling
        def audio_processor():
            audio_samples = self.audio.record_samples()
            sensor_data['audio_samples'] = audio_samples
            sensor_data['has_audio'] = len(audio_samples) > 50
            
            if sensor_data['has_audio']:
                deltas = self.audio.compute_deltas(audio_samples)
                sensor_data['audio_deltas'] = deltas
                sensor_data['frequency'] = self.audio.calculate_frequency(deltas)
        
        self._safe_audio_processing(audio_processor)
        return sensor_data
    
    # ============================================================================
    # PENN STATE FUNCTIONALITY - Refactored
    # ============================================================================
    
    def _detect_penn_state_chant(self, audio_samples):
        """Detect 'WE ARE' chant pattern in audio."""
        # Check if Penn State detection is enabled - FIRST CHECK
        if not self.penn_state_enabled:
            return False
        
        if (len(audio_samples) < 100 or 
            time.monotonic() - self.last_penn_state_trigger < self.penn_state_cooldown):
            return False
        
        def detection_processor():
            try:
                # Calculate energy levels in segments
                segment_size = max(1, len(audio_samples) // 10)
                segment_energies = []
                
                for i in range(0, len(audio_samples), segment_size):
                    segment = audio_samples[i:i + segment_size]
                    if len(segment) > 10:
                        mean_val = sum(segment) / len(segment)
                        energy = sum((x - mean_val) ** 2 for x in segment) / len(segment)
                        segment_energies.append(energy ** 0.5)
                
                # Look for the "WE ARE" pattern (two peaks with a gap)
                if len(segment_energies) >= 6:
                    peak_threshold = max(segment_energies) * 0.6
                    peaks = [i for i, energy in enumerate(segment_energies) if energy > peak_threshold]
                    
                    if len(peaks) >= 2:
                        gap = peaks[1] - peaks[0]
                        if 1 <= gap <= 3:
                            confidence = (min(segment_energies[peaks[0]], segment_energies[peaks[1]]) / 
                                        max(segment_energies))
                            
                            if self.debug_audio:
                                print("[UFO_AI] 🎯 Penn State pattern detected! Confidence: %.2f" % confidence)
                            
                            return confidence > 0.3
                return False
            except Exception as e:
                if self.debug_audio:
                    print("[UFO_AI] Penn State detection error: %s" % str(e))
                return False
        
        return self._safe_audio_processing(detection_processor, False)
    
    def _execute_penn_state_celebration(self, volume):
        """Execute Penn State celebration with proper timing control."""
        if not self.penn_state_enabled:
            return
        
        current_time = time.monotonic()
        
        # Only execute if enough time has passed since last trigger
        if current_time - self.last_penn_state_trigger < self.penn_state_cooldown:
            return
        
        print("[UFO_AI] 🏈 WE ARE... PENN STATE!")
        
        # Update timing IMMEDIATELY to prevent re-triggering
        self.last_penn_state_trigger = current_time
        self.school_spirit = min(100, self.school_spirit + 10)
        self.energy_level = 100
        self.mood = "excited"
        
        # Quick visual celebration
        for i in range(10):
            self.hardware.pixels[i] = self.penn_state_blue
        self.hardware.pixels.show()
        
        # Quick audio (non-blocking)
        if volume > 0:
            self._speak_penn_state()
        
        # Record the interaction
        self._record_penn_state_interaction()
        
        # Set timed excitement behavior instead of blocking light show
        self.attention_start = current_time
        self.current_attention_behavior = "penn_state_excited"
        
        if self.debug_audio:
            print("[UFO_AI] Penn State celebration initiated - 5 second excitement period")

    def _speak_penn_state(self):
        """Non-blocking Penn State speech synthesis."""
        if not self.penn_state_enabled:
            return
        
        # Simplified to avoid blocking time.sleep() calls
        self.hardware.play_tone_if_enabled(150, 0.3, 1)  # "PENN STATE" combined
    
    def _play_fight_song(self):
        """Play fight song with proper non-blocking timing."""
        if not self.penn_state_enabled:
            return
        
        # Play just one note quickly to avoid blocking
        self.hardware.play_tone_if_enabled(294, 0.2, 1)

    def _penn_state_light_show(self, duration):
        """Penn State light show that actually uses the duration parameter."""
        if not self.penn_state_enabled:
            return
        
        start_time = time.monotonic()
        end_time = start_time + duration

        # Initialize color to ensure it's always defined
        color = self.penn_state_blue

        while time.monotonic() < end_time:
            current_time = time.monotonic()
            # 4Hz alternation during the specified duration
            if int(current_time * 4) % 2 == 0:
                color = self.penn_state_blue
            else:
                color = self.penn_state_white
        
        for i in range(10):
            self.hardware.pixels[i] = color
        self.hardware.pixels.show()
        time.sleep(0.1)  # Small delay to control update rate
        
        # Clear pixels when done
        self.hardware.clear_pixels()
        self.hardware.pixels.show()

    def _record_penn_state_interaction(self):
        """Record Penn State interaction for learning."""
        interaction = {
            'type': 'penn_state_chant',
            'timestamp': time.monotonic(),
            'school_spirit_boost': 10,
            'mood': 'excited'
        }
        
        self.interaction_memory.append(interaction)
        
        # Update long-term memory
        self._ensure_memory_structure('experiences.penn_state_responses')
        self.long_term_memory['experiences']['penn_state_responses'] += 1
        self._save_long_term_memory()
    
    # ============================================================================
    # AUDIO-VISUAL PROCESSING - Refactored
    # ============================================================================
    
    def _process_audio_visual(self, sensor_data, color_func, volume):
        """Process audio for visual effects while maintaining AI personality."""
        audio_deltas = sensor_data.get('audio_deltas', [])
        frequency = sensor_data.get('frequency')
        
        if frequency is None:
            self._gentle_ai_animation(color_func)
            return
        
        # Audio-reactive visualization influenced by AI mood
        pixel_data = self.hardware.map_deltas_to_pixels(audio_deltas)
        mood_modifier = self._get_mood_modifier()
        
        current_time = time.monotonic()
        time_delta = current_time - self.last_audio_update
        
        # Update rotation based on AI energy
        rotation_speed = (self.energy_level / 100.0) * 0.01
        self.rotation_offset = (self.rotation_offset + frequency * time_delta * rotation_speed) % 10
        
        # Apply mood-influenced visualization
        self.hardware.clear_pixels()
        for i in range(10):
            rotated_index = int((i + self.rotation_offset) % 10)
            base_intensity = min(200, pixel_data[i] * 3)
            final_intensity = int(base_intensity * mood_modifier['intensity'])
            
            if final_intensity > mood_modifier['threshold']:
                self.hardware.pixels[rotated_index] = color_func(final_intensity)
        
        self.hardware.pixels.show()
        self.hardware.play_tone_if_enabled(frequency, 0.05, volume)
        
        # Learn from audio interaction
        self._learn_from_audio_interaction(frequency, pixel_data)
        self.last_audio_update = current_time
    
    def _get_mood_modifier(self):
        """Get visualization modifiers based on the current AI mood."""
        modifiers = {
            'excited': {'intensity': 1.3, 'threshold': 30},
            'curious': {'intensity': 1.1, 'threshold': 35},
            'investigating': {'intensity': 1.2, 'threshold': 25},
            'calm': {'intensity': 0.8, 'threshold': 50},
            'seeking_attention': {'intensity': 1.5, 'threshold': 20},
            'neutral': {'intensity': 1.0, 'threshold': 40}
        }
        return modifiers.get(self.mood, modifiers['neutral'])
    
    def _gentle_ai_animation(self, color_func):
        """Gentle AI animation when no audio is detected."""
        current_time = time.monotonic()
        
        if current_time - self.last_audio_update > 0.2:
            if self.mood == "seeking_attention":
                self._attention_seeking_animation(color_func)
            else:
                main_brightness = int(80 + (self.energy_level / 100) * 40)
                self._rotating_comet_pattern(color_func, main_brightness, 2, 0)
            
            self.last_audio_update = current_time
    
    def _attention_seeking_animation(self, color_func):
        """Special animation for attention-seeking mood."""
        current_time = time.monotonic()
        pulse_phase = (current_time * 0.5) % 1.0
        
        # Calculate pulsing intensity
        if pulse_phase < 0.5:
            intensity = int(255 * (pulse_phase * 2))
        else:
            intensity = int(255 * (2 - pulse_phase * 2))
        
        # Flash all pixels
        for i in range(10):
            self.hardware.pixels[i] = color_func(intensity)
        self.hardware.pixels.show()
    
    def _learn_from_audio_interaction(self, frequency, pixel_data):
        """AI learning from audiovisual interactions."""
        if frequency and len(pixel_data) > 0:
            avg_intensity = sum(pixel_data) / len(pixel_data)
            freq_range = self._categorize_frequency(frequency)
            
            self._ensure_memory_structure('audio_preferences.%s' % freq_range)
            pref = self.long_term_memory['audio_preferences'][freq_range]
            
            if 'count' not in pref:
                pref['count'] = 0
                pref['avg_response'] = 0
            
            pref['count'] += 1
            pref['avg_response'] = avg_intensity
    
    @staticmethod
    def _categorize_frequency(freq):
        """Categorize frequency for learning purposes."""
        if freq < 200:
            return 'bass'
        elif freq < 800:
            return 'mid'
        elif freq < 2000:
            return 'treble'
        else:
            return 'high'
    
    # ============================================================================
    # AI DECISION MAKING - Refactored
    # ============================================================================
    
    def _make_intelligent_decision(self, sensor_data):
        """Enhanced decision-making with Penn State spirit integration."""
        current_time = time.monotonic()
        
        # High-priority responses
        if sensor_data.get('tap_detected'):
            self.last_interaction = current_time
            self.energy_level = min(100, self.energy_level + 15)
            return 'excited_penn_state_fan' if self.school_spirit > 50 else 'excited'
        
        if sensor_data.get('shake_detected'):
            self.mood = 'investigating'
            return 'investigate'
        
        # Penn State personality influences
        if self.school_spirit > 70 and current_time % 30 < 1:
            return 'show_school_spirit'
        
        # Standard AI logic
        time_since_interaction = current_time - self.last_interaction
        
        if time_since_interaction > 60 and self.energy_level > 30:
            return 'seeking_attention'
        elif sensor_data.get('has_audio') and self.curiosity_level > 60:
            return 'audio_curious'
        elif self.energy_level < 30:
            return 'calm'
        else:
            return 'neutral'
    
    # ============================================================================
    # BEHAVIOR EXECUTION - Refactored to eliminate duplication
    # ============================================================================
    
    def _execute_behavior(self, behavior, color_func, volume):
        """Execute AI behavior with Penn State personality integration."""
        if self.debug_audio:
            print("[UFO_AI] Executing behavior: %s (School Spirit: %d)" % (behavior, self.school_spirit))
        
        behavior_map = {
            'excited_penn_state_fan': lambda: self._excited_penn_state_behavior(color_func, volume),
            'show_school_spirit': lambda: self._subtle_penn_state_pride(),
            'audio_curious': lambda: self._audio_curious_behavior(color_func),
            'seeking_attention': lambda: self._seeking_attention_behavior(color_func, volume),
            'excited': lambda: self._flash_pixels_pattern(color_func(200), 4, 0.15, 0.1),
            'investigate': lambda: self._investigate_behavior(color_func),
            'calm': lambda: self._pulse_pixels_pattern(color_func, (30, 80), 10, 0.15),
            'neutral': lambda: self._neutral_behavior(color_func)
        }
        
        behavior_func = behavior_map.get(behavior, lambda: self._neutral_behavior(color_func))
        behavior_func()
    
    def _excited_penn_state_behavior(self, color_func, volume):
        """Special excited behavior for Penn State fans."""
        # Use color_func with Penn State blue intensity instead of hardcoded color
        penn_state_color = color_func(200)  # or blend with Penn State blue
        self._flash_pixels_pattern(penn_state_color, 3, 0.1, 0.1)
        if volume > 0:
            self.hardware.play_tone_if_enabled(440, 0.3, volume)
    
    def _subtle_penn_state_pride(self):
        """Subtle display of the Penn State school spirit."""
        # Brief blue pulse using the common pattern
        for intensity in range(0, 100, 20):
            for i in range(10):
                self.hardware.pixels[i] = (0, int(intensity * 0.3), int(intensity * 2))
            self.hardware.pixels.show()
            time.sleep(0.1)
        
        # Fade out
        for intensity in range(100, 0, -20):
            for i in range(10):
                self.hardware.pixels[i] = (0, int(intensity * 0.3), int(intensity * 2))
            self.hardware.pixels.show()
            time.sleep(0.1)
        
        if self.debug_audio:
            print("[UFO_AI] 💙 Showing subtle Penn State pride")
    
    def _audio_curious_behavior(self, color_func):
        """Behavior when curious about audio."""
        self.mood = 'curious'
        
        # Searching pattern using a rotating beam
        for sweep in range(3):
            for pos in range(10):
                self.hardware.clear_pixels()
                
                # Light up pixels in a searching beam
                for i in range(3):
                    pixel_pos = (pos + i) % 10
                    intensity = 120 - (i * 30)
                    self.hardware.pixels[pixel_pos] = color_func(intensity)
                
                self.hardware.pixels.show()
                time.sleep(0.1)
    
    def _seeking_attention_behavior(self, color_func, volume):
        """Enhanced attention-seeking with possible Penn State references."""
        self.mood = 'seeking_attention'
        
        # Dramatic pulsing
        for pulse in range(5):
            intensity = 200 if self.school_spirit > 50 else 150
            self._flash_pixels_pattern(color_func(intensity), 1, 0.3, 0.2)
            
            # Occasional Penn State reference when seeking attention
            if volume > 0 and pulse == 2 and self.school_spirit > 60:
                self.hardware.play_tone_if_enabled(330, 0.2, volume)
    
    def _investigate_behavior(self, color_func):
        """Investigation behavior with focused beam."""
        for scan in range(2):
            for pos in range(10):
                self.hardware.clear_pixels()
                
                # Focused investigation beam
                self.hardware.pixels[pos] = color_func(180)
                self.hardware.pixels[(pos + 1) % 10] = color_func(100)
                
                self.hardware.pixels.show()
                time.sleep(0.12)
    
    def _neutral_behavior(self, color_func):
        """Standard neutral behavior using rotating comet."""
        self._rotating_comet_pattern(color_func, 100, 1, 0.2)
    
    # ============================================================================
    # MEMORY UPDATES - Refactored
    # ============================================================================
    
    def _update_long_term_memory(self, sensor_data):
        """Update long-term memory with sensor data and experiences."""
        current_time = time.monotonic()
        
        # Update interaction statistics
        self._ensure_memory_structure('experiences.total_interactions')
        if sensor_data.get('tap_detected') or sensor_data.get('shake_detected'):
            self.long_term_memory['experiences']['total_interactions'] += 1
        
        # Decay energy over time
        if current_time % 5 < 1:
            self.energy_level = max(20, self.energy_level - 1)
        
        # Save memory periodically
        self._save_long_term_memory()
    
    def record_successful_attention(self):
        """Record successful attention-seeking for learning."""
        self._ensure_memory_structure('relationships.trust_level')
        trust_level = self.long_term_memory['relationships']['trust_level']
        self.long_term_memory['relationships']['trust_level'] = min(1.0, trust_level + 0.05)
        print("[UFO_AI] 💚 Trust relationship improved!")

# Helper function for sin calculation (basic approximation)
def sin(x):
    """Basic sine approximation for LED breathing effects."""
    x = x % (2 * 3.14159)
    if x < 3.14159:
        return x / 3.14159
    else:
        return (2 * 3.14159 - x) / 3.14159
