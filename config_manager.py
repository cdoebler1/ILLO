# Charles Doebler at Feral Cat AI
# Configuration Manager - Handles all configuration loading and saving

import json


class ConfigManager:
    def __init__(self):
        """Initialize Configuration Manager."""
        print("[CONFIG] Configuration Manager initialized")
    
    def load_config(self):
        """
        Load configuration from the config.json file.
        Returns simplified config without debug flags and volume.
        """
        try:
            with open('config.json') as config_file:
                data = json.load(config_file)
            
            return {
                'routine': data['routine'],
                'mode': data['mode'], 
                'name': data['name'],
                'college_spirit_enabled': data.get('college_spirit_enabled', True),
                'college': data.get('college', 'none'),
                'ufo_persistent_memory': data.get('ufo_persistent_memory', False),
                'college_chant_detection_enabled': data.get('college_chant_detection_enabled', True)
            }
        except Exception as e:
            print("[CONFIG] ❌ Failed to load config: %s" % str(e))
            # Return defaults
            return {
                'routine': 1,
                'mode': 1,
                'name': 'ILLO',
                'college_spirit_enabled': True,
                'college': 'none',
                'ufo_persistent_memory': False,
                'college_chant_detection_enabled': True
            }
    
    def save_config(self, config):
        """
        Save current configuration to config.json file.
        
        Args:
            config: Dictionary with configuration values
        """
        try:
            # Ensure we have all required fields
            config_data = {
                'routine': config.get('routine', 1),
                'mode': config.get('mode', 1),
                'name': config.get('name', 'ILLO'),
                'college_spirit_enabled': config.get('college_spirit_enabled', True),
                'college': config.get('college', 'none'),
                'ufo_persistent_memory': config.get('ufo_persistent_memory', False),
                'college_chant_detection_enabled': config.get('college_chant_detection_enabled', True)
            }
            
            with open('config.json', 'w') as config_file:
                json.dump(config_data, config_file)
            
            print("[CONFIG] ⚙️ Configuration saved: Routine %d, Mode %d" % 
                  (config_data['routine'], config_data['mode']))
            return True
            
        except (OSError, RuntimeError) as e:
            print("[CONFIG] ❌ Failed to save config: %s" % str(e))
            return False
