# 🛸 ILLO - Identified Little Levitating Object

Meet ILLO, your AI-powered UFO companion that reacts to your world and evolves with you.
ILLO listens, learns, and lights the surrounding space with mesmerizing animations that sync to music,
respond to touch, and adapt to your environment. **Proudly 3D printed with recycled PETG and Made in USA.**

## 🌟 Key Features

- **🧠 AI Intelligence**: Advanced learning system that develops unique personality traits over time
- **🎵 Music & Chant Detection**: Real-time audio analysis with synchronized lighting effects
- **🏫 College Spirit**: Recognizes fight songs and chants with team color displays
- **💾 Persistent Memory**: Remembers personality, moods, and preferences across power cycles
- **🎨 Dynamic Lighting**: 10 RGB NeoPixels with synchronized light shows
- **🌙 Smart Light Sensing**: Automatic brightness adjustment with adaptive dimming (2%-25%)
- **👋 Interactive Response**: Touch, shake, light changes, environmental sounds, and user interactions
- **📱 Bluetooth Ready**: Libraries included for future sync capabilities (currently standalone)
- **♻️ Sustainable**: 3D printed with recycled PETG plastic - environmentally responsible design
- **🇺🇸 Made in USA**: Designed, programmed, and manufactured domestically

## 🚀 Operating Modes

### 1. AI Intelligence 🧠 *(Default)*
- Autonomous AI behaviors that adapt to your interactions
- Environmental response and learning algorithms  
- Develops unique personality over time
- Memory management with behavioral evolution
- Attention-seeking and mood-based responses
- **Full interaction support**: Touch, shake, light changes, college chant detection

### 2. Intergalactic Cruising 🌌
- Smooth ambient lighting patterns with automatic brightness adjustment
- Real-time audio visualization with frequency-responsive patterns
- Bluetooth control support for advanced features
- Automatic dimming for perfect night light mode
- **Light-only interactions**: Environmental brightness control only

### 3. Meditate 🧘
- Calming breathing-pattern animations
- Soft color gradients for relaxation
- Mindfulness-focused lighting sequences
- **Light-only interactions**: Environmental brightness control only

### 4. Dance Party 🕺
- Advanced beat detection and music synchronization
- Dynamic light shows that pulse with the beat
- Music-reactive color patterns
- **Full interaction support**: Touch, shake, light changes for party energy

## 🌙 Smart Environmental Features

**Adaptive Brightness Control:**
- **Very Dark (< 30)**: 2% brightness - perfect nightlight visibility
- **Dark (30-59)**: 5% brightness - comfortable low-light ambiance  
- **Indoor (60-99)**: 10% brightness - normal indoor lighting
- **Bright Indoor (100-149)**: 15% brightness - well-lit room comfort
- **Very Bright (150-199)**: 20% brightness - bright room visibility
- **Daylight (200+)**: 25% brightness - maximum outdoor/bright conditions

**Light Interaction Detection:**
- Detects sudden changes in ambient light (shadows, hand waves, approaching)
- Triggers special response patterns when light interactions are detected
- Non-contact interaction method with instant visual feedback
- Builds AI trust and relationship scores through light-based play

## 🎵 Music System

ILLO features a sophisticated music player that handles:

- **Chants**: Short, repetitive team chants (played 3 times)
- **Fight Songs**: Full college fight songs (single play)
- **College Colors**: Automatic team color display during collegiate music
- **Tempo Matching**: Precise BPM synchronization with 16th note accuracy
- **Synchronized Lighting**: Music-reactive light shows with beat detection

## 🏫 College Integration

**Supported Colleges:**
- Penn State (primary implementation)
- Extensible system for additional colleges via JSON configuration

**College Features:**
- Fight song recognition and playback
- Team chant detection and celebration
- College color schemes and light patterns
- School spirit tracking and personality development
- Random college pride displays when chant detection is disabled

## 🔧 Hardware Requirements

