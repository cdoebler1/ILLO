# Charles Doebler at Feral Cat AI
# Autonomous UFO Intelligence - Adaptive behavior simulation

from base_routine import BaseRoutine
from audio_processor import AudioProcessor
import time
import math
import random
import json

class UFOIntelligence(BaseRoutine):
    def __init__(self, enable_persistent_memory=None):
        super().__init__()
        self.audio = AudioProcessor()
        
        # Configure persistent memory based on parameter or config
        if enable_persistent_memory is None:
            self.persistent_memory = self._load_memory_config()
        else:
            self.persistent_memory = enable_persistent_memory
            
        # Long-term memory file (only used if persistent memory is enabled)
        self.memory_file = 'ufo_memory.json' if self.persistent_memory else None
        
        # AI-like state variables
        self.curiosity_level = 0.5      # 0.0 to 1.0
        self.energy_level = 0.7         # Current "energy" state
        self.mood = "neutral"           # neutral, excited, calm, investigating
        self.attention_focus = 0        # Which pixel the UFO is "looking" at
        
        # Short-term memory (in RAM)
        self.interaction_memory = []    # Recent interactions
        self.environment_baseline = 50  # Learned "normal" audio level
        
        # Long-term memory (persistent or RAM-only based on config)
        self.long_term_memory = self._load_long_term_memory()
        
        # Behavior timers
        self.last_decision = time.monotonic()
        self.decision_interval = 2.0    # How often UFO "thinks"
        self.last_interaction = 0
        self.autonomy_timer = 0
        self.last_memory_save = time.monotonic()
        
        # Environmental awareness
        self.audio_history = []
        self.movement_history = []
        self.ambient_learning = True
        
        # Apply learned preferences from memory
        self._apply_memory_on_startup()
        
        # Print memory configuration status
        if self.persistent_memory:
            print("[UFO AI] 💾 Persistent memory ENABLED - UFO will remember between sessions")
        else:
            print("[UFO AI] 🧠 RAM-only memory - UFO will forget on restart (safe mode)")
    
    def _load_memory_config(self):
        """Load persistent memory setting from config.json."""
        try:
            with open('config.json', 'r') as f:
                config = json.load(f)
                return config.get('ufo_persistent_memory', False)  # Default to False for safety
        except (OSError, ValueError, KeyError):
            print("[UFO AI] ⚠️ Could not load memory config - defaulting to RAM-only mode")
            return False
        
    def _load_long_term_memory(self):
        """Load persistent UFO memory from a JSON file or create default."""
        default_memory = {
            'personality': {
                'base_curiosity': 0.5,
                'preferred_colors': [],
                'favorite_interactions': [],
                'learned_environment': 50
            },
            'user_patterns': {
                'active_times': [],
                'interaction_frequency': [],
                'preferred_modes': {},
                'response_preferences': []
            },
            'experiences': {
                'total_interactions': 0,
                'memorable_events': [],
                'learned_behaviors': {},
                'adaptation_history': []
            },
            'relationships': {
                'trust_level': 0.5,
                'bonding_events': [],
                'user_recognition': {}
            },
            'metadata': {
                'first_boot': time.monotonic(),
                'total_runtime': 0,
                'memory_version': '1.0',
                'last_saved': 0,
                'persistent_mode': self.persistent_memory
            }
        }
        
        # If persistent memory is disabled, just return default (RAM-only)
        if not self.persistent_memory:
            print("[UFO AI] 🌟 Creating fresh UFO consciousness (RAM-only)")
            return default_memory
        
        # Try to load from file if persistent memory is enabled
        try:
            with open(self.memory_file, 'r') as f:
                memory = json.load(f)
                # Update metadata to reflect current persistent setting
                if 'metadata' not in memory:
                    memory['metadata'] = {}
                memory['metadata']['persistent_mode'] = True
                print("[UFO AI] 🧠 Long-term memory loaded successfully")
                return memory
        except (OSError, ValueError):
            print("[UFO AI] 🌟 Creating new UFO consciousness with persistent memory...")
            # Create and save the default memory
            if self._save_long_term_memory(default_memory):
                print("[UFO AI] ✅ Initial memory file created successfully")
            else:
                print("[UFO AI] ⚠️ Could not create memory file - switching to RAM-only mode")
                self.persistent_memory = False
                self.memory_file = None
            return default_memory
    
    def _save_long_term_memory(self, memory_data=None):
        """Save persistent UFO memory to a JSON file (if enabled)."""
        # If persistent memory is disabled, just update timestamp and return
        if not self.persistent_memory:
            self.last_memory_save = time.monotonic()
            return True
            
        try:
            if memory_data is None:
                memory_data = self.long_term_memory

            # Ensure metadata exists
            if 'metadata' not in memory_data:
                memory_data['metadata'] = {}

            memory_data['metadata']['last_saved'] = time.monotonic()
            memory_data['metadata']['persistent_mode'] = True

            # Calculate runtime safely
            current_time = time.monotonic()
            if hasattr(self, 'last_memory_save') and self.last_memory_save > 0:
                runtime_delta = current_time - self.last_memory_save
                current_runtime = memory_data['metadata'].get('total_runtime', 0)
                memory_data['metadata']['total_runtime'] = current_runtime + runtime_delta

            # Save with minimal memory footprint
            with open(self.memory_file, 'w') as f:
                json.dump(memory_data, f)

            self.last_memory_save = current_time
            return True

        except (OSError, MemoryError, ValueError) as e:
            print("[UFO AI] Memory save failed: %s" % str(e))
            if "Read-only filesystem" in str(e):
                print("[UFO AI] 🔒 Filesystem is read-only - switching to RAM-only mode")
                self.persistent_memory = False
                self.memory_file = None
            return False
        except Exception as e:
            print("[UFO AI] Unexpected error saving memory: %s" % str(e))
            return False
    
    def _apply_memory_on_startup(self):
        """Apply learned behaviors and preferences from memory."""
        personality = self.long_term_memory.get('personality', {})
        experiences = self.long_term_memory.get('experiences', {})
        relationships = self.long_term_memory.get('relationships', {})
        
        # Apply learned personality traits
        self.curiosity_level = personality.get('base_curiosity', 0.5)
        self.environment_baseline = personality.get('learned_environment', 50)
        
        # Adjust behavior based on total interactions
        total_interactions = experiences.get('total_interactions', 0)
        if total_interactions > 100:
            print("[UFO AI] 🎓 Experienced UFO - enhanced behaviors active")
            self.decision_interval = 1.5  # More responsive
        elif total_interactions > 50:
            print("[UFO AI] 🤖 Mature UFO - balanced behaviors")
            self.decision_interval = 2.0
        else:
            print("[UFO AI] 👶 Young UFO - learning mode")
            self.decision_interval = 2.5  # More cautious
        
        # Adjust trust and energy based on relationship
        trust_level = relationships.get('trust_level', 0.5)
        if trust_level > 0.8:
            self.energy_level = 0.8  # More energetic with a trusted user
            print("[UFO AI] 💚 High trust relationship detected")
        elif trust_level < 0.3:
            self.energy_level = 0.4  # More reserved with new user
            self.curiosity_level = max(0.7, self.curiosity_level)  # But more curious
            print("[UFO AI] 🤔 Building trust relationship")

    def run(self, mode, volume):
        """Main AI routine - UFO demonstrates intelligent behavior."""
        try:
            current_time = time.monotonic()
            color_func = self.get_color_function(mode)

            # Gather environmental data
            self._collect_sensor_data()

            # UFO "thinks" and makes decisions
            if current_time - self.last_decision > self.decision_interval:
                self._make_intelligent_decision()
                self.last_decision = current_time

            # Execute current behavior
            self._execute_behavior(color_func, volume, current_time)

            # Learn and adapt
            self._update_learning()

            # Save memory periodically (every 60 seconds to reduce wear, only if persistent memory is enabled)
            if current_time - self.last_memory_save > 60:
                self._update_long_term_memory()

            # Record preferred mode usage (less frequently)
            if int(current_time) % 5 == 0:  # Every 5 seconds
                self._record_mode_preference(mode)

        except MemoryError:
            print("[UFO AI] Low memory - performing cleanup")
            self._cleanup_memory()
        except Exception as e:
            print("[UFO AI] Runtime error: %s" % str(e))
            # Continue operation in safe mode
            self.mood = "neutral"

    def _cleanup_memory(self):
        """Clean up memory when running low."""
        try:
            # Reduce history sizes
            if len(self.audio_history) > 10:
                self.audio_history = self.audio_history[-10:]
            if len(self.movement_history) > 5:
                self.movement_history = self.movement_history[-5:]
            if len(self.interaction_memory) > 20:
                self.interaction_memory = self.interaction_memory[-20:]

            # Clean up long-term memory
            experiences = self.long_term_memory.get('experiences', {})
            memorable_events = experiences.get('memorable_events', [])
            if len(memorable_events) > 20:
                experiences['memorable_events'] = memorable_events[-20:]

            print("[UFO AI] Memory cleanup completed")
        except Exception as e:
            print("[UFO AI] Cleanup error: %s" % str(e))
    
    def _collect_sensor_data(self):
        """Gather and analyze environmental data."""
        # Audio analysis
        np_samples = self.audio.record_samples()
        if len(np_samples) > 0:
            audio_level = sum(abs(s) for s in np_samples) / len(np_samples)
            self.audio_history.append(audio_level)
            if len(self.audio_history) > 20:
                self.audio_history.pop(0)
        
        # Accelerometer "awareness"
        accel_data = self.hardware.get_accelerometer()
        movement_magnitude = sum(abs(x) for x in accel_data)
        self.movement_history.append(movement_magnitude)
        if len(self.movement_history) > 10:
            self.movement_history.pop(0)
    
    def _make_intelligent_decision(self):
        """UFO's decision-making process. It appears to think and plan."""
        current_time = time.monotonic()
        
        # Use long-term memory to influence decisions
        experiences = self.long_term_memory.get('experiences', {})
        relationships = self.long_term_memory.get('relationships', {})
        
        # Analyze current environment vs learned baseline
        if self.audio_history:
            current_audio = sum(self.audio_history[-3:]) / min(3, len(self.audio_history))
            audio_change = abs(current_audio - self.environment_baseline)
        else:
            audio_change = 0
        
        # Analyze movement patterns
        recent_movement = sum(self.movement_history[-3:]) / min(3, len(self.movement_history)) if self.movement_history else 0
        
        # Time since last interaction affects mood
        time_since_interaction = current_time - self.last_interaction
        
        # Memory-influenced decision-making
        trust_level = relationships.get('trust_level', 0.5)
        
        # Decision logic - UFO chooses behavior based on analysis AND memory
        if audio_change > 100:  # Significant audio change detected
            self.mood = "investigating"
            self.curiosity_level = min(1.0, self.curiosity_level + 0.3)
            self.attention_focus = random.randint(0, 9)
            
            # Remember this type of investigation
            self._record_experience('audio_investigation', {
                'audio_change': audio_change,
                'time': current_time
            })
            memory_note = " (remembered)" if self.persistent_memory else " (session only)"
            print("[UFO AI] 🛸 Investigating audio anomaly..." + memory_note)
            
        elif recent_movement > 15:  # Physical interaction detected
            self.mood = "excited"
            self.energy_level = min(1.0, self.energy_level + 0.2)
            self.last_interaction = current_time
            
            # Build trust through positive interactions
            new_trust = min(1.0, trust_level + 0.05)
            self.long_term_memory['relationships']['trust_level'] = new_trust
            
            self._record_experience('physical_interaction', {
                'movement': recent_movement,
                'trust_change': new_trust - trust_level
            })
            memory_note = " (trust saved)" if self.persistent_memory else " (session trust)"
            print("[UFO AI] ✨ Responding to physical interaction! (trust +%.2f)%s" % (new_trust - trust_level, memory_note))
            
        elif time_since_interaction > 30:  # Been quiet for a while
            # Use memory to decide attention-seeking behavior
            if random.random() < self.curiosity_level:
                self.mood = "curious"
                self._initiate_attention_seeking()
                memory_note = " (using learned behaviors)" if self.persistent_memory else " (using session patterns)"
                print("[UFO AI] 👀 UFO seeks attention..." + memory_note)
            else:
                self.mood = "calm"
                self.energy_level = max(0.2, self.energy_level - 0.1)
                
        else:  # Normal operation - use personality from memory
            self.mood = "neutral"
            personality = self.long_term_memory.get('personality', {})
            base_energy = personality.get('base_energy', 0.5)
            self.energy_level = base_energy + (0.3 * math.sin(current_time * 0.1))
        
        # Adaptive decision timing - more experienced UFO thinks faster
        total_interactions = experiences.get('total_interactions', 0)
        experience_factor = min(total_interactions / 100, 0.5)  # Max 0.5 seconds faster
        self.decision_interval = 3.0 - (self.energy_level * 1.5) - experience_factor
    
    def _update_long_term_memory(self):
        """Update and save long-term memory periodically."""
        # Fix type issues by handling missing keys properly and using proper types
        if 'personality' not in self.long_term_memory:
            self.long_term_memory['personality'] = {
                'base_curiosity': 0.5,
                'learned_environment': 50.0
            }
        
        # Update personality based on recent behavior - ensure we store float values
        self.long_term_memory['personality']['base_curiosity'] = float(self.curiosity_level)
        self.long_term_memory['personality']['learned_environment'] = float(self.environment_baseline)
        
        # Save to file (if persistent memory is enabled)
        if self._save_long_term_memory():
            memory_status = "saved to file" if self.persistent_memory else "updated in RAM"
            print("[UFO AI] 💾 Long-term memory %s" % memory_status)
    
    def _record_experience(self, event_type, data):
        """Record significant experiences in long-term memory."""
        experience = {
            'type': event_type,
            'timestamp': time.monotonic(),
            'data': data
        }
        
        # Fix type issues by ensuring the proper dictionary structure
        if 'experiences' not in self.long_term_memory:
            self.long_term_memory['experiences'] = {
                'memorable_events': [],
                'total_interactions': 0
            }
        
        experiences = self.long_term_memory['experiences']
        
        if 'memorable_events' not in experiences:
            experiences['memorable_events'] = []
        
        # Now we can safely work with the list
        memorable_events = experiences['memorable_events']
        memorable_events.append(experience)
        
        # Keep only the most recent 50 memorable events
        if len(memorable_events) > 50:
            memorable_events.pop(0)
        
        # Update total interaction count - ensure we store an integer
        if event_type == 'physical_interaction':
            current_total = experiences.get('total_interactions', 0)
            if not isinstance(current_total, (int, float)):
                current_total = 0  # Reset if corrupted
            experiences['total_interactions'] = int(current_total) + 1
    
    def _record_mode_preference(self, mode):
        """Track which color modes the user prefers."""
        if 'user_patterns' not in self.long_term_memory:
            self.long_term_memory['user_patterns'] = {
                'preferred_modes': {}
            }
        
        user_patterns = self.long_term_memory['user_patterns']
        
        if 'preferred_modes' not in user_patterns:
            user_patterns['preferred_modes'] = {}
        
        # Now we can safely work with the dictionary
        preferred_modes = user_patterns['preferred_modes']
        
        mode_key = str(mode)
        current_count = preferred_modes.get(mode_key, 0)
        if not isinstance(current_count, (int, float)):
            current_count = 0  # Reset if corrupted
        preferred_modes[mode_key] = int(current_count) + 1
    
    def _initiate_attention_seeking(self):
        """UFO tries to get user's attention - uses learned successful behaviors."""
        try:
            # Use memory to choose effective attention behaviors
            experiences = self.long_term_memory.get('experiences', {})
            learned_behaviors = experiences.get('learned_behaviors', {})
            successful_attention = learned_behaviors.get('attention_seeking', [])

            if successful_attention and len(successful_attention) > 0:
                # Use a previously successful behavior
                self.current_attention_behavior = random.choice(successful_attention)
                behavior_source = "learned" if self.persistent_memory else "session"
                print("[UFO AI] Using %s attention behavior: %s" % (behavior_source, self.current_attention_behavior))
            else:
                # Use default behaviors
                attention_behaviors = [
                    "sweep_scan",      # Sweep around looking for user
                    "pulse_beacon",    # Beacon-like pulsing
                    "color_shift",     # Cycle through colors
                    "follow_sound"     # Track audio sources
                ]
                self.current_attention_behavior = random.choice(attention_behaviors)
                print("[UFO AI] Trying new attention behavior: %s" % self.current_attention_behavior)

            self.attention_start = time.monotonic()
        except Exception as e:
            print("[UFO AI] Error in attention seeking: %s" % str(e))
            self.current_attention_behavior = "pulse_beacon"  # Safe default

    def record_successful_attention(self):
        """Called when attention-seeking behavior successfully got user interaction."""
        try:
            if hasattr(self, 'current_attention_behavior'):
                # Safely ensure nested dictionary structure exists
                if 'experiences' not in self.long_term_memory:
                    self.long_term_memory['experiences'] = {}
                experiences = self.long_term_memory['experiences']

                if 'learned_behaviors' not in experiences:
                    experiences['learned_behaviors'] = {}
                learned_behaviors = experiences['learned_behaviors']

                if 'attention_seeking' not in learned_behaviors:
                    learned_behaviors['attention_seeking'] = []
                attention_seeking = learned_behaviors['attention_seeking']

                # Add this behavior to successful list (if not already there)
                if self.current_attention_behavior not in attention_seeking:
                    attention_seeking.append(self.current_attention_behavior)
                    memory_note = " (will remember)" if self.persistent_memory else " (for this session)"
                    print("[UFO AI] Learned: %s gets attention!%s" % (self.current_attention_behavior, memory_note))
        except Exception as e:
            print("[UFO AI] Error recording attention success: %s" % str(e))
    
    def _execute_behavior(self, color_func, volume, current_time):
        """Execute the UFO's current behavioral state."""
        if self.mood == "investigating":
            self._investigate_behavior(color_func, volume, current_time)
            
        elif self.mood == "excited":
            self._excited_behavior(color_func, volume, current_time)
            
        elif self.mood == "curious":
            self._curious_behavior(color_func, volume, current_time)
            
        elif self.mood == "calm":
            self._calm_behavior(color_func, current_time)
            
        else:  # neutral
            self._neutral_behavior(color_func, current_time)
    
    def _investigate_behavior(self, color_func, volume, current_time):
        """UFO investigates something interesting."""
        # Focus attention on specific area, sweep back and forth
        sweep_speed = 3.0 * self.curiosity_level
        sweep_position = (math.sin(current_time * sweep_speed) + 1) / 2  # 0 to 1
        
        # Clear all pixels
        self.hardware.clear_pixels()
        
        # Focused beam effect
        center_pixel = int(sweep_position * 9)
        intensity = int(200 + (self.curiosity_level * 55))
        
        # Bright center with dim adjacents
        self.hardware.pixels[center_pixel] = color_func(intensity)
        if center_pixel > 0:
            self.hardware.pixels[center_pixel - 1] = color_func(intensity // 3)
        if center_pixel < 9:
            self.hardware.pixels[center_pixel + 1] = color_func(intensity // 3)
        
        self.hardware.pixels.show()
        
        # Investigative sound
        if volume and random.random() < 0.1:
            freq = 400 + int(sweep_position * 200)
            self.hardware.play_tone_if_enabled(freq, 0.05, volume)
    
    def _excited_behavior(self, color_func, volume, current_time):
        """UFO shows excitement through rapid, bright patterns."""
        # Fast rainbow chase
        chase_speed = 8.0 * self.energy_level
        offset = int(current_time * chase_speed) % 10
        
        for i in range(10):
            pixel_phase = (i + offset) % 10
            intensity = int(150 + (105 * math.sin(pixel_phase * 0.628)))  # 0.628 = 2π/10
            self.hardware.pixels[i] = color_func(intensity)
        
        self.hardware.pixels.show()
        
        # Excited chirping
        if volume and random.random() < 0.2:
            freq = 600 + random.randint(0, 400)
            self.hardware.play_tone_if_enabled(freq, 0.08, volume)
    
    def _curious_behavior(self, color_func, volume, current_time):
        """UFO demonstrates curiosity through exploratory patterns."""
        if hasattr(self, 'current_attention_behavior'):
            behavior = self.current_attention_behavior
            
            if behavior == "sweep_scan":
                # Slow scan pattern
                scan_pos = int((current_time * 2) % 10)
                self.hardware.clear_pixels()
                self.hardware.pixels[scan_pos] = color_func(180)
                self.hardware.pixels[(scan_pos + 5) % 10] = color_func(100)
                
                # Attention-seeking sound
                if volume and random.random() < 0.05:
                    freq = 300 + (scan_pos * 50)
                    self.hardware.play_tone_if_enabled(freq, 0.1, volume)
                
            elif behavior == "pulse_beacon":
                # Rhythmic pulsing
                pulse = int(100 + 100 * abs(math.sin(current_time * 4)))
                for i in range(0, 10, 2):
                    self.hardware.pixels[i] = color_func(pulse)
                
                # Beacon sound
                if volume and pulse > 180:
                    self.hardware.play_tone_if_enabled(500, 0.05, volume)
                
            elif behavior == "color_shift":
                # Cycle through different colors
                hue_shift = int(current_time * 30) % 360
                shifted_color = self._shift_hue(color_func(150), hue_shift)
                for i in range(10):
                    self.hardware.pixels[i] = shifted_color
                    
            elif behavior == "follow_sound":
                # Point toward sound sources
                if self.audio_history:
                    recent_audio = self.audio_history[-1] if self.audio_history else 50
                    focus_pixel = int((recent_audio % 50) / 5)  # Map audio to pixel
                    self.hardware.clear_pixels()
                    self.hardware.pixels[focus_pixel] = color_func(200)
        
        self.hardware.pixels.show()
    
    def _calm_behavior(self, color_func, current_time):
        """Peaceful, meditative UFO behavior."""
        # Slow breathing pattern
        breath_cycle = 6.0  # 6 second breath cycle
        breath_phase = (current_time % breath_cycle) / breath_cycle
        
        if breath_phase < 0.5:  # Inhale
            intensity = int(80 + (breath_phase * 2 * 70))
        else:  # Exhale
            intensity = int(150 - ((breath_phase - 0.5) * 2 * 70))
        
        # All pixels breathe together
        breath_color = color_func(intensity)
        for i in range(10):
            self.hardware.pixels[i] = breath_color
        
        self.hardware.pixels.show()
    
    def _neutral_behavior(self, color_func, current_time):
        """Default UFO idle behavior with subtle variations."""
        # Gentle rotation with varying intensity
        base_intensity = 100 + int(30 * math.sin(current_time * 0.5))
        rotation_speed = 1.0 + (self.energy_level * 0.5)
        
        for i in range(10):
            phase = (current_time * rotation_speed + i * 0.628) % 6.28  # 2π
            pixel_intensity = base_intensity + int(20 * math.sin(phase))
            self.hardware.pixels[i] = color_func(pixel_intensity)
        
        self.hardware.pixels.show()
    
    def _update_learning(self):
        """UFO learns and adapts its behavior over time."""
        current_time = time.monotonic()
        
        # Learn environmental baseline
        if self.audio_history and len(self.audio_history) >= 10:
            recent_avg = sum(self.audio_history[-10:]) / 10
            # Slowly adjust baseline
            self.environment_baseline = (self.environment_baseline * 0.95) + (recent_avg * 0.05)
        
        # Adapt curiosity based on interaction frequency
        if current_time - self.last_interaction > 60:  # No interaction for 1 minute
            self.curiosity_level = min(1.0, self.curiosity_level + 0.01)
        elif current_time - self.last_interaction < 10:  # Recent interaction
            self.curiosity_level = max(0.2, self.curiosity_level - 0.01)
        
        # Store interaction patterns for future learning
        if len(self.interaction_memory) > 50:
            self.interaction_memory.pop(0)
        
        self.interaction_memory.append({
            'time': current_time,
            'mood': self.mood,
            'audio_level': self.audio_history[-1] if self.audio_history else 0,
            'energy': self.energy_level
        })
    
    @staticmethod
    def _shift_hue(color, hue_degrees):
        """Simple hue shifting for color variation."""
        # Basic color shifting - rotate through RGB components
        r, g, b = color
        shift = hue_degrees % 360
        
        if shift < 120:
            factor = shift / 120.0
            return int(r * (1-factor) + g * factor), int(g * (1-factor) + b * factor), b
        elif shift < 240:
            factor = (shift - 120) / 120.0
            return r, int(g * (1-factor) + b * factor), int(b * (1-factor) + r * factor)
        else:
            factor = (shift - 240) / 120.0
            return int(r * (1-factor) + b * factor), g, int(b * (1-factor) + r * factor)
