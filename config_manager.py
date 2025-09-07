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
                'college': data.get('college', 'none'),
                'college_spirit_enabled': data.get('college_spirit_enabled', True),
                'college_chant_detection_enabled': data.get('college_chant_detection_enabled', True),
                'ufo_persistent_memory': data.get('ufo_persistent_memory', False),
                'bluetooth_enabled': data.get('bluetooth_enabled', True)  # Default to enabled for compatibility
            }
        except Exception as e:
            print("[CONFIG] ❌ Failed to load config: %s" % str(e))
            # Return defaults
            return {
                'routine': 1,
                'mode': 1,
                'name': 'ILLO',
                'college': 'none',
                'college_spirit_enabled': True,
                'college_chant_detection_enabled': True,
                'ufo_persistent_memory': False,
                'bluetooth_enabled': True
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
                'college': config.get('college', 'none'),
                'college_spirit_enabled': config.get('college_spirit_enabled', True),
                'college_chant_detection_enabled': config.get('college_chant_detection_enabled', True),
                'ufo_persistent_memory': config.get('ufo_persistent_memory', False),
                'bluetooth_enabled': config.get('bluetooth_enabled', True)
            }
            
            with open('config.json', 'w') as config_file:
                # Manually format JSON with line breaks for CircuitPython compatibility
                config_file.write('{\n')
                config_file.write('  "routine": %d,\n' % config_data['routine'])
                config_file.write('  "mode": %d,\n' % config_data['mode'])
                config_file.write('  "name": "%s",\n' % config_data['name'])
                config_file.write('  "college": "%s",\n' % config_data['college'])
                config_file.write('  "college_spirit_enabled": %s,\n' % ('true' if config_data['college_spirit_enabled'] else 'false'))
                config_file.write('  "college_chant_detection_enabled": %s,\n' % ('true' if config_data['college_chant_detection_enabled'] else 'false'))
                config_file.write('  "ufo_persistent_memory": %s,\n' % ('true' if config_data['ufo_persistent_memory'] else 'false'))
                config_file.write('  "bluetooth_enabled": %s\n' % ('true' if config_data['bluetooth_enabled'] else 'false'))
                config_file.write('}\n')
            
            print("[CONFIG] ⚙️ Configuration saved: Routine %d, Mode %d, BT: %s" % 
                  (config_data['routine'], config_data['mode'], config_data['bluetooth_enabled']))
            return True
            
        except (OSError, RuntimeError) as e:
            print("[CONFIG] ❌ Failed to save config: %s" % str(e))
            return False
