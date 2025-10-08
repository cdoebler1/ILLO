# ILLO Device Configuration Guide

## Configuration File Overview

The ILLO device uses a `config.json` file to control various settings and behaviors.
Below are detailed descriptions of each configuration field.

## Configuration Fields

### Device Identity

#### `name` (string)

- **Purpose**: Device identifier for Bluetooth and logging
- **Usage**: Used for BLE advertising and device identification
- **Default**: `"ILLO"`
- **Notes**: Useful when running multiple ILLO devices for identification

### College Spirit Features

#### `college_spirit_enabled` (boolean)

- **Purpose**: Enable college team integration
- **Options**:
    - `true`: Activates fight song recognition and team color displays (default)
    - `false`: Disables college-specific features

#### `college` (string)

- **Purpose**: Selected college/team for spirit features
- **Default**: `"penn_state"`
- **Notes**:
    - Available teams stored in `colleges/` directory
    - Used for fight song recognition and team color schemes

#### `college_chant_detection_enabled` (boolean)

- **Purpose**: Enable real-time chant detection
- **Options**:
    - `true`: Listens for crowd chants and responds with team colors
    - `false`: Disables active chant listening (default for memory conservation)
- **⚠️ Note**: Uses significant processing power when enabled

### Operating Modes

#### `routine` (integer 1-4)

- **Purpose**: Default operating mode selection
- **Options**:
    - `1`: AI Intelligence (adaptive AI behaviors; default)
    - `2`: Intergalactic Cruising (ambient sci-fi lighting with light sensing)
    - `3`: Meditate (calming breathing patterns)
    - `4`: Dance Party (music-reactive light shows)

#### `mode` (integer 1-4)

- **Purpose**: Default color theme or behavior selection
- **Options**:
    - **AI Intelligence, Intergalactic Cruising**:
        - `1`: Rainbow spectrum colors (default)
        - `2`: Pink color variations
        - `3`: Blue color variations
        - `4`: Green color variations
    - **Meditation**:
        - Controlled by `meditate_breath_pattern` (Button B cycles patterns)
    - **Dance Party**:
        - `1`: Leader mode (broadcasts to followers)
        - `2`: Follower mode (syncs to leader)
        - `3-4`: Reserved for future use

### Meditation Configuration

#### `meditate_breath_pattern` (integer 1-4)

- **Purpose**: Selected breathing technique
- **Options**:
    - `1`: 4-7-8 Breathing (4.8 s inhale, 2.4 s hold, 4.8 s exhale; default)
    - `2`: Box Breathing (4 s inhale, 4 s hold, 4 s exhale, 4 s hold)
    - `3`: Triangle Breathing (4 s inhale, 4 s hold, 4 s exhale)
    - `4`: Deep Relaxation (6 s inhale, 2 s hold, 8 s exhale)
- **Notes**: Button B cycles through patterns when in Meditation mode

#### `meditate_adaptive_timing` (boolean)

- **Purpose**: Enable light-sensor adaptive timing
- **Options**:
    - `true`: Breathing speed adjusts to ambient light conditions (default)
    - `false`: Fixed timing regardless of lighting

#### `meditate_ultra_dim` (boolean)

- **Purpose**: Enable ultra-low brightness mode
- **Options**:
    - `true`: Meditation uses very dim LEDs for minimal distraction (default)
    - `false`: Normal brightness levels

### Memory Management

#### `ufo_persistent_memory` (boolean)

- **Purpose**: Enable AI memory persistence between power cycles
- **Options**:
    - `true`: Saves AI personality, preferences, and learning to storage (default)
    - `false`: Resets AI memory on each power cycle
- **Notes**: Affects flash memory write cycles; AI still learns during active sessions

### Debug Settings

**Note**: Debug settings are now configured in `code.py` as module-level constants rather than in `config.json`. This
prevents accidental enabling of memory-intensive debug features.

#### `bluetooth_enabled` (boolean)

- **Purpose**: Enable/disable Bluetooth features
- **Options**:
    - `true`: Enables Bluetooth for Intergalactic Cruising and Dance Party sync (default)
    - `false`: Disables all Bluetooth features for improved performance
- **Notes**: Affects Intergalactic Cruising remote control and Dance Party multi-device sync

## Hardware Controls

### Physical Buttons and Switches

| Control           | Function                                                                             |
|-------------------|--------------------------------------------------------------------------------------|
| **Button A**      | Cycles routines (1–4), saves to config, and soft-resets for a clean start            |
| **Button B**      | Context-aware — Meditate: cycles breathing patterns; other modes: cycles color modes |
| **Slide Switch**  | Sound on/off control + boot-time storage configuration                               |
| **Touch/Tap**     | Interact with AI system and trigger responses (disabled in Meditate)                 |
| **Shake**         | Generate turbulence effects and energy boosts (disabled in Meditate)                 |
| **Light Changes** | Wave hand over or approach ILLO for interaction responses (disabled in Meditate)     |

### Boot-Time Switch Behavior

The slide switch position during boot determines the device's operational mode:

| Switch Position | USB Connected | Result                                                   |
|-----------------|---------------|----------------------------------------------------------|
| **LEFT**        | Yes           | Sound on, testing mode (read-only via USB)               |
| **RIGHT**       | Yes           | Sound off, development mode (read/write storage via USB) |
| **LEFT**        | No            | Sound on, standalone operation                           |
| **RIGHT**       | No            | Sound off, standalone operation                          |

## Smart Features

### Environmental Features

