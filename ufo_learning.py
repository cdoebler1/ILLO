# Charles Doebler at Feral Cat AI
# UFO Learning and Sensor Processing System

import time

class UFOLearningSystem:
    def __init__(self, memory_manager, college_system):
        self.memory_manager = memory_manager
        self.college_system = college_system
        
        # Learning state
        self.interaction_memory = []
        self.environment_baseline = 50
        self.audio_history = []
        self.movement_history = []
        self.ambient_learning = True

    def collect_sensor_data_enhanced(self, audio_processor, hardware, sound_enabled, chant_detection_enabled):
        """Enhanced sensor data collection - audio input ALWAYS active, chant detection optional."""
        # Audio analysis - ALWAYS process audio for AI decisions, regardless of sound output
        np_samples = audio_processor.record_samples()
        if len(np_samples) > 0:
            audio_level = sum(abs(s) for s in np_samples) / len(np_samples)
            self.audio_history.append(audio_level)
            if len(self.audio_history) > 20:
                self.audio_history.pop(0)
            
            # College chant detection - ONLY if explicitly enabled
            if (self.college_system.college_spirit_enabled and 
                chant_detection_enabled and  # New separate control
                self.college_system.is_college_celebration_ready()):
                
                try:
                    chant_detected = self.college_system.detect_college_chant(np_samples)
                    if chant_detected:
                        self.college_system.execute_college_celebration(hardware, sound_enabled)
                        self.memory_manager.record_college_interaction('chant_detection', True)
                        self._learn_from_audio_interaction(audio_level, 'college_chant')
                        return True  # College celebration triggered
                        
                except Exception as e:
                    print("[UFO AI] College detection error: %s" % str(e))
        
        # Accelerometer analysis - always active
        accel_data = hardware.get_accelerometer()
        movement_magnitude = sum(abs(x) for x in accel_data)
        self.movement_history.append(movement_magnitude)
        if len(self.movement_history) > 10:
            self.movement_history.pop(0)
        
        return False  # No college celebration triggered

    def _learn_from_audio_interaction(self, audio_level, interaction_type):
        """Learn from audio-based interactions."""
        try:
            # Update learning based on successful audio interaction
            if interaction_type == 'college_chant':
                # College interactions boost enthusiasm
                personality = self.memory_manager.long_term_memory.get('personality', {})
                current_enthusiasm = personality.get('college_enthusiasm', 0.8)
                new_enthusiasm = min(1.0, current_enthusiasm + 0.05)
                personality['college_enthusiasm'] = new_enthusiasm
                
                # Update college bond
                relationships = self.memory_manager.long_term_memory.get('relationships', {})
                current_bond = relationships.get('college_bond_strength', 0.5)
                new_bond = min(1.0, current_bond + 0.1)
                relationships['college_bond_strength'] = new_bond
                
                print("[UFO AI] 🏈 College bond strengthened! (+%.2f)" % 
                      (new_bond - current_bond))
            
            # Record the successful interaction pattern
            self.memory_manager.record_experience('successful_audio_interaction', {
                'audio_level': audio_level,
                'interaction_type': interaction_type,
                'frequency_category': self._categorize_frequency(audio_level)
            })
            
        except Exception as e:
            print("[UFO AI] Audio learning error: %s" % str(e))

    @staticmethod
    def _categorize_frequency(audio_level):
        """Categorize audio frequency for learning."""
        if audio_level < 20:
            return "quiet"
        elif audio_level < 60:
            return "normal"
        elif audio_level < 100:
            return "loud"
        else:
            return "very_loud"

    def update_learning(self, ai_core):
        """Update learning based on recent interactions."""
        current_time = time.monotonic()
        
        # Learn environmental baseline - always active regardless of sound output
        if self.audio_history and len(self.audio_history) >= 10:
            recent_avg = sum(self.audio_history[-10:]) / 10
            self.environment_baseline = (self.environment_baseline * 0.95) + (recent_avg * 0.05)
        
        # Adapt curiosity based on interaction frequency
        new_curiosity = ai_core.curiosity_level
        if current_time - ai_core.last_interaction > 60:
            new_curiosity = min(1.0, ai_core.curiosity_level + 0.01)
        elif current_time - ai_core.last_interaction < 10:
            new_curiosity = max(0.2, ai_core.curiosity_level - 0.01)
        
        ai_core.curiosity_level = new_curiosity
        
        # Update college spirit based on activity
        # self.college_system.update_school_spirit()
        
        # Store interaction patterns
        if len(self.interaction_memory) > 50:
            self.interaction_memory.pop(0)
        
        self.interaction_memory.append({
            'time': current_time,
            'mood': ai_core.mood,
            'audio_level': self.audio_history[-1] if self.audio_history else 0,
            'energy': ai_core.energy_level,
            'college_spirit': self.college_system.school_spirit
        })

    def cleanup_memory(self):
        """Clean up learning memory when low on resources."""
        try:
            if len(self.audio_history) > 10:
                self.audio_history = self.audio_history[-10:]
            if len(self.movement_history) > 5:
                self.movement_history = self.movement_history[-5:]
            if len(self.interaction_memory) > 20:
                self.interaction_memory = self.interaction_memory[-20:]
            
            print("[UFO AI] Learning memory cleanup completed")
        except Exception as e:
            print("[UFO AI] Learning cleanup error: %s" % str(e))
