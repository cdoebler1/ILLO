UFO Configuration Settings
==========================

config.json field descriptions:

name (string): Bluetooth device name for the UFO
  - Used for BLE advertising and device identification
  - Example: "Illo_4"

routine (integer 1-4): Default routine
  1 = UFOIntelligence (AI behavior; default)
  2 = IntergalacticCruising (audio-reactive lights)
  3 = Meditate (breathing patterns)
  4 = DanceParty (beat detection; runs standalone, BLE sync disabled)


mode (integer 1-3): Default color theme
  1 = Rainbow wheel colors
  2 = Pink variations  
  3 = Blue variations

volume (integer 0-1): Default sound setting
  0 = Silent (lights only)
  1 = Sound enabled (lights + tones)
  Note: Can be overridden by physical switch

debug_bluetooth (boolean): Enable/disable Bluetooth debug logging
  true = Show BLE connection, scanning, and sync details
  false = Hide Bluetooth debug messages

debug_audio (boolean): Enable/disable audio processing debug logging  
  true = Show beat detection energy levels and thresholds
  false = Hide audio analysis debug messages

ufo_persistent_memory (boolean): Enable AI long-term memory between power cycles
  false = Default (safer for storage wear and memory limits)
  true = Saves personality/preferences to ufo_memory.json