import json


class ConfigManager:

    @staticmethod
    def load_config():
        """
        Load configuration from the config.json file.
        Returns simplified config without debug flags and volume.
        """
        try:
            with open('config.json') as config_file:
                data = json.load(config_file)

            return {
                'name': data.get('name', 'ILLO'),
                'routine': data['routine'],
                'mode': data['mode'],
                'bluetooth_enabled': data.get('bluetooth_enabled', True),
                'college': data.get('college', 'none'),
                'college_spirit_enabled': data.get('college_spirit_enabled', True),
                'ufo_persistent_memory': data.get('ufo_persistent_memory', True),
                'meditate_adaptive_timing': data.get('meditate_adaptive_timing', True),
                'meditate_ultra_dim': data.get('meditate_ultra_dim', True),
                'college_chant_detection_enabled': data.get(
                    'college_chant_detection_enabled', False)
            }
        except Exception as e:
            print("[CONFIG] ❌ Failed to load config: %s" % str(e))
            # Return defaults
            return {
                'name': 'ILLO',
                'routine': 1,
                'mode': 1,
                'bluetooth_enabled': True,
                'college': 'none',
                'college_spirit_enabled': True,
                'ufo_persistent_memory': True,
                'meditate_adaptive_timing': True,
                'meditate_ultra_dim': True,
                'college_chant_detection_enabled': False
            }

    @staticmethod
    def save_config(config):
        """
        Save current configuration to config.json file.

        Args:
            config: Dictionary with configuration values
        """
        try:
            config_data = {
                'name': config.get('name', 'ILLO'),
                'routine': config.get('routine', 1),
                'mode': config.get('mode', 1),
                'bluetooth_enabled': config.get('bluetooth_enabled', True),
                'college': config.get('college', 'none'),
                'college_spirit_enabled': config.get('college_spirit_enabled', True),
                'ufo_persistent_memory': config.get('ufo_persistent_memory', True),
                'meditate_adaptive_timing': config.get('meditate_adaptive_timing',
                                                       True),
                'meditate_ultra_dim': config.get('meditate_ultra_dim', True),
                'is_leader': config.get('is_leader', False),
                'college_chant_detection_enabled': config.get(
                    'college_chant_detection_enabled', False)
            }
            with open('config.json', 'w') as config_file:
                config_file.write('{\n')
                config_file.write('  "name": "%s",\n' % config_data['name'])
                config_file.write('  "routine": %d,\n' % config_data['routine'])
                config_file.write('  "mode": %d,\n' % config_data['mode'])
                config_file.write('  "bluetooth_enabled": %s,\n' % str(
                    config_data['bluetooth_enabled']).lower())
                config_file.write('  "college": "%s",\n' % config_data['college'])
                config_file.write('  "college_spirit_enabled": %s,\n' % str(
                    config_data['college_spirit_enabled']).lower())
                config_file.write('  "ufo_persistent_memory": %s,\n' % str(
                    config_data['ufo_persistent_memory']).lower())
                config_file.write('  "meditate_adaptive_timing": %s,\n' % str(
                    config_data['meditate_adaptive_timing']).lower())
                config_file.write('  "meditate_ultra_dim": %s,\n' % str(
                    config_data['meditate_ultra_dim']).lower())
                config_file.write('  "college_chant_detection_enabled": %s\n' % str(
                    config_data['college_chant_detection_enabled']).lower())
                config_file.write('}\n')

            print(
                "[CONFIG] ⚙️ Configuration saved: Routine %d, Mode %d, BT: %s" %
                (config_data['routine'], config_data['mode'],
                 config_data['bluetooth_enabled']))
            return True

        except (OSError, RuntimeError) as e:
            print("[CONFIG] ❌ Failed to save config: %s" % str(e))
            return False