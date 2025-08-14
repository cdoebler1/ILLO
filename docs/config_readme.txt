UFO Configuration Settings
==========================

config.json field descriptions:

name (string): Bluetooth device name for the UFO
  - Used for BLE advertising and device identification
  - Example: "UFO" (default), "Illo", etc.
  - Useful when running multiple UFOs for identification

routine (integer 1-4): Default routine selection
  1 = UFOIntelligence (AI behavior; default)
  2 = IntergalacticCruising (audio-reactive lights)
  3 = Meditate (breathing patterns)
  4 = DanceParty (standalone beat detection; BLE sync disabled for memory safety)

mode (integer 1-3): Default color theme
  1 = Rainbow wheel colors
  2 = Pink variations  
  3 = Blue variations

volume (integer 0-1): Default sound setting
  0 = Silent (lights only)
  1 = Sound enabled (lights + tones)
  Note: Overridden by physical switch position on Circuit Playground board

debug_bluetooth (boolean): Enable/disable Bluetooth debug logging
  true = Show BLE connection, scanning, and sync details in console
  false = Hide Bluetooth debug messages (default)
  Note: Dance Party runs standalone regardless of this setting

debug_audio (boolean): Enable/disable audio processing debug logging  
  true = Show beat detection energy levels and thresholds in console
  false = Hide audio analysis debug messages (default)

ufo_persistent_memory (boolean): Enable AI long-term memory between power cycles
  Default: true (AI personality/preferences are saved to ufo_memory.json between sessions)
  false = Resets AI memory on power cycle
  true = Saves AI personality/preferences to ufo_memory.json between sessions
  Note: Only affects UFO Intelligence routine; increases flash write cycles

Hardware Controls:
- Button A: Cycle through routines (1-4)
- Button B: Cycle through color modes (1-3)  
- Switch: Controls volume (On=1, Off=0) - overrides config setting
- Tap detection: Interact with AI and trigger responses
- Shake detection: Turbulence effects and energy boosts

Physical UFO Integration:
- Circuit Playground Bluefruit embedded in levitating UFO toy
- Battery-powered for untethered operation
- LED ring creates UFO lighting effects during levitation
- Microphone responds to ambient sound and music
- Motion sensors detect when UFO is disturbed or interacted with

Memory Usage Notes:
- Dance Party disables Bluetooth sync to prevent memory errors on 256KB RAM
- Persistent memory disabled by default to reduce flash wear on embedded system
- AI learning occurs in RAM during an active session regardless of persistence setting
- Memory optimization critical for stable levitation operation