# 🛸 ILLO - Identified Little Levitating Object
## Production Release v3.0 - AI-Powered Levitating UFO Companion

**Transform any levitating UFO toy into an intelligent AI companion that learns, adapts, and evolves with you.**

ILLO is a complete, production-ready AI system that brings consciousness to levitating UFO toys through advanced
CircuitPython programming on the Adafruit Circuit Playground Bluefruit. Watch your UFO develop its own personality
while gracefully floating and responding intelligently to your environment.
**Proudly 3D printed with recycled PETG and Made in USA.**

---

## 🌟 Revolutionary Features

### 🧠 **AI Intelligence System**
- **Adaptive Learning**: Develops personality traits through repeated interactions
- **Relationship Building**: Trust and bonds strengthen with continued play
- **Autonomous Behaviors**: Seeks attention when ignored, celebrates interaction
- **Persistent Memory**: Saves preferences when filesystem is writeable
- **Environmental Awareness**: Reacts to ambient light changes
- **Mood Management**: Different emotional states create unique light patterns

### 🌙 **Smart Environmental Sensing**
- **Adaptive Brightness**: Automatically dims and brightens based on room light
- **Light Interaction Detection**: Waves, shadows, and movement affect behavior
- **Night Light Mode**: Calming, low-level illumination
- **Battery Conservation**: Smart dimming extends runtime
- **Ambient Tracking**: Uses history of light readings for smooth adaptation

### 🎵 **Music & College System**
- **Audio Reactivity**: FFT-powered microphone input for real-time beat detection
- **College Fight Song**: Celebrates Penn State songs/colors
- **College Chant**: Chants and responds with team spirit displays
- **Tempo Matching**: Light pulses synchronized to BPM
- **Expandable Colleges**: Drop JSON files into /colleges/ to add more teams (Penn State included by default)

### ♻️ **Sustainable & Made in USA**
- **Recycled PETG**: 3D printed enclosure
- **Domestic Manufacturing**: Built in USA
- **Energy Efficient**: Optimized code for long battery life
- **Open Source**: Extend, remix, improve

---

## 🚀 Four Complete Operating Modes

### **1. UFO Intelligence 🧠** *(Default)*
AI-driven behaviors that adapt to you:
- Investigates sounds while hovering
- Builds personality traits and quirks
- Responds to tap, shake, light interactions, and ambient sounds
- Tracks interaction history for “trust” scoring
- College chant and spirit responses

### **2. Intergalactic Cruising 🌌**
Classic sci-fi mode:
- Elegant rotating light trails with auto-brightness
- Audio-reactive ambient glow
- Perfect night light behavior
- Light-based interactions off; brightness only
- Bluetooth control availble (see below)

### **3. Meditate 🧘**
Relaxation mode:
- Breathing patterns: 4-7-8, Box, Triangle, Deep Relaxation
- Adaptive timing from light conditions
- Ultra-low brightness for calm spaces
- Breathing lights only — no tap/shake/light interactions

### **4. Dance Party 🕺**
Music visualization mode:
- Real-time FFT analysis for beat sync
- Dynamic light shows matched to tempo
- College color overlays when triggered
- Brightness control only (tap/shake/light disabled in v3.0)
- Multi-UFO Bluetooth Sync: ILLOs near each other automatically discover peers and synchronize beat pulses and scene changes using lightweight BLE messages—no phone app required. One ILLO assumes the leader role; others follow. Leadership can transfer seamlessly if the leader leaves.

---

## 🔧 Hardware Integration
- **Board**: Adafruit Circuit Playground Bluefruit (nRF52840)
- **Firmware**: CircuitPython 9.0.4 with ulab (download CPB UF2 that includes ulab)
- **Sensors**: Onboard mic, accelerometer, light sensor, slide switch, buttons
- **Outputs**: Onboard NeoPixels + BLE UART

---

## 🕹️ Controls
- **Button A**: Cycles routines (1–4), saves to config, and soft-resets
- **Button B**: Context-aware
  - Meditate → cycles breathing patterns
  - Other modes → cycles color modes
- **Slide Switch**:
  - Controls volume behavior
  - Chooses filesystem mode (see below)

---

### 📱 Bluetooth (Intergalactic Cruising only)
- **App**: Adafruit Bluefruit Connect (UART)
- **Device Name**: ILLO_x
- **Advertising**: 120 s on boot, re-advertises every 300 s
- **Controls**: Override mode, brightness, and colors

---

### 💾 Persistence & Filesystem Modes

| Scenario | Filesystem | Behavior |
|----------|------------|----------|
| Standalone (no USB) | Read/Write | Preferences saved |
| USB + Slide ON | Read/Write | "Testing mode" |
| USB + Slide OFF | Read-Only | Safe demo mode; no saves |

---

## 📦 Installation
1. Flash CircuitPython 9.0.4 with ulab onto your Circuit Playground Bluefruit.
2. Copy `code.py`, `boot.py`, `config.json`, and `colleges/` to CIRCUITPY.
3. Install required libraries from the Adafruit Bundle:
   ```
   lib/
   ├── adafruit_circuitplayground/
   └── adafruit_ble/
   ```
4. Safely eject, power cycle, and watch ILLO come alive.

---

## 🎓 Colleges
- Built-in: Penn State
- Add more: Place a JSON file into `colleges/` following the schema