- **Automatic brightness adjustment** based on ambient light conditions
- **Light-based interaction detection** for non-contact user responses
- **Night light mode** in Intergalactic Cruising (sound off) with room dimming
- **Environmental awareness** through continuous light sensor monitoring
- **Battery conservation** through intelligent brightness scaling

### Adaptive Brightness Levels—Automatic

| Light Level                 | Brightness | Use Case                   |
|-----------------------------|------------|----------------------------|
| **Very Dark (< 30)**        | 2%         | Perfect nightlight         |
| **Dark (30-59)**            | 5%         | Comfortable low-light      |
| **Indoor (60-99)**          | 10%        | Normal indoor lighting     |
| **Bright Indoor (100-149)** | 15%        | Well-lit rooms             |
| **Very Bright (150-199)**   | 20%        | Bright room visibility     |
| **Daylight (200+)**         | 25%        | Maximum outdoor conditions |

### Meditation Breathing Patterns - Complete

1. **4-7-8 Breathing**: 4.8 s inhale, 2.4 s hold, 4.8 s exhale (default)
2. **Box Breathing**: 4 s inhale, 4 s hold, 4 s exhale, 4 s hold
3. **Triangle Breathing**: 4 s inhale, 4 s hold, 4 s exhale
4. **Deep Relaxation**: 6 s inhale, 2 s hold, 8 s exhale

### Music System Features

- **Automatic tempo detection** and BPM synchronization
- **College fight song and chant recognition**
- **Real-time beat-synchronized lighting effects**
- **Support for 16th note precision timing**
- **Team color displays** during collegiate music

### AI System Features

- **Persistent personality development** over time
- **Environmental response and adaptation** including light changes
- **Interactive learning** from user behaviors (touch, shake, light)
- **Memory management** with configurable persistence
- **Autonomous attention-seeking behaviors**

## 🏫 College Integration—Expandable System

### Penn State Implementation—Complete

- **Fight Songs**: "Fight On State" with authentic musical notes
- **Team Colors**: Blue and white color schemes
- **Chant Recognition**: (disabled) "We Are Penn State" and other crowd chants
- **Spirit Tracking**: AI develops team loyalty over time
- **Random Pride**: Spontaneous team color displays

### Expandable Architecture

- **JSON Configuration**: Easy addition of new colleges
- **Color Schemes**: Team-specific color palettes
- **Music Recognition**: Fight song and chant patterns
- **Audio Integration**: Team-specific tones and musical sequences
- **Spirit Features**: Loyalty tracking and celebration behaviors

### Adding New Colleges

1. Create JSON file in `colleges/` directory
2. Define team colors, fight songs, and chant patterns
3. Include audio tones and musical note sequences
4. Update config.json to reference the new college
5. System automatically loads and integrates the new team

## 🏗️ Production Architecture—Modular & Scalable

### Core Systems—Complete

- **InteractionManager**: Centralized interaction detection and routing
- **LightManager**: Ambient light sensing and adaptive brightness control
- **HardwareManager**: Low-level hardware abstraction layer
- **AudioProcessor**: Real-time FFT analysis and beat detection
- **ConfigManager**: Persistent configuration and settings management
- **MemoryManager**: Optimized for 256KB RAM with garbage collection

### AI Components—Production Complete

- **UFOAICore**: Decision making, mood management, personality development
- **UFOLearningSystem**: Environmental learning and interaction history
- **UFOMemoryManager**: Persistent memory with flash wear protection
- **UFOAIBehaviors**: Behavior pattern execution and visual responses
- **PhysicalActions**: Touch, shake, and motion response systems

### College & Music Systems—Complete

- **UFOCollegeSystem**: College spirit management and celebration control
- **CollegeManager**: Dynamic college data loading and color schemes
- **ChantDetector**: Real-time audio pattern recognition for team chants
- **MusicPlayer**: Unified music playbook with synchronized lighting
- **ColorUtils**: Advanced color manipulation and theme management

## Technical Specifications

### Memory Management

- **Optimized for CircuitPython's 256KB RAM limitation**
- **Automatic garbage collection** during operation
- **Configurable memory persistence** to reduce flash wear
- **Safe fallback modes** when memory limits are reached
- **Memory-efficient data structures** throughout the system

### Memory Optimization—Production Tuned

- **256KB RAM Optimized**: Specifically tuned for Circuit Playground constraints
- **Garbage Collection**: Automatic memory management during operation
- **Flash Wear Protection**: Configurable persistence reduces write cycles
- **Safe Fallback**: Graceful degradation when memory limits approached
- **Real-time Performance**: Maintains a 60 fps target for smooth lighting

### College Integration

- **Expandable team database** in `colleges/` directory
- **Automatic fight song detection** and response
- **Team-specific color schemes** and patterns
- **Crowd chant pattern recognition** (when enabled)
- **Customizable team preferences** and loyalty tracking

### Performance Notes

- AI learning occurs in RAM during active sessions
- Persistent memory saves occur at safe intervals
- Audio processing optimized for real-time performance
- Light synchronization maintains a smooth 60 fps target
- Bluetooth features are disabled by default for memory conservation
- Light sensor monitoring adds minimal processing overhead

## Sustainability

### Environmental & Manufacturing

- **Enclosure**: 3D printed from recycled PETG plastic
- **Made in the USA** with domestic components where possible
- **Energy-efficient algorithms** for extended battery life
- **Sustainable design practices** throughout development
- **Open source** to extend the product lifecycle and reduce e-waste
