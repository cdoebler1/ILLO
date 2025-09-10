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
                'college_chant_detection_enabled': data.get('college_chant_detection_enabled', True),
                'bluetooth_enabled': data.get('bluetooth_enabled', True),  # Default to enabled for compatibility
                # Meditation configuration entries
                'meditate_breath_pattern': data.get('meditate_breath_pattern', 1),  # 1-4 breathing patterns
                'meditate_adaptive_timing': data.get('meditate_adaptive_timing', True),  # Light-based timing adjustment
                'meditate_ultra_dim': data.get('meditate_ultra_dim', True)  # Ultra-low brightness mode
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
                'college_chant_detection_enabled': True,
                'bluetooth_enabled': True,
                # Meditation defaults
                'meditate_breath_pattern': 1,  # Default to 4-7-8 breathing
                'meditate_adaptive_timing': True,  # Enable light-based timing by default
                'meditate_ultra_dim': True  # Enable ultra-dim mode by default
            }

    def save_config(self, config):
        """
        Save current configuration to config.json file.
        
        Args:
            config: Dictionary with configuration values
        """
        try:
            # Ensure we have all required fields including meditation settings
            config_data = {
                'routine': config.get('routine', 1),
                'mode': config.get('mode', 1),
                'name': config.get('name', 'ILLO'),
                'college_spirit_enabled': config.get('college_spirit_enabled', True),
                'college': config.get('college', 'none'),
                'ufo_persistent_memory': config.get('ufo_persistent_memory', False),
                'college_chant_detection_enabled': config.get('college_chant_detection_enabled', True),
                'bluetooth_enabled': config.get('bluetooth_enabled', True),
                # Meditation configuration
                'meditate_breath_pattern': config.get('meditate_breath_pattern', 1),
                'meditate_adaptive_timing': config.get('meditate_adaptive_timing', True),
                'meditate_ultra_dim': config.get('meditate_ultra_dim', True)
            }
            with open('config.json', 'w') as config_file:
                config_file.write('{\n')
                config_file.write('  "routine": %d,\n' % config_data['routine'])
                config_file.write('  "mode": %d,\n' % config_data['mode'])
                config_file.write('  "name": "%s",\n' % config_data['name'])
                config_file.write('  "college_spirit_enabled": %s,\n' % str(config_data['college_spirit_enabled']).lower())
                config_file.write('  "college": "%s",\n' % config_data['college'])
                config_file.write('  "ufo_persistent_memory": %s,\n' % str(config_data['ufo_persistent_memory']).lower())
                config_file.write('  "college_chant_detection_enabled": %s,\n' % str(config_data['college_chant_detection_enabled']).lower())
                config_file.write('  "bluetooth_enabled": %s,\n' % str(config_data['bluetooth_enabled']).lower())
                config_file.write('  "meditate_breath_pattern": %d,\n' % config_data['meditate_breath_pattern'])
                config_file.write('  "meditate_adaptive_timing": %s,\n' % str(config_data['meditate_adaptive_timing']).lower())
                config_file.write('  "meditate_ultra_dim": %s\n' % str(config_data['meditate_ultra_dim']).lower())
                config_file.write('}\n')
            
            print("[CONFIG] ⚙️ Configuration saved: Routine %d, Mode %d, BT: %s, Meditate: P%d/A%s" % 
                  (config_data['routine'], config_data['mode'], config_data['bluetooth_enabled'],
                   config_data['meditate_breath_pattern'], config_data['meditate_adaptive_timing']))
            return True
            
        except (OSError, RuntimeError) as e:
            print("[CONFIG] ❌ Failed to save config: %s" % str(e))
            return False
