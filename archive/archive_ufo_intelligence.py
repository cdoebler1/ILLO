# Charles Doebler at Feral Cat AI
# Enhanced UFO Intelligence with Penn State spirit and audio-visual integration

from base_routine import BaseRoutine
from audio_processor import AudioProcessor
import time
import json
import gc

class UFOIntelligence(BaseRoutine):
    def __init__(self, device_name, debug_bluetooth=False, debug_audio=False, persistent_memory=False):
        super().__init__()
        self.device_name = device_name
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
        
        # Decision making
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
        self.we_are_detection_threshold = 2  # Audio pattern confidence needed
        
        # Audio-visual integration
        self.audio_reactive_mode = False
        self.last_audio_update = time.monotonic()
        self.rotation_offset = 0
        
        # Penn State fight song notes (simplified main melody)
        self.fight_song_notes = [
            (294, 0.3),  # D4
            (330, 0.3),  # E4
            (370, 0.3),  # F#4
            (392, 0.6),  # G4
            (370, 0.3),  # F#4
            (330, 0.3),  # E4
            (294, 0.6),  # D4
            (392, 0.3),  # G4
            (440, 0.3),  # A4
            (494, 0.6),  # B4
        ]
        
        # Attention seeking behavior
        self.attention_start = 0
        self.current_attention_behavior = None
        
        print("[UFO_AI] 🧠 Enhanced UFO Intelligence initialized with Penn State spirit!")
        if persistent_memory:
            print("[UFO_AI] 💾 Persistent memory enabled")
        
        self._load_long_term_memory()
        self._apply_memory_on_startup()
    
    def _apply_memory_on_startup(self):
        """Apply learned behaviors and preferences from memory."""
        personality = self.long_term_memory.get('personality', {})
        experiences = self.long_term_memory.get('experiences', {})
        relationships = self.long_term_memory.get('relationships', {})
        
        # Apply learned personality traits (convert from 0-1 scale to 0-100)
        base_curiosity = personality.get('base_curiosity', 0.5)
        self.curiosity_level = int(base_curiosity * 100)
        self.environment_baseline = personality.get('learned_environment', 50)
        
        # Adjust behavior based on total interactions
        total_interactions = experiences.get('total_interactions', 0)
        if total_interactions > 100:
            print("[UFO_AI] 🎓 Experienced UFO - enhanced behaviors active")
            self.decision_interval = 1.5  # More responsive
        elif total_interactions > 50:
            print("[UFO_AI] 🤖 Mature UFO - balanced behaviors")
            self.decision_interval = 2.0
        else:
            print("[UFO_AI] 👶 Young UFO - learning mode")
            self.decision_interval = 2.5  # More cautious
        
        # Adjust trust and energy based on relationship (convert from 0-1 scale)
        trust_level = relationships.get('trust_level', 0.5)
        if trust_level > 0.8:
            self.energy_level = 80  # More energetic with a trusted user
            print("[UFO_AI] 💚 High trust relationship detected")
        elif trust_level < 0.3:
            self.energy_level = 40  # More reserved with new user
            self.curiosity_level = max(70, self.curiosity_level)  # But more curious
            print("[UFO_AI] 🤔 Building trust relationship")
    
    def _load_long_term_memory(self):
        """Load AI memory from persistent storage."""
        if not self.persistent_memory:
            # Set default memory structure for RAM-only mode
            self.long_term_memory = {
                'personality': {
                    'base_curiosity': 0.5,
                    'learned_environment': 50
                },
                'experiences': {
                    'total_interactions': 0
                },
                'relationships': {
                    'trust_level': 0.5
                }
            }
            return
            
        try:
            with open(self.memory_file, 'r') as f:
                data = json.load(f)
                self.long_term_memory = data.get('memory', {})
                self.school_spirit = data.get('school_spirit', 0)
                print("[UFO_AI] 📚 Memory loaded - School spirit: %d" % self.school_spirit)
        except (OSError, ValueError) as e:
            print("[UFO_AI] ⚠️ No existing memory file")
            self.long_term_memory = {
                'personality': {
                    'base_curiosity': 0.5,
                    'learned_environment': 50
                },
                'experiences': {
                    'total_interactions': 0
                },
                'relationships': {
                    'trust_level': 0.5
                }
            }
    
    def _save_long_term_memory(self):
        """Save AI memory to persistent storage."""
        if not self.persistent_memory:
            return
            
        current_time = time.monotonic()
        if current_time - self.last_memory_save < 30:  # Save every 30 seconds max
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
    
    def run(self, mode, volume):
        """Enhanced run method with audio-visual integration and Penn State features."""
        current_time = time.monotonic()
        color_func = self.get_color_function(mode)
        
        # Collect sensor data including audio
        sensor_data = self._collect_sensor_data_enhanced()
        
        # Check for Penn State triggers first (highest priority)
        if self._detect_penn_state_chant(sensor_data.get('audio_samples', [])):
            self._execute_penn_state_celebration(color_func, volume)
            return
        
        # Audio-visual processing
        if sensor_data.get('has_audio', False) and volume > 0:
            self._process_audio_visual(sensor_data, color_func, volume)
        else:
            # Normal AI decision making when no audio
            if current_time - self.last_decision > self.decision_interval:
                decision = self._make_intelligent_decision(sensor_data)
                self._execute_behavior(decision, color_func, volume)
                self.last_decision = current_time
        
        # Memory management
        self._update_long_term_memory(sensor_data)
        if current_time % 10 < 1:  # Every ~10 seconds
            gc.collect()
    
    def _collect_sensor_data_enhanced(self):
        """Enhanced sensor data collection including audio analysis."""
        sensor_data = {}
        
        # Basic sensor data
        sensor_data['tap_detected'] = self.hardware.tap_detected()
        sensor_data['shake_detected'] = self.hardware.shake_detected()
        sensor_data['light_level'] = self.hardware.light
        sensor_data['temperature'] = self.hardware.temperature
        
        # Audio processing
        try:
            audio_samples = self.audio.record_samples()
            sensor_data['audio_samples'] = audio_samples
            sensor_data['has_audio'] = len(audio_samples) > 50
            
            if sensor_data['has_audio']:
                deltas = self.audio.compute_deltas(audio_samples)
                sensor_data['audio_deltas'] = deltas
                sensor_data['frequency'] = self.audio.calculate_frequency(deltas)
                
        except Exception as e:
            if self.debug_audio:
                print("[UFO_AI] Audio error: %s" % str(e))
            sensor_data['has_audio'] = False
            sensor_data['audio_samples'] = []
        
        return sensor_data
    
    def _detect_penn_state_chant(self, audio_samples):
        """Detect 'WE ARE' chant pattern in audio."""
        if len(audio_samples) < 100:
            return False
            
        current_time = time.monotonic()
        if current_time - self.last_penn_state_trigger < self.penn_state_cooldown:
            return False
        
        try:
            # Simple pattern detection for "WE ARE" - look for two distinct energy bursts
            # This is a simplified approach that looks for rhythm patterns
            
            # Calculate energy levels in segments
            segment_size = len(audio_samples) // 10
            segment_energies = []
            
            for i in range(0, len(audio_samples), segment_size):
                segment = audio_samples[i:i + segment_size]
                if len(segment) > 10:
                    # Simple energy calculation
                    mean_val = sum(segment) / len(segment)
                    energy = sum((x - mean_val) ** 2 for x in segment) / len(segment)
                    segment_energies.append(energy ** 0.5)
            
            # Look for pattern: high energy, pause, high energy (WE ... ARE)
            if len(segment_energies) >= 6:
                peak_threshold = max(segment_energies) * 0.6
                peaks = [i for i, energy in enumerate(segment_energies) if energy > peak_threshold]
                
                # Check for pattern that could be "WE ARE" (two peaks with gap)
                if len(peaks) >= 2:
                    gap = peaks[1] - peaks[0]
                    if 1 <= gap <= 3:  # Right timing for "WE ... ARE"
                        confidence = min(segment_energies[peaks[0]], segment_energies[peaks[1]]) / max(segment_energies)
                        
                        if self.debug_audio:
                            print("[UFO_AI] 🎯 Penn State pattern detected! Confidence: %.2f" % confidence)
                        
                        if confidence > 0.3:  # Lower threshold for demo purposes
                            return True
            
        except Exception as e:
            if self.debug_audio:
                print("[UFO_AI] Penn State detection error: %s" % str(e))
        
        return False
    
    def _execute_penn_state_celebration(self, color_func, volume):
        """Execute the full Penn State celebration sequence."""
        print("[UFO_AI] 🏈 WE ARE... PENN STATE!")
        
        self.last_penn_state_trigger = time.monotonic()
        self.school_spirit = min(100, self.school_spirit + 10)
        self.energy_level = 100
        self.mood = "excited"
        
        # Penn State colors (Blue and White)
        blue_color = (0, 50, 255)
        white_color = (255, 255, 255)
        
        # Three rounds of "WE ARE... PENN STATE"
        for round_num in range(3):
            if self.debug_audio:
                print("[UFO_AI] Round %d: WE ARE... PENN STATE!" % (round_num + 1))
            
            # "PENN STATE" response with blue flash
            self.hardware.clear_pixels()
            for i in range(10):
                self.hardware.pixels[i] = blue_color
            self.hardware.pixels.show()
            
            if volume > 0:
                # Synthesize "PENN STATE"
                self._speak_penn_state()
            
            time.sleep(0.5)
            
            # "WE ARE" with white flash
            self.hardware.clear_pixels()
            for i in range(10):
                self.hardware.pixels[i] = white_color
            self.hardware.pixels.show()
            
            time.sleep(0.8)
        
        # Play fight song snippet
        if volume > 0:
            self._play_fight_song()
        
        # Celebratory light show
        self._penn_state_light_show(3.0)  # 3-second celebration
        
        # Record this positive interaction
        self._record_penn_state_interaction()
    
    def _speak_penn_state(self):
        """Synthesize 'PENN STATE' using tone sequences."""
        # "PENN" - lower tone burst
        self.hardware.play_tone_if_enabled(150, 0.25, 1)
        time.sleep(0.1)
        
        # "STATE" - rising tone
        for freq in [200, 250, 300]:
            self.hardware.play_tone_if_enabled(freq, 0.15, 1)
    
    def _play_fight_song(self):
        """Play a snippet of the Penn State fight song."""
        print("[UFO_AI] 🎵 Playing fight song!")
        
        for note_freq, duration in self.fight_song_notes[:6]:  # First 6 notes
            self.hardware.play_tone_if_enabled(note_freq, duration, 1)
            time.sleep(0.05)  # Brief pause between notes
    
    def _penn_state_light_show(self, duration):
        """Penn State themed light celebration."""
        start_time = time.monotonic()
        blue = (0, 50, 255)
        white = (255, 255, 255)
        
        while time.monotonic() - start_time < duration:
            # Alternating blue and white wave
            current_time = time.monotonic() - start_time
            wave_pos = int((current_time * 5) % 10)
            
            self.hardware.clear_pixels()
            
            for i in range(10):
                if (i + wave_pos) % 2 == 0:
                    self.hardware.pixels[i] = blue
                else:
                    self.hardware.pixels[i] = white
            
            self.hardware.pixels.show()
            time.sleep(0.1)
    
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
        if 'experiences' not in self.long_term_memory:
            self.long_term_memory['experiences'] = {}
        
        if 'penn_state_responses' not in self.long_term_memory['experiences']:
            self.long_term_memory['experiences']['penn_state_responses'] = 0
        self.long_term_memory['experiences']['penn_state_responses'] += 1
        
        self._save_long_term_memory()
    
    def _process_audio_visual(self, sensor_data, color_func, volume):
        """Process audio for visual effects while maintaining AI personality."""
        audio_deltas = sensor_data.get('audio_deltas', [])
        frequency = sensor_data.get('frequency')
        
        if frequency is None:
            # No clear audio - gentle AI behavior
            self._gentle_ai_animation(color_func)
            return
        
        # Audio-reactive visualization influenced by AI mood
        pixel_data = self.hardware.map_deltas_to_pixels(audio_deltas)
        
        # Modify visualization based on AI mood
        mood_modifier = self._get_mood_modifier()
        
        current_time = time.monotonic()
        time_delta = current_time - self.last_audio_update
        
        # Rotation speed influenced by AI energy level
        rotation_speed = (self.energy_level / 100.0) * 0.01
        self.rotation_offset = (self.rotation_offset + frequency * time_delta * rotation_speed) % 10
        
        self.hardware.clear_pixels()
        
        # Apply mood-influenced audio visualization
        for i in range(10):
            rotated_index = int((i + self.rotation_offset) % 10)
            base_intensity = min(200, pixel_data[i] * 3)
            
            # Mood influences intensity and threshold
            final_intensity = int(base_intensity * mood_modifier['intensity'])
            threshold = mood_modifier['threshold']
            
            if final_intensity > threshold:
                self.hardware.pixels[rotated_index] = color_func(final_intensity)
        
        self.hardware.pixels.show()
        self.hardware.play_tone_if_enabled(frequency, 0.05, volume)
        
        # AI learning from audio interaction
        self._learn_from_audio_interaction(frequency, pixel_data)
        
        self.last_audio_update = current_time
    
    def _get_mood_modifier(self):
        """Get visualization modifiers based on current AI mood."""
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
            # Personality-based idle animation
            if self.mood == "seeking_attention":
                self._attention_seeking_animation(color_func)
            else:
                # Standard gentle rotation
                self.rotation_offset = (self.rotation_offset + 1) % 10
                
                self.hardware.clear_pixels()
                
                # Create personality-influenced comet
                main_pos = int(self.rotation_offset)
                trail_positions = [(main_pos - 1) % 10, (main_pos - 2) % 10]
                
                # Brightness influenced by energy level
                main_brightness = int(80 + (self.energy_level / 100) * 40)
                
                self.hardware.pixels[main_pos] = color_func(main_brightness)
                self.hardware.pixels[trail_positions[0]] = color_func(int(main_brightness * 0.6))
                self.hardware.pixels[trail_positions[1]] = color_func(int(main_brightness * 0.3))
                
                self.hardware.pixels.show()
            
            self.last_audio_update = current_time
    
    def _attention_seeking_animation(self, color_func):
        """Special animation for attention-seeking mood."""
        current_time = time.monotonic()
        pulse_speed = 0.5  # Fast pulsing
        
        # Pulsing brightness
        pulse_phase = (current_time * pulse_speed) % 1.0
        if pulse_phase < 0.5:
            intensity = int(255 * (pulse_phase * 2))
        else:
            intensity = int(255 * (2 - pulse_phase * 2))
        
        # Flash all pixels
        for i in range(10):
            self.hardware.pixels[i] = color_func(intensity)
        
        self.hardware.pixels.show()
    
    def _learn_from_audio_interaction(self, frequency, pixel_data):
        """AI learning from audio-visual interactions."""
        if frequency and len(pixel_data) > 0:
            avg_intensity = sum(pixel_data) / len(pixel_data)
            
            # Learn frequency preferences
            freq_range = self._categorize_frequency(frequency)
            
            if 'audio_preferences' not in self.long_term_memory:
                self.long_term_memory['audio_preferences'] = {}
            
            if freq_range not in self.long_term_memory['audio_preferences']:
                self.long_term_memory['audio_preferences'][freq_range] = {'count': 0, 'avg_response': 0}
            
            self.long_term_memory['audio_preferences'][freq_range]['count'] += 1
            self.long_term_memory['audio_preferences'][freq_range]['avg_response'] = avg_intensity
    
    def _categorize_frequency(self, freq):
        """Categorize frequency for learning purposes."""
        if freq < 200:
            return 'bass'
        elif freq < 800:
            return 'mid'
        elif freq < 2000:
            return 'treble'
        else:
            return 'high'
    
    def _make_intelligent_decision(self, sensor_data):
        """Enhanced decision making that considers audio history and Penn State spirit."""
        current_time = time.monotonic()
        
        # High priority responses
        if sensor_data.get('tap_detected'):
            self.last_interaction = current_time
            self.energy_level = min(100, self.energy_level + 15)
            if self.school_spirit > 50:
                return 'excited_penn_state_fan'
            return 'excited'
        
        if sensor_data.get('shake_detected'):
            self.mood = 'investigating'
            return 'investigate'
        
        # Penn State fan personality influences decisions
        if self.school_spirit > 70:
            # High school spirit affects behavior
            if current_time % 30 < 1:  # Occasional spontaneous Penn State pride
                return 'show_school_spirit'
        
        # Standard AI decision logic with audio awareness
        time_since_interaction = current_time - self.last_interaction
        
        if time_since_interaction > 60 and self.energy_level > 30:
            return 'seeking_attention'
        elif sensor_data.get('has_audio') and self.curiosity_level > 60:
            return 'audio_curious'
        elif self.energy_level < 30:
            return 'calm'
        else:
            return 'neutral'
    
    def _execute_behavior(self, behavior, color_func, volume):
        """Execute AI behavior with Penn State personality integration."""
        if self.debug_audio:
            print("[UFO_AI] Executing behavior: %s (School Spirit: %d)" % (behavior, self.school_spirit))
        
        if behavior == 'excited_penn_state_fan':
            self._excited_penn_state_behavior(color_func, volume)
        elif behavior == 'show_school_spirit':
            self._subtle_penn_state_pride(color_func, volume)
        elif behavior == 'audio_curious':
            self._audio_curious_behavior(color_func)
        elif behavior == 'seeking_attention':
            self._seeking_attention_behavior(color_func, volume)
        elif behavior == 'excited':
            self._excited_behavior(color_func)
        elif behavior == 'investigate':
            self._investigate_behavior(color_func)
        elif behavior == 'calm':
            self._calm_behavior(color_func)
        else:
            self._neutral_behavior(color_func)
    
    def _excited_penn_state_behavior(self, color_func, volume):
        """Special excited behavior for Penn State fans."""
        blue = (0, 50, 255)  # Penn State blue
        
        # Quick blue flashes
        for flash in range(3):
            for i in range(10):
                self.hardware.pixels[i] = blue
            self.hardware.pixels.show()
            time.sleep(0.1)
            
            self.hardware.clear_pixels()
            self.hardware.pixels.show()
            time.sleep(0.1)
        
        # Play a brief celebratory tone
        if volume > 0:
            self.hardware.play_tone_if_enabled(440, 0.3, volume)  # Happy A note
    
    def _subtle_penn_state_pride(self, color_func, volume):
        """Subtle display of Penn State school spirit."""
        blue = (0, 30, 200)  # Dimmer Penn State blue
        
        # Brief blue pulse
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
        
        # Searching pattern - pixels move in seeking pattern
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
            # Bright flash
            for i in range(10):
                intensity = 200 if self.school_spirit > 50 else 150
                self.hardware.pixels[i] = color_func(intensity)
            self.hardware.pixels.show()
            
            if volume > 0 and pulse == 2 and self.school_spirit > 60:
                # Occasional Penn State reference when seeking attention
                self.hardware.play_tone_if_enabled(330, 0.2, volume)  # E note
            
            time.sleep(0.3)
            
            # Fade
            self.hardware.clear_pixels()
            self.hardware.pixels.show()
            time.sleep(0.2)
    
    def _excited_behavior(self, color_func):
        """Standard excited behavior."""
        for flash in range(4):
            for i in range(10):
                self.hardware.pixels[i] = color_func(200)
            self.hardware.pixels.show()
            time.sleep(0.15)
            
            self.hardware.clear_pixels()
            self.hardware.pixels.show()
            time.sleep(0.1)
    
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
    
    def _calm_behavior(self, color_func):
        """Calm, gentle behavior."""
        self.mood = 'calm'
        
        # Gentle breathing pattern
        for phase in range(20):
            intensity = int(30 + 50 * abs(sin(phase / 3.14)))
            
            for i in range(10):
                self.hardware.pixels[i] = color_func(intensity)
            self.hardware.pixels.show()
            time.sleep(0.15)
    
    def _neutral_behavior(self, color_func):
        """Standard neutral behavior."""
        # Simple rotation
        for pos in range(5):
            self.hardware.clear_pixels()
            
            main_pos = pos * 2
            self.hardware.pixels[main_pos] = color_func(100)
            self.hardware.pixels[(main_pos + 1) % 10] = color_func(60)
            
            self.hardware.pixels.show()
            time.sleep(0.2)
    
    def _update_long_term_memory(self, sensor_data):
        """Update long-term memory with sensor data and experiences."""
        current_time = time.monotonic()
        
        # Ensure experiences dict exists
        if 'experiences' not in self.long_term_memory:
            self.long_term_memory['experiences'] = {}
        
        # Update interaction statistics
        if 'total_interactions' not in self.long_term_memory['experiences']:
            self.long_term_memory['experiences']['total_interactions'] = 0
        
        if sensor_data.get('tap_detected') or sensor_data.get('shake_detected'):
            self.long_term_memory['experiences']['total_interactions'] += 1
        
        # Decay energy over time
        if current_time % 5 < 1:  # Every ~5 seconds
            self.energy_level = max(20, self.energy_level - 1)
        
        # Save memory periodically
        self._save_long_term_memory()
    
    def record_successful_attention(self):
        """Record successful attention-seeking for learning."""
        if 'relationships' not in self.long_term_memory:
            self.long_term_memory['relationships'] = {}
        
        trust_level = self.long_term_memory['relationships'].get('trust_level', 0.5)
        self.long_term_memory['relationships']['trust_level'] = min(1.0, trust_level + 0.05)
        
        print("[UFO_AI] 💚 Trust relationship improved!")

# Helper function for sin calculation (basic approximation)
def sin(x):
    """Basic sine approximation for LED breathing effects."""
    # Simple sine approximation for breathing patterns
    x = x % (2 * 3.14159)
    if x < 3.14159:
        return x / 3.14159
    else:
        return (2 * 3.14159 - x) / 3.14159
