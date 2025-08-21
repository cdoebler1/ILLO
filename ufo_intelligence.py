# Charles Doebler at Feral Cat AI
# Autonomous UFO Intelligence - College-Aware AI System

from base_routine import BaseRoutine
from audio_processor import AudioProcessor
from ufo_memory_manager import UFOMemoryManager
from ufo_college_system import UFOCollegeSystem  
from ufo_ai_core import UFOAICore
from ufo_ai_behaviors import UFOAIBehaviors
from ufo_learning import UFOLearningSystem
import time

class UFOIntelligence(BaseRoutine):
    def __init__(self, device_name=None, debug_bluetooth=False, debug_audio=False,
                 persistent_memory=False, college_spirit_enabled=True, college="penn_state"):
        super().__init__()
        
        # Core components
        self.audio = AudioProcessor()
        self.device_name = device_name or "UFO"
        self.debug_bluetooth = debug_bluetooth
        self.debug_audio = debug_audio
        
        # Load chant detection setting from config
        try:
            import json
            with open('config.json', 'r') as f:
                config = json.load(f)
                self.chant_detection_enabled = config.get('college_chant_detection_enabled', False)
        except:
            self.chant_detection_enabled = False  # Default to disabled for safety
        
        # Initialize subsystems
        self.memory_manager = UFOMemoryManager(persistent_memory)
        self.college_system = UFOCollegeSystem(college_spirit_enabled, college)
        self.ai_core = UFOAICore(self.memory_manager, self.college_system)
        self.behaviors = UFOAIBehaviors(self.hardware, self.college_system)
        self.learning = UFOLearningSystem(self.memory_manager, self.college_system)
        
        print("[UFO AI] 🛸 %s Intelligence System Online" % self.device_name)
        if college_spirit_enabled:
            print("[UFO AI] 🏈 College spirit: %s" % 
                  self.college_system.college_manager.get_college_name())
            if self.chant_detection_enabled:
                print("[UFO AI] 🎤 Chant detection: ENABLED")
            else:
                print("[UFO AI] 🎤 Chant detection: DISABLED (random college behaviors active)")

    def run(self, mode, sound_enabled):
        """Main AI routine with separated sound output and audio input."""
        try:
            current_time = time.monotonic()
            color_func = self.get_color_function(mode)

            # Enhanced sensor data collection - audio input ALWAYS active
            # sound_enabled only controls output, not input processing
            college_celebration = self.learning.collect_sensor_data_enhanced(
                self.audio, self.hardware, sound_enabled, self.chant_detection_enabled)
            
            # Check for random college behaviors (when chant detection is off)
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

            # Execute current behavior (college-aware)
            self.behaviors.execute_behavior(
                self.ai_core.mood, color_func, sound_enabled, current_time,
                self.ai_core.curiosity_level, self.ai_core.energy_level,
                self.learning.audio_history
            )

            # Update learning systems - always active regardless of sound output
            self.learning.update_learning(self.ai_core)

            # Periodic memory saves
            if current_time - self.memory_manager.last_memory_save > 60:
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
            self.ai_core.mood = "neutral"

    def record_successful_attention(self):
        """Called when attention-seeking behavior gets user interaction."""
        self.ai_core.record_successful_attention()

    def _cleanup_memory(self):
        """Clean up memory when running low."""
        self.memory_manager.cleanup_memory()
        self.learning.cleanup_memory()

    # Expose key properties for compatibility with existing code
    @property
    def mood(self):
        return self.ai_core.mood
    
    @mood.setter  
    def mood(self, value):
        self.ai_core.mood = value

    @property
    def energy_level(self):
        return self.ai_core.energy_level
    
    @energy_level.setter
    def energy_level(self, value):
        self.ai_core.energy_level = value

    @property
    def last_interaction(self):
        return self.ai_core.last_interaction
    
    @last_interaction.setter
    def last_interaction(self, value):
        self.ai_core.last_interaction = value
