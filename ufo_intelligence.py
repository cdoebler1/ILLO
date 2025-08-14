# Charles Doebler at Feral Cat AI
# UFO Intelligence - AI-driven behavior with generic college spirit support

from base_routine import BaseRoutine
from audio_processor import AudioProcessor
import time
import json
import gc

def sin(x):
    """Simple sine approximation for CircuitPython."""
    # Taylor series approximation for sin(x)
    x = x % (2 * 3.14159)  # Normalize to 0-2π
    return x - (x**3)/6 + (x**5)/120 - (x**7)/5040

class UFOIntelligence(BaseRoutine):
    def __init__(self, device_name=None, debug_bluetooth=False, debug_audio=False, 
                 persistent_memory=False, college_spirit_enabled=True, college="none"):
        super().__init__()
        self.device_name = device_name or "UFO"
        self.debug_bluetooth = debug_bluetooth
        self.debug_audio = debug_audio
        self.persistent_memory = persistent_memory
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
        
        # Generic college system
        from college_manager import CollegeManager
        self.college_manager = CollegeManager(college if college_spirit_enabled else "none")
        self.college_spirit_enabled = college_spirit_enabled
        self.school_spirit = 0
        self.last_college_trigger = 0
        self.college_cooldown = 10.0
        
        # Get college-specific colors and data
        if self.college_manager.is_enabled():
            college_colors = self.college_manager.get_colors()
            self.college_primary = college_colors["primary"]
            self.college_secondary = college_colors["secondary"]
            self.fight_song_notes = self.college_manager.get_fight_song_notes()
        else:
            self.college_primary = (255, 255, 255)
            self.college_secondary = (128, 128, 128)
            self.fight_song_notes = []
        
        print(f"[UFO_AI] 🏈 College spirit: {self.college_manager.get_college_name()}")
        
        # Audio-visual integration
        self.audio_reactive_mode = False
        self.last_audio_update = time.monotonic()
        self.rotation_offset = 0
        
        # Attention seeking behavior
        self.attention_start = 0
        self.current_attention_behavior = None
        
        print("[UFO_AI] 🧠 Enhanced UFO Intelligence initialized with college spirit!")
        if persistent_memory:
            print("[UFO_AI] 💾 Persistent memory enabled")
        
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
            'college_responses': 0  # Updated from penn_state_responses
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
            if final_key in ['total_interactions', 'college_responses']:  # Updated
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
    
    # ============================================================================
    # MAIN RUN LOOP - Refactored
    # ============================================================================
    
    def run(self, mode, volume):
        """Enhanced run method with audiovisual integration and college features."""

        current_time = time.monotonic()
        color_func = self.get_color_function(mode)

        # Collect sensor data
        sensor_data = self._collect_sensor_data_enhanced()

        # Check for college triggers first (the highest priority)
        if self._detect_college_chant(sensor_data.get('audio_samples', [])):
            self._execute_college_celebration(volume)
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
    # COLLEGE FUNCTIONALITY - Fully Generic
    # ============================================================================
    
    def _detect_college_chant(self, audio_samples):
        """Generic college chant detection using college_manager data."""
        # Temporary disable flag for testing
        COLLEGE_DETECTION_DISABLED = False
        if COLLEGE_DETECTION_DISABLED:
            return False

        # Add throttling - only check every 100ms
        current_time = time.monotonic()
        if not hasattr(self, '_last_college_check'):
            self._last_college_check = 0
        if current_time - self._last_college_check < 0.1:  # 100ms throttle
            return False
        self._last_college_check = current_time

        if not self.college_manager.is_enabled():
            return False
            
        if (len(audio_samples) < 500 or
            time.monotonic() - self.last_college_trigger < self.college_cooldown):
            return False
        
        chant_data = self.college_manager.get_chant_data()
        if not chant_data:
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
                
                # Use college-specific detection parameters

                # Use college-specific detection parameters
                if len(segment_energies) >= 6:
                    # Require higher energy threshold to reduce false triggers
                    peak_threshold = max(segment_energies) * 0.85  # Changed from 0.8 to 0.85
                    peaks = [i for i, energy in enumerate(segment_energies) if energy > peak_threshold]

                    # Require more peaks for detection
                    required_peaks = max(chant_data["detection_peaks"], 3)  # At least 3 peaks
                    if len(peaks) >= required_peaks:
                        gap = peaks[1] - peaks[0]
                        gap_range = chant_data["gap_range"]
                        if gap_range[0] <= gap <= gap_range[1]:
                            confidence = (min(segment_energies[peaks[0]], segment_energies[peaks[1]]) /
                                          max(segment_energies))

                            if self.debug_audio:
                                trigger_pattern = chant_data["trigger_pattern"]
                                print(
                                    "[UFO_AI] 🎯 %s pattern detected! Confidence: %.2f" % (trigger_pattern, confidence))

                            # Much stricter confidence threshold
                            return confidence > 0.95  # Increased from 0.9               return False
            except Exception as e:
                if self.debug_audio:
                    print("[UFO_AI] College detection error: %s" % str(e))
                return False
        
        return self._safe_audio_processing(detection_processor, False)

    def _execute_college_celebration(self, volume):
        """Generic college celebration using college_manager data."""
        if not self.college_manager.is_enabled():
            return

        current_time = time.monotonic()
        if current_time - self.last_college_trigger < self.college_cooldown:
            return

        # Only print and execute if we pass the checks
        print("[UFO_AI] 🎉 COLLEGE CELEBRATION TRIGGERED!")

        chant_data = self.college_manager.get_chant_data()
        print("[UFO_AI] 🏈 %s... %s!" % (chant_data['trigger_pattern'], chant_data['response']))

        # Update timing and spirit
        self.last_college_trigger = current_time
        self.school_spirit = min(100, self.school_spirit + 10)
        self.energy_level = 100
        self.mood = "excited"

        # Use college colors for celebration
        for i in range(10):
            self.hardware.pixels[i] = self.college_primary
        self.hardware.pixels.show()

        # Add the missing chant response and fight song
        if volume > 0:
            # First play the response tone
            tone_data = self.college_manager.get_response_tone()
            self.hardware.play_tone_if_enabled(tone_data[0], tone_data[1], volume)

            # Then repeat the chant response
            self._speak_college_response()

            # Finally play the fight song
            self._play_fight_song()

        self._record_college_interaction()

        # Set timed excitement behavior
        self.attention_start = current_time
        self.current_attention_behavior = "college_excited"

        # Extend the excitement duration
        self.last_decision = current_time + 5.0  # Delay normal AI for 5 seconds
        self.mood = "excited"

    def _speak_college_response(self):
        """Generic college response speech synthesis - use data from college JSON."""
        if not self.college_manager.is_enabled():
            return

        # Get the chant data from the college JSON file
        chant_data = self.college_manager.get_chant_data()
        if not chant_data or "response" not in chant_data:
            return

        response_text = chant_data["response"]  # e.g., "PENN STATE"

        # Create tones based on syllables in the response
        # Split response into words and create tones
        words = response_text.split()
        base_frequency = 600
        frequency_step = 100

        for i, word in enumerate(words):
            # Each word gets a tone, with rising pitch
            frequency = base_frequency + (i * frequency_step)
            duration = 0.5 if len(word) > 4 else 0.4  # Longer duration for longer words

            self.hardware.play_tone_if_enabled(frequency, duration, 1)
            time.sleep(0.1)  # Brief pause between words

    def _play_fight_song(self):
        """Play complete college fight song using college_manager data."""
        if not self.college_manager.is_enabled():
            return

        # Get all the fight song notes from the college JSON
        notes = self.college_manager.get_fight_song_notes()
        if not notes:
            return

        print("[UFO_AI] 🎵 Playing complete fight song...")

        # Play ALL notes of the fight song
        for i, (note, duration) in enumerate(notes):
            self.hardware.play_tone_if_enabled(note, duration, 1)
            # Small gap between notes to make it sound more musical
            if i < len(notes) - 1:  # Don't pause after the last note
                time.sleep(0.05)

        print("[UFO_AI] 🎵 Fight song complete!")

    def _college_light_show(self, duration):
        """Generic college light show using college colors."""
        if not self.college_manager.is_enabled():
            return
        
        start_time = time.monotonic()
        end_time = start_time + duration

        while time.monotonic() < end_time:
            current_time = time.monotonic()
            # Alternating college colors
            if int(current_time * 4) % 2 == 0:
                color = self.college_primary
            else:
                color = self.college_secondary
        
            for i in range(10):
                self.hardware.pixels[i] = color
            self.hardware.pixels.show()
            time.sleep(0.1)
        
        # Clear pixels when done
        self.hardware.clear_pixels()
        self.hardware.pixels.show()

    def _record_college_interaction(self):
        """Record college interaction for learning."""
        if not self.college_manager.is_enabled():
            return
            
        chant_data = self.college_manager.get_chant_data()
        interaction = {
            'type': 'college_chant',
            'college': self.college_manager.college_name,
            'chant': chant_data['trigger_pattern'],
            'timestamp': time.monotonic(),
            'school_spirit_boost': 10,
            'mood': 'excited'
        }
        
        self.interaction_memory.append(interaction)
        
        # Update long-term memory
        self._ensure_memory_structure('experiences.college_responses')
        self.long_term_memory['experiences']['college_responses'] += 1
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
    # AI DECISION MAKING - Updated for Generic College System
    # ============================================================================
    
    def _make_intelligent_decision(self, sensor_data):
        """Enhanced decision-making with generic college spirit integration."""
        current_time = time.monotonic()
        
        # High-priority responses
        if sensor_data.get('tap_detected'):
            self.last_interaction = current_time
            self.energy_level = min(100, self.energy_level + 15)
            return 'excited_college_fan' if self.school_spirit > 50 else 'excited'
        
        if sensor_data.get('shake_detected'):
            self.mood = 'investigating'
            return 'investigate'
        
        # Generic college spirit influences
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
    # BEHAVIOR EXECUTION - Updated for Generic College System
    # ============================================================================
    
    def _execute_behavior(self, behavior, color_func, volume):
        """Execute AI behavior with generic college personality integration."""
        if self.debug_audio:
            print("[UFO_AI] Executing behavior: %s (School Spirit: %d)" % (behavior, self.school_spirit))
        
        behavior_map = {
            'excited_college_fan': lambda: self._excited_college_behavior(color_func, volume),
            'show_school_spirit': lambda: self._subtle_college_pride(),
            'audio_curious': lambda: self._audio_curious_behavior(color_func),
            'seeking_attention': lambda: self._seeking_attention_behavior(color_func, volume),
            'excited': lambda: self._flash_pixels_pattern(color_func(200), 4, 0.15, 0.1),
            'investigate': lambda: self._investigate_behavior(color_func),
            'calm': lambda: self._pulse_pixels_pattern(color_func, (30, 80), 10, 0.15),
            'neutral': lambda: self._neutral_behavior(color_func)
        }
        
        behavior_func = behavior_map.get(behavior, lambda: self._neutral_behavior(color_func))
        behavior_func()
    
    def _excited_college_behavior(self, color_func, volume):
        """Generic excited behavior for college fans."""
        if self.college_manager.is_enabled():
            # Use college primary color
            college_color = self.college_primary
            self._flash_pixels_pattern(college_color, 3, 0.1, 0.1)
        else:
            # Default excited behavior
            self._flash_pixels_pattern(color_func(200), 3, 0.1, 0.1)
            
        if volume > 0:
            if self.college_manager.is_enabled():
                tone_data = self.college_manager.get_response_tone("celebration")
                self.hardware.play_tone_if_enabled(tone_data[0], tone_data[1], volume)
            else:
                self.hardware.play_tone_if_enabled(440, 0.3, volume)
    
    def _subtle_college_pride(self):
        """Generic subtle display of college spirit."""
        if not self.college_manager.is_enabled():
            return

        # Use college colors for subtle pride display
        primary = self.college_primary
        secondary = self.college_secondary

        def _apply_college_colors(brightness_level):
            """Helper function to apply college colors at a given intensity."""
            for i in range(10):
                # Alternate between primary and secondary colors
                if i % 2 == 0:
                    color = primary
                else:
                    color = secondary

                r = int(color[0] * (brightness_level / 100.0))
                g = int(color[1] * (brightness_level / 100.0))
                b = int(color[2] * (brightness_level / 100.0))
                self.hardware.pixels[i] = (r, g, b)
            self.hardware.pixels.show()
            time.sleep(0.1)

        # Fade in
        for intensity in range(0, 100, 20):
            _apply_college_colors(intensity)

        # Fade out
        for intensity in range(100, 0, -20):
            _apply_college_colors(intensity)

        if self.debug_audio:
            college_name = self.college_manager.get_college_name()
            print("[UFO_AI] 💙 Showing subtle %s pride" % college_name)
    
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
        """Enhanced attention-seeking with possible college references."""
        self.mood = 'seeking_attention'

        # Dramatic pulsing
        for pulse in range(5):
            intensity = 200 if self.school_spirit > 50 else 150
            self._flash_pixels_pattern(color_func(intensity), 1, 0.3, 0.2)

            # Occasional college reference when seeking attention
            if volume > 0 and pulse == 2 and self.school_spirit > 60 and self.college_manager.is_enabled():
                tone_data = self.college_manager.get_response_tone("celebration")
                self.hardware.play_tone_if_enabled(tone_data[0], 0.2, volume)

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
