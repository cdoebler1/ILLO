# 🛸 ILLO - AI-Powered UFO Controller

An intelligent UFO lighting system powered by CircuitPython and machine
learning, designed for the Adafruit Circuit Playground Bluefruit.

## 🌟 Features

- **🧠 AI Intelligence**: Advanced machine learning system that develops
  personality and learns from interactions
- **🎵 Audio Reactive**: Real-time sound analysis and beat detection for
  music synchronization
- **📱 Bluetooth (optional)**: Libraries included; current release runs
  standalone (BLE sync disabled for memory safety)
- **🎨 Dynamic Lighting**: 10 RGB NeoPixel LEDs with 4 routines and 3
  color themes
- **🤝 Interactive**: Responds to taps, shakes, and environmental sounds
- **💾 Persistent Memory (configurable)**: Optional long-term memory to save
  AI personality between sessions

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
- **Features**: Bluetooth, NeoPixels, Accelerometer, Microphone, Buttons,
  Switch

## 📦 Installation

1. **Install CircuitPython** on your Circuit Playground Bluefruit using the
   firmware files in the `firmware/` directory
2. **Copy all files** (except `firmware/` directory) to the CIRCUITPY drive
3. **Install required libraries** from the Adafruit Bundle to the `lib/`
   folder:
   - adafruit_circuitplayground
   - neopixel
   - adafruit_ble
   - adafruit_bluefruit_connect
   - simpleio

4. **Reset the board** the UFO will start in AI Intelligence mode

## 🎮 Controls

- **Button A**: Cycle through routines (1–4)
- **Button B**: Cycle through color modes (1–3)
- **Switch**: Controls volume (On=1, Off=0)
- **Shake**: Trigger turbulence effects and energy boosts
- **Tap**: Interact with AI and build trust

##