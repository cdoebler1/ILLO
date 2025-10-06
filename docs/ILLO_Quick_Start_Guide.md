# 🛸 ILLO Quick Start Guide

**Get your AI UFO companion flying in minutes!**

---

## 📋 What You Need

- **Adafruit Circuit Playground Bluefruit** (nRF52840)
- **CircuitPython 9.0.4** ([Download CPB UF2](https://circuitpython.org/board/circuitplayground_bluefruit/))
- **USB-micro B cable** for programming
- **USB-C cable** for power
- **Computer** with file management capabilities
- **Levitating UFO base** (compatible magnetic levitation platform)
- **3D printed UFO enclosure** for integration

---

## 🕹️ ILLO Operating Routines & Controls

| Routine                        | Button A Value | Visual Indicator | Description                                     | Button B Function         | Special Features                                                      |
|--------------------------------|----------------|------------------|-------------------------------------------------|---------------------------|-----------------------------------------------------------------------|
| **🧠 AI Intelligence**         | 1 (Default)    | 1 purple         | Interactive AI companion that learns and adapts | Change colors/themes      | Touch/tap to wake AI, shake for turbulence, wave hand for interaction |
| **🌌 Intergalactic Cruising**  | 2              | 2 green          | Ambient lighting with auto-brightness           | Change colors/themes      | Bluetooth control via Adafruit Bluefruit Connect app                  |
| **🧘 Meditate**                | 3              | 3 blue           | Relaxation breathing patterns (4 techniques)    | Change breathing patterns | Interactions disabled, ultra-dim option available                     |
| **🕺 Dance Party**             | 4              | 4 orange         | Beat detection and music-reactive light shows   | Change colors/themes      | Music synchronization, enhanced with steady beat music                |

### Mode Settings for Each Routine

| Routine                       | Mode 1                                                                                                         | Mode 2                  | Mode 3                     | Mode 4                    |
|-------------------------------|----------------------------------------------------------------------------------------------------------------|-------------------------|----------------------------|---------------------------|
| **🧠 AI Intelligence**        | Rainbow wheel                                                                                                  | Pink colors             | Blue colors                | Green colors              |
| **🌌 Intergalactic Cruising** | Rainbow wheel                                                                                                  | Pink colors             | Blue colors                | Green colors              |
| **🧘 Meditate**               | 4-7-8 breathing (inhale 4, hold 7, exhale 8)                                                                   | Box breathing (4-4-4-4) | Triangle breathing (4-4-8) | Custom breathing pattern  |
| **🕺 Dance Party**            | <td colspan="4">Audio-reactive (automatic color selection based on beat intensity and frequency analysis)</td> |        

### Universal Controls

| Control                | Function                             | Works In All Routines |
|------------------------|--------------------------------------|-----------------------|
| **Button A**           | Cycle through routines (1→2→3→4→1)   | ✅ Yes                 |
| **Slide Switch LEFT**  | Sound enabled (more power usage)     | ✅ Yes                 |
| **Slide Switch RIGHT** | Sound disabled (longer battery)      | ✅ Yes                 |
| **Touch/Tap**          | Interact with AI/wake up             | 🧠 AI Mode only       |
| **Shake**              | Turbulence effects and energy bursts | 🧠 AI Mode only       |
| **Wave Hand**          | Light sensor interaction             | 🧠 AI Mode only       |

---

## ⚡ Battery & Power

### Charging

- Use a USB-C cable to charge the CR123A battery

### Power Management

- ILLO automatically adjusts brightness based on ambient light to conserve battery
- Slide switch controls sound (sound uses more power)
- AI learning and memory features are optimized for minimal power consumption
- Expected runtime: 5 hours

---

## 🚀 Installation Steps

### 1. Prepare Your Circuit Playground

1. Connect Circuit Playground Bluefruit to your computer via USB-micro B
2. **Flash CircuitPython 9.0.4 with ulab**:
    - Download the UF2 file from CircuitPython.org
    - Double-tap the reset button to enter bootloader mode
    - Drag the UF2 file to the CPLAYBOOT drive that appears
    - Wait for the device to restart

### 2. Install Required Libraries

Copy these libraries from the [Adafruit CircuitPython Bundle](https://circuitpython.org/libraries) to `CIRCUITPY/lib/`:

### 3. Install ILLO Software

1. Download all ILLO `.py` files from the repository
2. Copy **all Python files** to the root of `CIRCUITPY`
3. Copy `config.json` to `CIRCUITPY`
4. Copy the entire `colleges/` folder to `CIRCUITPY`
5. Safely eject and disconnect USB

### 4. First Boot

1. **Set the slide switch** to your preferred position:
    - **LEFT** = Sound enabled
    - **RIGHT** = Sound disabled (longer battery life)
2. **Power on** - ILLO will start in AI Intelligence mode (rainbow colors)
3. **Watch for the startup light sequence** - indicates successful boot

---

## 🎓 College Spirit Features

### Built-in Penn State Support

- College team colors available in color mode 4
- Team-specific color schemes and patterns
- College pride displays when manually triggered

### Adding Your Team

1. Create a JSON file in the `colleges/` folder
2. Define your team's colors and visual themes
3. Update `college` field in `config.json`
4. ILLO will automatically load your team's color schemes

### ⚠️ Important: Chant Detection

**DO NOT enable `college_chant_detection_enabled`** - this feature is disabled by default due to memory limitations.
Enabling it may cause system instability or crashes.

---

## 📱 Bluetooth Control (Intergalactic Cruising Only)

### Setup

1. Switch to **Intergalactic Cruising mode** (Button A until mode 2)
2. Open **Adafruit Bluefruit Connect** app on your phone
3. Look for device named **ILLO_x** (where x is your device name)
4. Connect via **UART** feature

### Commands

Send text commands via UART to control ILLO remotely:

- Override brightness and color settings
- Change lighting patterns
- Sync multiple ILLOs together

---

## ⚙️ First-Time Configuration

### Essential Settings (config.json)

Open `config.json` on your computer to customize:

"name": "ILLO_1", // Change to personalize your ILLO
"routine": 1, // Default mode (1-4)
"mode": 1, // Default color mode (1-4)
"bluetooth_enabled": true, // Enable Bluetooth (Intergalactic Cruising mode)
"college_spirit_enabled": true, // Enable team colors (Penn State only)
"college": "penn_state", // Your team (for colors only)
"volume": 0, // 0=silent, 1=sound
"ufo_persistent_memory": true, // AI learns and remembers
"meditate_breath_pattern": 1,
"meditate_adaptive_timing": true,
"meditate_ultra_dim": true,
"is_leader": true, // Set to true for multi-ILLO sync
"college_chant_detection_enabled": false // KEEP THIS FALSE - memory intensive

```
### Memory & Storage Modes
**USB Connection Behavior:**
- : Testing mode (read-only protection) **Slide LEFT + USB**
- : Development mode (read/write access) **Slide RIGHT + USB**
- **No USB**: Full read/write operation with AI memory saving

## 🔧 Troubleshooting
### ILLO Won't Start
- ✅ Check CircuitPython 9.0.4 with ulab is installed
- ✅ Verify all required libraries are in folder `lib/`
- ✅ Ensure all files are in the root directory `.py`
- ✅ Check that has valid JSON syntax `config.json`

### No Lights/Dim Lights
- 💡 ILLO auto-adjusts brightness - try different lighting conditions
- 💡 Check battery level if using battery power
- 💡 Wave hand over device to trigger interaction
- 💡 Try pressing Button B to cycle color modes

### AI Not Responding
- 🤖 Tap the center of the Circuit Playground to wake AI
- 🤖 Shake gently to trigger turbulence response
- 🤖 Check that you're not in Meditate mode (interactions disabled)
- 🤖 Ensure is enabled in config `ufo_persistent_memory`

### Memory Issues
- 🧠 Ensure is set to `false` `college_chant_detection_enabled`
- 🧠 Set debug options to `false` to free up memory
- 🧠 Reset device if behavior becomes erratic

### System Crashes/Instability
- ⚠️ **Most common cause**: set to `true` `college_chant_detection_enabled`
- ⚠️ Verify this setting is `false` in `config.json`
- ⚠️ Power cycle device after making config changes

## 📚 Next Steps
- **Full Configuration**: See for complete settings `ILLO_Device_Configuration_Guide.md`
- **Bluetooth Guide**: Check for advanced BLE features `ILLO_Bluetooth_Control_Guide.md`
- **Add Your College**: Create custom team color files in the directory `colleges/`
- **Experiment**: Try different combinations of modes, colors, and interactions

## 🌟 Pro Tips
- **Night Light**: Use Intergalactic Cruising mode with sound off for perfect ambient lighting
- **Meditation**: Try the 4-7-8 breathing pattern for stress relief
- **Music Fun**: Dance Party mode works best with steady beat music
- : Multiple ILLOs can sync their light shows via Bluetooth **Multi-ILLO**
- **Battery Life**: Sound-off modes significantly extend operating time
- **Memory Conservation**: Keep all audio detection features disabled for best performance

**Welcome to the ILLO family! Your AI UFO companion is ready to learn, adapt, and become your unique levitating friend.**