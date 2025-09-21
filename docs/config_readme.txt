ILLO Configuration Settings
===========================

config.json field descriptions:

name (string): Device identifier for Bluetooth and logging
  - Used for BLE advertising and device identification
  - Default: "UFO" 
  - Useful when running multiple ILLO devices for identification

college_spirit_enabled (boolean): Enable college team integration
  true = Activates fight song recognition and team color displays (default)
  false = Disables college-specific features
  
college (string): Selected college/team for spirit features
  - Default: "penn_state"
  - Available teams stored in colleges/ directory
  - Used for fight song recognition and team color schemes

college_chant_detection_enabled (boolean): Enable real-time chant detection
  true = Listens for crowd chants and responds with team colors
  false = Disables active chant listening (default for memory conservation)
  Note: Uses significant processing power when enabled

routine (integer 1-4): Default operating mode selection
  1 = AI Intelligence (adaptive AI behaviors; default)
  2 = Intergalactic Cruising (ambient sci-fi lighting with light sensing)  
  3 = Meditate (calming breathing patterns)
  4 = Dance Party (music-reactive light shows)

mode (integer 1-4): Default color theme selection
  1 = Rainbow spectrum colors (default)
  2 = Pink color variations
  3 = Blue color variations  
  4 = College team colors (when college_spirit_enabled = true)

volume (integer 0-1): Default sound setting
  0 = Silent mode (lights only; default)
  1 = Sound enabled (lights + audio tones)
  Note: Physical slide switch overrides this setting during operation

ufo_persistent_memory (boolean): Enable AI memory persistence between power cycles
  true = Saves AI personality, preferences, and learning to storage (default)
  false = Resets AI memory on each power cycle
  Note: Affects flash memory write cycles; AI still learns during active sessions

debug_bluetooth (boolean): Enable/disable Bluetooth debug logging
  true = Show BLE connection, scanning, and sync details in console
  false = Hide Bluetooth debug messages (default)
  Note: Bluetooth sync currently disabled for memory optimization

debug_audio (boolean): Enable/disable audio processing debug logging
  true = Show beat detection, music analysis, and audio energy levels
  false = Hide audio processing debug messages (default)

Hardware Controls:
- Button A: cycles routines (1–4), saves to config, and soft-resets for a clean start
- Button B: context-aware — Meditate: cycles breathing patterns; other modes: cycles color modes
- Slide Switch: Sound on/off control + boot-time storage configuration
- Touch/Tap: Interact with AI system and trigger responses (disabled in Meditate)
- Shake: Generate turbulence effects and energy boosts (disabled in Meditate)
- Light Changes: Wave hand over or approach ILLO for interaction responses (disabled in Meditate)

Boot-Time Switch Behavior:
- Switch LEFT + USB: Sound on, testing mode (read/write storage via USB)
- Switch RIGHT + USB: Sound off, development mode (read-only via USB) 
- Switch LEFT (no USB): Sound on, standalone operation
- Switch RIGHT (no USB): Sound off, standalone operation

Smart Environmental Features:
- Automatic brightness adjustment based on ambient light conditions
- Light-based interaction detection for non-contact user responses
- Night light mode in Intergalactic Cruising (sound off) with room dimming
- Environmental awareness through continuous light sensor monitoring
- Battery conservation through intelligent brightness scaling

Music System Features:
- Automatic tempo detection and BPM synchronization
- College fight song and chant recognition
- Real-time beat-synchronized lighting effects
- Support for 16th note precision timing
- Team color displays during collegiate music

AI System Features:
- Persistent personality development over time
- Environmental response and adaptation including light changes
- Interactive learning from user behaviors (touch, shake, light)
- Memory management with configurable persistence
- Autonomous attention-seeking behaviors

Memory Management:
- Optimized for CircuitPython's 256KB RAM limitation
- Automatic garbage collection during operation
- Configurable memory persistence to reduce flash wear
- Safe fallback modes when memory limits are reached
- Memory-efficient data structures throughout system

College Integration:
- Expandable team database in colleges/ directory
- Automatic fight song detection and response
- Team-specific color schemes and patterns
- Crowd chant pattern recognition (when enabled)
- Customizable team preferences and loyalty tracking

Performance Notes:
- AI learning occurs in RAM during active sessions
- Persistent memory saves occur at safe intervals
- Audio processing optimized for real-time performance
- Light synchronization maintains smooth 60fps target
- Bluetooth features disabled by default for memory conservation
- Light sensor monitoring adds minimal processing overhead

