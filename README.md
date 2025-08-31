# 🛸 ILLO - Identified Little Levitating Object

Meet ILLO, your AI-powered UFO companion that reacts to your world and evolves with you.
ILLO listens, learns, and lights the surrounding space with mesmerizing animations that sync to music,
respond to touch, and adapt to your environment.

## 🌟 Key Features

- **🧠 AI Intelligence**: Advanced learning system that develops unique personality traits over time
- **🎵 Music & Chant Detection**: Real-time audio analysis with synchronized lighting effects
- **🏫 College Spirit**: Recognizes fight songs and chants with team color displays
- **💾 Persistent Memory**: Remembers personality, moods, and preferences across power cycles
- **🎨 Dynamic Lighting**: 10 RGB NeoPixels with synchronized light shows
- **🤝 Interactive**: Responds to touch, shake, environmental sounds, and user interactions
- **📱 Bluetooth Ready**: Libraries included for future sync capabilities (currently standalone)

## 🚀 Operating Modes

### 1. AI Intelligence 🧠 *(Default)*
- Autonomous AI behaviors that adapt to your interactions
- Environmental response and learning algorithms  
- Develops unique personality over time
- Memory management with behavioral evolution
- Attention-seeking and mood-based responses

### 2. Intergalactic Cruising 🌌
- Smooth ambient lighting patterns
- Low-energy color transitions
- Sci-fi inspired visual effects
- Perfect for background ambiance

### 3. Meditate 🧘
- Calming breathing-pattern animations
- Soft color gradients for relaxation
- Mindfulness-focused lighting sequences
- Stress-relief visual therapy

### 4. Dance Party 🕺
- Advanced beat detection and music synchronization
- Dynamic light shows that pulse with the beat
- Music-reactive color patterns
- Party-energy visual displays

## 🎵 Music System

ILLO features a sophisticated music player that handles:

- **Chants**: Short, repetitive team chants (played 3 times)
- **Fight Songs**: Full college fight songs (single play)
- **General Music**: Any audio with synchronized lighting
- **College Colors**: Automatic team color display during collegiate music
- **Tempo Matching**: Precise BPM synchronization with 16th note accuracy

## 🔧 Hardware Requirements

- **Board**: Adafruit Circuit Playground Bluefruit
- **CircuitPython**: Version 7.0.0 or higher
- **Memory**: 2MB Flash, 256KB RAM minimum
- **Components**: 
  - 10x NeoPixel RGB LEDs
  - Built-in accelerometer & microphone
  - 2x tactile buttons + slide switch
  - Bluetooth radio (BLE)

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
   ```
4. **Reset the board** - ILLO will start in AI Intelligence mode

### Boot Configuration
The slide switch controls storage mode during boot:
- **Development: Switch right + USB**: Sound off, read from local, read/write over USB
- **Testing: Switch left + USB**: Sound on, read/write from local, read over USB
- **Operation: Switch right**: Sound off, read/write from local
- **Operation: Switch left**: Sound on, read/write from local

## 🎮 Controls
- **Button A**: Cycle through operating modes (1–4)
- **Button B**: Cycle through color themes (1–4)
- **Slide Switch**: Sound on/off. Boot-time storage configuration
- **Touch/Tap**: Interact with the AI system and trigger responses
- **Shake**: Generate turbulence effects and energy responses

## 📁 Project Structure