- **Board**: Adafruit Circuit Playground Bluefruit
- **CircuitPython**: Version 7.0.0 or higher
- **Memory**: 2MB Flash, 256KB RAM minimum
- **Components**: 
  - 10x NeoPixel RGB LEDs
  - Built-in accelerometer & microphone
  - Light sensor for environmental adaptation
  - 2x tactile buttons + slide switch
  - Bluetooth radio (BLE)
- **Enclosure**: 3D printed from recycled PETG (Made in USA)

## 📦 Installation

### Quick Start
1. **Install CircuitPython** on your Circuit Playground Bluefruit
2. **Copy all project files** to the CIRCUITPY drive (except firmware/ directory)
3. **Install required libraries** to the `lib/` folder:
   ```
   adafruit_circuitplayground/
   neopixel.mpy
   adafruit_ble/
   adafruit_bluefruit_connect/
   simpleio.mpy
   ulab/
   ```
4. **Reset the board** - ILLO will start in AI Intelligence mode

### Detailed Installation Steps

1. **Download CircuitPython 7.0+** from [circuitpython.org](https://circuitpython.org/board/circuitplayground_bluefruit/)
2. **Flash CircuitPython** to your Circuit Playground Bluefruit
3. **Download ILLO** from the GitHub repository
4. **Copy these files** to the CIRCUITPY drive:
   - All `.py` files from the root directory
   - `colleges/` folder with college configuration files
   - `config.json` for system settings
5. **Download and install libraries** to the `lib/` folder:
   - From the CircuitPython Library Bundle, copy these to `lib/`:
     - `adafruit_circuitplayground/` (folder)
     - `neopixel.mpy`
     - `adafruit_ble/` (folder)
     - `adafruit_bluefruit_connect/` (folder)
     - `simpleio.mpy`
     - `ulab/` (folder) - for audio processing
6. **Verify installation** - the CIRCUITPY drive should look like this:
   ```
   CIRCUITPY/
   ├── code.py
   ├── config.json
   ├── All other .py files...
   ├── colleges/
   │   └── penn_state.json
   └── lib/
       ├── adafruit_circuitplayground/
       ├── adafruit_ble/
       ├── adafruit_bluefruit_connect/
       ├── ulab/
       ├── neopixel.mpy
       └── simpleio.mpy
   ```

### Boot Configuration
The slide switch controls storage mode during boot:
- **Development: Switch right + USB**: Sound off, read from local, read/write over USB
- **Testing: Switch left + USB**: Sound on, read/write from local, read over USB  
- **Operation: Switch right**: Sound off, read/write from local
- **Operation: Switch left**: Sound on, read/write from local

## 🎮 Controls

- **Button A**: Cycle through operating modes (1–4)
- **Button B**: Cycle through color themes (1–4)
- **Slide Switch**: Sound on/off + boot-time storage configuration
- **Touch/Tap**: Interact with the AI system and trigger responses
- **Shake**: Generate turbulence effects and energy responses
- **Light Changes**: Wave hand over or approach ILLO to trigger interaction responses

## 🏗️ System Architecture

ILLO uses a clean, modular architecture with centralized interaction management:
**Core Components:**

- **InteractionManager**: Centralized interaction detection and routing
- **LightManager**: All light sensing and brightness control
- **HardwareManager**: Low-level hardware abstraction
- **AudioProcessor**: Real-time audio analysis and frequency detection
- **ConfigManager**: Persistent configuration and settings

**AI Components (UFO Intelligence):**

- **UFOAICore**: Decision making, mood management, personality development
- **UFOLearningSystem**: Environmental learning and interaction history
- **UFOMemoryManager**: Persistent memory and experience storage
- **UFOAIBehaviors**: Behavior pattern execution and visual responses

**College System:**

- **UFOCollegeSystem**: College spirit management and celebration control
- **CollegeManager**: College data loading and color schemes
- **ChantDetector**: Audio pattern recognition for team chants
- **MusicPlayer**: Unified music playback with synchronized lighting

## 📁 Project Structure

ILLO/
├── code.py                      # Main application loop
├── config.json                 # System configuration  
├── boot.py                      # Boot configuration
├── base_routine.py              # Base class for modes
├── audio_processor.py           # Audio processing
├── hardware_manager.py          # Hardware abstraction
├── light_manager.py             # Light sensing and control
├── interaction_manager.py       # Interaction detection
├── config_manager.py            # Configuration management
├── memory_manager.py            # Memory utilities
├── physical_actions.py          # Physical feedback
├── sync_manager.py              # Device sync utilities
├── ufo_intelligence.py          # AI Intelligence mode
├── intergalactic_cruising.py    # Cruising mode
├── meditate.py                  # Meditation mode
├── dance_party.py               # Dance Party mode
├── ufo_ai_core.py              # AI decision making
├── ufo_ai_behaviors.py         # AI behaviors
├── ufo_learning.py             # AI learning system
├── ufo_memory_manager.py       # AI memory persistence
├── ufo_college_system.py       # College integration
├── college_manager.py          # College data management
├── chant_detector.py           # Chant recognition
├── music_player.py             # Music playback
├── color_utils.py              # Color functions
├── bluetooth_controller.py     # Bluetooth communication
├── ble_sample_code.py          # Bluetooth examples
├── colleges/
│   └── penn_state.json         # Penn State configuration
├── docs/                       # Documentation files
├── firmware/                   # CircuitPython firmware
└── lib/                        # Required libraries

## ⚙️ Configuration

ILLO uses `config.json` for system settings:

**Configuration Options:**

- `routine`: Default operating mode (1-4)
- `mode`: Default color theme (1-4)
- `name`: Device name for Bluetooth and identification
- `college_spirit_enabled`: Enable/disable college integration features
- `college`: College configuration to load (matches filename in colleges/)
- `ufo_persistent_memory`: Enable AI memory persistence across power cycles
- `college_chant_detection_enabled`: Enable real-time chant recognition
- `bluetooth_enabled`: Enable Bluetooth features (when implemented)

## 🚀 Development

**Recent Updates (v2.1.0):**

- ✅ Centralized light management architecture
- ✅ Adaptive brightness control (2%-25% range)
- ✅ Light-based interaction detection
- ✅ Improved college integration system
- ✅ Enhanced AI learning and memory systems
- ✅ Unified music player with synchronized lighting
- ✅ Modular interaction management

**Development Status:**

- Core AI system: **Complete**
- Light management: **Complete**
- College integration: **Complete**
- Music system: **Complete**
- Bluetooth features: **Libraries ready, implementation pending**

**Adding New Colleges:**

1. Create a new JSON file in the `colleges/` directory
2. Follow the format of `penn_state.json`
3. Include colors, chant patterns, fight song notes, and audio tones
4. Update configuration to reference the new college file

## 🤝 Contributing

ILLO is an open-source project welcoming contributions:

1. **Hardware**: Design improvements, enclosure modifications
2. **Software**: Bug fixes, new features, college integrations
3. **Content**: Additional college configurations, music recognition
4. **Documentation**: Usage guides, tutorials, troubleshooting

## 🐛 Troubleshooting

**Common Issues:**

- **No LEDs**: Check CircuitPython version and library installation
- **No audio response**: Verify microphone functionality and audio processing libraries
- **Memory errors**: Disable persistent memory or reduce college features
- **College features not working**: Check college JSON file format and college name in config
- **Bluetooth not working**: Bluetooth features are in development - libraries included for future use

## 📄 License

MIT License - see LICENSE file for details.

---

**Made with ❤️ by Charles Doebler at Feral Cat AI**

*ILLO represents the intersection of artificial intelligence, environmental sensing, and interactive art. Through
advanced light management, audio processing, and adaptive behaviors, ILLO creates a unique companion experience that
grows and evolves with its user.*