### **Adaptive Brightness Levels - Automatic**
- **Very Dark (< 30)**: 2% brightness - perfect nightlight
- **Dark (30-59)**: 5% brightness - comfortable low-light
- **Indoor (60-99)**: 10% brightness - normal indoor lighting
- **Bright Indoor (100-149)**: 15% brightness - well-lit rooms
- **Very Bright (150-199)**: 20% brightness - bright room visibility
- **Daylight (200+)**: 25% brightness - maximum outdoor conditions

### **Meditation Breathing Patterns - Complete**
1. **4-7-8 Breathing**: 4.8s inhale, 2.4s hold, 4.8s exhale (default)
2. **Box Breathing**: 4s inhale, 4s hold, 4s exhale, 4s hold
3. **Triangle Breathing**: 4s inhale, 4s hold, 4s exhale
4. **Deep Relaxation**: 6s inhale, 2s hold, 8s exhale

---

## 🏫 College Integration - Expandable System

### **Penn State Implementation - Complete**
- **Fight Songs**: "Fight On State" with authentic musical notes
- **Team Colors**: Blue and white color schemes
- **Chant Recognition**: "We Are Penn State" and other crowd chants
- **Spirit Tracking**: AI develops team loyalty over time
- **Random Pride**: Spontaneous team color displays

### **Expandable Architecture**
- **JSON Configuration**: Easy addition of new colleges
- **Color Schemes**: Team-specific color palettes
- **Music Recognition**: Fight song and chant patterns
- **Audio Integration**: Team-specific tones and musical sequences
- **Spirit Features**: Loyalty tracking and celebration behaviors

### **Adding New Colleges**
1. Create JSON file in `colleges/` directory
2. Define team colors, fight songs, and chant patterns
3. Include audio tones and musical note sequences
4. Update config.json to reference new college
5. System automatically loads and integrates new team

---

## 🏗️ Production Architecture - Modular & Scalable

### **Core Systems - Complete**
- **InteractionManager**: Centralized interaction detection and routing
- **LightManager**: Ambient light sensing and adaptive brightness control
- **HardwareManager**: Low-level hardware abstraction layer
- **AudioProcessor**: Real-time FFT analysis and beat detection
- **ConfigManager**: Persistent configuration and settings management
- **MemoryManager**: Optimized for 256KB RAM with garbage collection

### **AI Components - Production Complete**
- **UFOAICore**: Decision making, mood management, personality development
- **UFOLearningSystem**: Environmental learning and interaction history
- **UFOMemoryManager**: Persistent memory with flash wear protection
- **UFOAIBehaviors**: Behavior pattern execution and visual responses
- **PhysicalActions**: Touch, shake, and motion response systems

### **College & Music Systems - Complete**
- **UFOCollegeSystem**: College spirit management and celebration control
- **CollegeManager**: Dynamic college data loading and color schemes
- **ChantDetector**: Real-time audio pattern recognition for team chants
- **MusicPlayer**: Unified music playback with synchronized lighting
- **ColorUtils**: Advanced color manipulation and theme management

### **Memory Optimization - Production Tuned**
- **256KB RAM Optimized**: Specifically tuned for Circuit Playground constraints
- **Garbage Collection**: Automatic memory management during operation
- **Flash Wear Protection**: Configurable persistence reduces write cycles
- **Safe Fallback**: Graceful degradation when memory limits approached
- **Real-time Performance**: Maintains 60fps target for smooth lighting

---

## 📁 Complete Project Structure

Meditation Configuration:
meditate_breath_pattern (integer 1-4): Selected breathing technique
  1 = 4-7-8 Breathing (4.8s inhale, 2.4s hold, 4.8s exhale; default)
  2 = Box Breathing (4s inhale, 4s hold, 4s exhale, 4s hold)
  3 = Triangle Breathing (4s inhale, 4s hold, 4s exhale)
  4 = Deep Relaxation (6s inhale, 2s hold, 8s exhale)
  Note: Button B cycles through patterns when in Meditation mode

meditate_adaptive_timing (boolean): Enable light-sensor adaptive timing
  true = Breathing speed adjusts to ambient light conditions (default)
  false = Fixed timing regardless of lighting

meditate_ultra_dim (boolean): Enable ultra-low brightness mode
  true = Meditation uses very dim LEDs for minimal distraction (default)
  false = Normal brightness levels

Environmental & Manufacturing:
- Enclosure 3D printed from recycled PETG plastic
- Made in USA with domestic components where possible
- Energy-efficient algorithms for extended battery life
- Sustainable design practices throughout development
- Open source to extend product lifecycle and reduce e-waste