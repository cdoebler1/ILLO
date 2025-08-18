# Charles Doebler at Feral Cat AI
# UFO AI Core Decision Making - College-Aware

import time
import random
import math

class UFOAICore:
    def __init__(self, memory_manager, college_system):
        self.memory_manager = memory_manager
        self.college_system = college_system
        
        # AI state variables
        self.curiosity_level = 0.5
        self.energy_level = 0.7
        self.mood = "neutral"
        self.attention_focus = 0
        
        # Behavior timers
        self.last_decision = time.monotonic()
        self.decision_interval = 2.0
        self.last_interaction = 0
        self.autonomy_timer = 0
        
        # Attention seeking
        self.current_attention_behavior = "pulse_beacon"
        self.attention_start = 0
        
        # Apply memory-based personality
        self._apply_memory_on_startup()

    def _set_experience_level(self, total_interactions):
        """Set UFO experience level based on interaction history."""
        if total_interactions > 100:
            self.decision_interval = 1.5
            print("[UFO AI]  Experienced UFO - enhanced behaviors active")
        elif total_interactions > 50:
            self.decision_interval = 2.0
            print("[UFO AI]  Mature UFO - balanced behaviors")
        else:
            self.decision_interval = 2.5
            print("[UFO AI]  Young UFO - learning mode")

    def _apply_memory_on_startup(self):
        """Apply learned behaviors and preferences from memory."""
        self.memory_manager.ensure_memory_structure()
        
        personality = self.memory_manager.long_term_memory['personality']
        experiences = self.memory_manager.long_term_memory['experiences']
        relationships = self.memory_manager.long_term_memory['relationships']
        
        # Apply personality traits
        self.curiosity_level = personality.get('base_curiosity', 0.5)
        self.energy_level = personality.get('base_energy', 0.7)
        
        # Set experience level
        total_interactions = experiences.get('total_interactions', 0)
        self._set_experience_level(total_interactions)
        
        # Apply relationship-based adjustments
        trust_level = relationships.get('trust_level', 0.5)
        college_bond = relationships.get('college_bond_strength', 0.5)
        
        if trust_level > 0.8:
            self.energy_level = min(1.0, self.energy_level + 0.1)
            print("[UFO AI]  High trust relationship detected")
        elif trust_level < 0.3:
            self.energy_level = max(0.4, self.energy_level - 0.1)
            self.curiosity_level = min(1.0, self.curiosity_level + 0.2)
            print("[UFO AI]  Building trust relationship")
        
        # College bond affects school spirit
        if self.college_system.college_spirit_enabled and college_bond > 0.7:
            self.college_system.school_spirit = min(100, self.college_system.school_spirit + 10)
            print("[UFO AI]  Strong %s bond detected!" % self.college_system.college_manager.get_college_name())

    def should_make_decision(self):
        """Check if it's time for UFO to make a decision."""
        current_time = time.monotonic()
        return current_time - self.last_decision > self.decision_interval

    def make_intelligent_decision(self, audio_history, movement_history, environment_baseline):
        """UFO's decision-making process with college awareness."""
        current_time = time.monotonic()
        
        # Get memory data
        experiences = self.memory_manager.long_term_memory['experiences']
        relationships = self.memory_manager.long_term_memory['relationships']
        
        # Analyze environment
        if audio_history:
            current_audio = sum(audio_history[-3:]) / min(3, len(audio_history))
            audio_change = abs(current_audio - environment_baseline)
        else:
            audio_change = 0
        
        recent_movement = (sum(movement_history[-3:]) / min(3, len(movement_history)) 
                          if movement_history else 0)
        time_since_interaction = current_time - self.last_interaction
        
        # Decision logic with college influence
        trust_level = relationships.get('trust_level', 0.5)
        
        if audio_change > 100:  # Significant audio change
            self.mood = "investigating"
            self.curiosity_level = min(1.0, self.curiosity_level + 0.3)
            self.attention_focus = random.randint(0, 9)
            
            self.memory_manager.record_experience('audio_investigation', {
                'audio_change': audio_change,
                'time': current_time
            })
            # memory_note = " (remembered)" if self.memory_manager.persistent_memory else " (session only)"
            # print("[UFO AI]  Investigating audio anomaly..." + memory_note)
            
        elif recent_movement > 15:  # Physical interaction
            self.mood = "excited"
            self.energy_level = min(1.0, self.energy_level + 0.2)
            self.last_interaction = current_time
            
            # Build trust and college bond
            new_trust = min(1.0, trust_level + 0.05)
            self.memory_manager.long_term_memory['relationships']['trust_level'] = new_trust
            
            if self.college_system.college_spirit_enabled:
                current_bond = relationships.get('college_bond_strength', 0.5)
                new_bond = min(1.0, current_bond + 0.03)
                self.memory_manager.long_term_memory['relationships']['college_bond_strength'] = new_bond
                self.college_system.update_school_spirit(interaction_success=True)
            
            self.memory_manager.record_experience('physical_interaction', {
                'movement': recent_movement,
                'trust_change': new_trust - trust_level
            })
            memory_note = " (trust saved)" if self.memory_manager.persistent_memory else " (session trust)"
            print("[UFO AI] ✨ Responding to physical interaction! (trust +%.2f)%s" % 
                  (new_trust - trust_level, memory_note))
            
        elif time_since_interaction > 30:  # Been quiet for a while
            if random.random() < self.curiosity_level:
                self.mood = "curious"
                self._initiate_attention_seeking()
                memory_note = " (using learned behaviors)" if self.memory_manager.persistent_memory else " (using session patterns)"
                print("[UFO AI]  UFO seeks attention..." + memory_note)
            else:
                self.mood = "calm"
                self.energy_level = max(0.2, self.energy_level - 0.1)
        else:
            # Normal operation
            self.mood = "neutral"
            base_energy = self.memory_manager.long_term_memory['personality'].get('base_energy', 0.5)
            self.energy_level = base_energy + (0.3 * math.sin(current_time * 0.1))
        
        # Adaptive decision timing
        total_interactions = experiences.get('total_interactions', 0)
        experience_factor = min(total_interactions / 100, 0.5)
        self.decision_interval = 3.0 - (self.energy_level * 1.5) - experience_factor
        
        self.last_decision = current_time

    def _initiate_attention_seeking(self):
        """UFO tries to get attention using learned behaviors."""
        try:
            experiences = self.memory_manager.long_term_memory['experiences']
            learned_behaviors = experiences.get('learned_behaviors', {})
            successful_attention = learned_behaviors.get('attention_seeking', [])

            if successful_attention:
                self.current_attention_behavior = random.choice(successful_attention)
                behavior_source = "learned" if self.memory_manager.persistent_memory else "session"
                print("[UFO AI] Using %s attention behavior: %s" % 
                      (behavior_source, self.current_attention_behavior))
            else:
                attention_behaviors = ["sweep_scan", "pulse_beacon", "color_shift", "follow_sound"]
                self.current_attention_behavior = random.choice(attention_behaviors)
                print("[UFO AI] Trying new attention behavior: %s" % self.current_attention_behavior)

            self.attention_start = time.monotonic()
        except Exception as e:
            print("[UFO AI] Error in attention seeking: %s" % str(e))
            self.current_attention_behavior = "pulse_beacon"

    def record_successful_attention(self):
        """Record successful attention-seeking behavior."""
        if hasattr(self, 'current_attention_behavior'):
            self.memory_manager.record_successful_attention(self.current_attention_behavior)
