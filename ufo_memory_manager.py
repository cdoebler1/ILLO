
# Charles Doebler at Feral Cat AI
# UFO Memory Management System - College-Aware

import json
import time

class UFOMemoryManager:
    def __init__(self, persistent_memory=False):
        self.persistent_memory = persistent_memory
        self.memory_file = 'ufo_memory.json' if persistent_memory else None
        self.last_memory_save = time.monotonic()
        self.long_term_memory = self._load_long_term_memory()
        
        if persistent_memory:
            print("[UFO AI]  Persistent memory ENABLED - UFO will remember between sessions")
        else:
            print("[UFO AI]  RAM-only memory - UFO will forget on restart (safe mode)")

    def _get_default_memory_structure(self):
        """Create default memory structure with college support."""
        return {
            'personality': {
                'base_curiosity': 0.5,
                'base_energy': 0.7,
                'college_enthusiasm': 0.8,
                'preferred_colors': [],
                'favorite_interactions': [],
                'learned_environment': 50
            },
            'user_patterns': {
                'active_times': [],
                'interaction_frequency': [],
                'preferred_modes': {},
                'response_preferences': [],
                'college_interaction_success': 0
            },
            'experiences': {
                'total_interactions': 0,
                'memorable_events': [],
                'learned_behaviors': {},
                'adaptation_history': [],
                'college_celebrations': 0,
                'successful_chant_detections': 0
            },
            'relationships': {
                'trust_level': 0.5,
                'bonding_events': [],
                'user_recognition': {},
                'college_bond_strength': 0.5
            },
            'metadata': {
                'first_boot': time.monotonic(),
                'total_runtime': 0,
                'memory_version': '2.0',
                'last_saved': 0,
                'persistent_mode': self.persistent_memory,
                'college_support': True
            }
        }

    def ensure_memory_structure(self):
        """Ensure memory has all required fields with college support - PUBLIC METHOD."""
        default_structure = self._get_default_memory_structure()
        
        def ensure_nested_dict(target, source):
            for key, value in source.items():
                if key not in target:
                    target[key] = value
                elif isinstance(value, dict) and isinstance(target[key], dict):
                    ensure_nested_dict(target[key], value)
        
        ensure_nested_dict(self.long_term_memory, default_structure)

    def _load_long_term_memory(self):
        """Load persistent UFO memory with college support."""
        default_memory = self._get_default_memory_structure()
        
        if not self.persistent_memory:
            print("[UFO AI]  Creating fresh UFO consciousness (RAM-only)")
            return default_memory
        
        try:
            with open(self.memory_file, 'r') as f:
                memory = json.load(f)
                if 'metadata' not in memory:
                    memory['metadata'] = {}
                memory['metadata']['persistent_mode'] = True
                memory['metadata']['college_support'] = True
                print("[UFO AI]  Long-term memory loaded successfully")
                return memory
        except (OSError, ValueError):
            print("[UFO AI]  Creating new UFO consciousness with persistent memory...")
            if self._save_memory(default_memory):
                print("[UFO AI] ✅ Initial memory file created successfully")
            return default_memory

    def _save_memory(self, memory_data=None):
        """Save persistent UFO memory."""
        if not self.persistent_memory:
            self.last_memory_save = time.monotonic()
            return True
            
        try:
            if memory_data is None:
                memory_data = self.long_term_memory

            if 'metadata' not in memory_data:
                memory_data['metadata'] = {}

            memory_data['metadata']['last_saved'] = time.monotonic()
            memory_data['metadata']['persistent_mode'] = True
            memory_data['metadata']['college_support'] = True

            current_time = time.monotonic()
            if hasattr(self, 'last_memory_save') and self.last_memory_save > 0:
                runtime_delta = current_time - self.last_memory_save
                current_runtime = memory_data['metadata'].get('total_runtime', 0)
                memory_data['metadata']['total_runtime'] = current_runtime + runtime_delta

            with open(self.memory_file, 'w') as f:
                json.dump(memory_data, f)

            self.last_memory_save = current_time
            return True

        except (OSError, MemoryError, ValueError) as e:
            print("[UFO AI] Memory save failed: %s" % str(e))
            if "Read-only filesystem" in str(e):
                print("[UFO AI]  Switching to RAM-only mode")
                self.persistent_memory = False
                self.memory_file = None
            return False

    def update_memory(self, curiosity_level, energy_level, environment_baseline):
        """Update and save long-term memory."""
        self.ensure_memory_structure()
        
        self.long_term_memory['personality']['base_curiosity'] = float(curiosity_level)
        self.long_term_memory['personality']['base_energy'] = float(energy_level)
        self.long_term_memory['personality']['learned_environment'] = float(environment_baseline)
        
        if self._save_memory():
            memory_status = "saved to file" if self.persistent_memory else "updated in RAM"
            print("[UFO AI]  Long-term memory %s" % memory_status)

    def record_college_interaction(self, interaction_type, success=True):
        """Record college-related interactions."""
        self.ensure_memory_structure()
        
        if success:
            current_success = self.long_term_memory['user_patterns'].get('college_interaction_success', 0)
            self.long_term_memory['user_patterns']['college_interaction_success'] = current_success + 1
            
            if interaction_type == 'chant_detection':
                current_detections = self.long_term_memory['experiences'].get('successful_chant_detections', 0)
                self.long_term_memory['experiences']['successful_chant_detections'] = current_detections + 1
            elif interaction_type == 'celebration':
                current_celebrations = self.long_term_memory['experiences'].get('college_celebrations', 0)
                self.long_term_memory['experiences']['college_celebrations'] = current_celebrations + 1

    def record_experience(self, event_type, data):
        """Record significant experiences in memory."""
        self.ensure_memory_structure()
        
        experience = {
            'type': event_type,
            'timestamp': time.monotonic(),
            'data': data
        }
        
        memorable_events = self.long_term_memory['experiences']['memorable_events']
        memorable_events.append(experience)
        
        if len(memorable_events) > 50:
            memorable_events.pop(0)
        
        if event_type == 'physical_interaction':
            current_total = self.long_term_memory['experiences'].get('total_interactions', 0)
            self.long_term_memory['experiences']['total_interactions'] = int(current_total) + 1

    def record_successful_attention(self, behavior):
        """Record successful attention-seeking behavior."""
        self.ensure_memory_structure()
        
        learned_behaviors = self.long_term_memory['experiences']['learned_behaviors']
        if 'attention_seeking' not in learned_behaviors:
            learned_behaviors['attention_seeking'] = []
        
        attention_behaviors = learned_behaviors['attention_seeking']
        if behavior not in attention_behaviors:
            attention_behaviors.append(behavior)
            memory_note = " (will remember)" if self.persistent_memory else " (for this session)"
            print("[UFO AI] Learned: %s gets attention!%s" % (behavior, memory_note))

    def cleanup_memory(self):
        """Clean up memory when running low."""
        try:
            memorable_events = self.long_term_memory['experiences']['memorable_events']
            if len(memorable_events) > 20:
                self.long_term_memory['experiences']['memorable_events'] = memorable_events[-20:]
            print("[UFO AI] Memory cleanup completed")
        except Exception as e:
            print("[UFO AI] Memory cleanup error: %s" % str(e))
