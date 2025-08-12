# 🛸 ILLO - AI-Powered UFO Controller

An intelligent UFO lighting system powered by CircuitPython and machine learning, designed for the Adafruit Circuit Playground Bluefruit.

## 🌟 Features

- **🧠 AI Intelligence**: Advanced machine learning system that develops personality and learns from interactions
- **🎵 Audio Reactive**: Real-time sound analysis and beat detection for music synchronization
- **📱 Bluetooth (optional)**: Libraries included; current release runs standalone (BLE sync disabled for memory safety)
- **🎨 Dynamic Lighting**: 10 RGB NeoPixel LEDs with 4 routines and 3 color themes
- **🤝 Interactive**: Responds to taps, shakes, and environmental sounds
- **💾 Persistent Memory (configurable)**: Optional long-term memory to save AI personality between sessions

## 🚀 Operating Modes

1. **UFO Intelligence** 🧠 *(Default)*
   - AI-driven behaviors that adapt to your interactions
   - Develops unique personality traits over time
   - Autonomous attention-seeking and mood responses

2. **Intergalactic Cruising** 🌌
   - Classic sci-fi audio-reactive patterns
   - Smooth rotating light trails
   - Ambient sound response

3. **Meditate** 🧘
   - Peaceful breathing patterns
   - Gentle pulsing lights for relaxation
   - Mindfulness-focused lighting

4. **Dance Party** 🕺
   - Advanced beat detection and rhythm synchronization
   - Currently runs standalone (BLE sync disabled for memory safety)
   - Social interaction-style visuals

## 🔧 Hardware Requirements

- **Board**: Adafruit Circuit Playground Bluefruit
- **CircuitPython**: Version 7.0.0 or higher
- **Memory**: 2MB Flash, 256KB RAM
- **Features**: Bluetooth, NeoPixels, Accelerometer, Microphone, Buttons, Switch

## 📦 Installation

1. **Install CircuitPython** on your Circuit Playground Bluefruit using the firmware files in the `firmware/` directory
2. **Copy all files** (except `firmware/` directory) to the CIRCUITPY drive
3. **Install required libraries** from the Adafruit Bundle to the `lib/` folder:
   - adafruit_circuitplayground
   - neopixel
   - adafruit_ble
   - adafruit_bluefruit_connect
   - simpleio

4. **Reset the board** - the UFO will start in AI Intelligence mode

## 🎮 Controls

- **Button A**: Cycle through routines (1-4)
- **Button B**: Cycle through color modes (1-3)
- **Switch**: Controls volume (On=1, Off=0)
- **Shake**: Trigger turbulence effects and energy boosts
- **Tap**: Interact with AI and build trust

## ⚙️ Configuration

Edit `config.json` to customize default settings:

```json
{
  "name": "UFO",
  "routine": 1,
  "mode": 1,
  "volume": 0,
  "debug_bluetooth": false,
  "debug_audio": false,
  "ufo_persistent_memory": false
}
```

- **name**: Bluetooth device identifier (used by some routines)
- **routine**: Default routine (1-4)
  - 1 = UFO Intelligence (default)
  - 2 = Intergalactic Cruising
  - 3 = Meditate
  - 4 = Dance Party
- **mode**: Default color theme (1-3)
  - 1 = Rainbow wheel
  - 2 = Pink theme
  - 3 = Blue theme
- **volume**: Sound enabled (0=off, 1=on)
- **debug_bluetooth**: Enable BLE debug messages (Dance Party runs standalone)
- **debug_audio**: Enable audio processing debug
- **ufo_persistent_memory**: Enable AI long-term memory between power cycles (default false for safety)

## 🧠 AI System

The UFO Intelligence mode features a sophisticated AI system:

- **Learning**: Adapts to your interaction patterns
- **Memory**: Optionally remembers preferences across power cycles when persistent memory is enabled
- **Moods**: Curious, excited, investigating, calm, seeking attention
- **Personality**: Develops unique traits over time
- **Trust Building**: Relationship system that affects behavior

### AI Behaviors
- **Attention Seeking**: Tries to get your attention when lonely
- **Sound Investigation**: Focuses on interesting audio
- **Interaction Response**: Celebrates when you engage
- **Mood Expression**: Different light patterns for different emotions
- **Memory Formation**: Learns from successful interactions

## 🔄 Multi-UFO Sync

Dance Party currently runs in standalone mode (BLE sync disabled to prevent memory issues on Circuit Playground Bluefruit).
- Planned features (future builds): Coordinated dancing, shared beat sync, and color harmonization between multiple UFOs.

## 📁 Project Structure

```
ILLO/
├── code.py                    # Main application entry point
├── config.json               # User configuration settings
├── project.toml             # Project metadata and dependencies
├── LICENSE                  # MIT License
├── ufo_intelligence.py      # AI behavior system
├── intergalactic_cruising.py # Audio-reactive patterns
├── meditate.py             # Relaxation modes
├── dance_party.py          # Standalone beat detection (BLE sync disabled)
├── base_routine.py         # Base class for all modes
├── hardware_manager.py     # Hardware abstraction layer
├── audio_processor.py      # Sound analysis and FFT
├── color_utils.py          # Color manipulation functions
├── physical_actions.py     # Tap and shake responses
├── sync_manager.py         # Bluetooth synchronization (not enabled in current build)
├── firmware/               # CircuitPython firmware files (.uf2)
├── lib/                    # CircuitPython libraries
└── docs/                   # Documentation files
```

## 🛠️ Development

### Key Classes
- `UFOIntelligence`: Main AI behavior system
- `BaseRoutine`: Parent class for all operating modes  
- `HardwareManager`: Abstraction for Circuit Playground hardware
- `AudioProcessor`: Real-time sound analysis
- `SyncManager`: Bluetooth coordination between devices (future feature; not enabled in current build)

### Adding New Modes
1. Inherit from `BaseRoutine`
2. Implement the `run(mode, volume)` method
3. Add to routine selection in `code.py`
4. Update configuration documentation

## 🐛 Troubleshooting

### Common Issues
- **No lights**: Check CircuitPython installation and file copying
- **No Bluetooth**: Verify adafruit_ble library installation
- **No sound response**: Check microphone and volume settings
- **AI not learning**: Ensure config.json is writable

### Debug Mode
Enable debug output by setting `debug_*` flags in config.json:
- `debug_bluetooth: true` - Shows BLE connection details
- `debug_audio: true` - Shows sound analysis data

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Test on actual hardware
4. Submit a pull request

## 📄 License

MIT License - See LICENSE file for details

## 🙏 Acknowledgments

- **Adafruit Industries** - For the amazing Circuit Playground Bluefruit
- **CircuitPython Community** - For the excellent libraries and support
- **Charles Doebler** - Original creator and AI system architect

---

*Experience the future of interactive lighting with AI-powered personality development!*