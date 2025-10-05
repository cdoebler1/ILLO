# ILLO: Intelligent Levitating Light Object

ILLO is an AI-powered, levitating UFO companion.  
It combines the physical magic of magnetic levitation with stateful behaviors, adaptive responses, and wireless control.  
Built on the Adafruit Circuit Playground Bluefruit (CPB, nRF52840) running CircuitPython, ILLO is open, hackable, and ready for classrooms, makerspaces, and curious tinkerers.

---

## Hardware & Firmware

- **Board:** Adafruit Circuit Playground Bluefruit (nRF52840)  
- **Firmware:** CircuitPython **9.0.4** (2024-04-16)  
- **Libraries:** Adafruit CircuitPython Bundle (pin exact release date in setup instructions)  
- **Enclosure:** 3D-printed PETG (with optional diffuser)  
- **Power:** USB or LiPo battery pack  
- **Levitation Base:** Standard commercial UFO levitation platform  

---

## Quickstart

1. Flash CircuitPython 9.0.4 (nRF52840 build with `ulab`).  
2. Copy the ILLO project files to `CIRCUITPY`.  
3. Copy required libraries:  
   - `adafruit_circuitplayground/`  
   - `adafruit_ble/`  
4. Eject and reset the board.  
5. On first boot, LEDs flash a startup pattern.  
6. If Bluetooth is enabled, ILLO advertises under its configured name for 2 minutes.  

---

## Routines (High-Level Personality States)

ILLO runs in **Routines**, the big states that define how it behaves.  
By default, ILLO boots into **Routine 1 (UFO Intelligence)**.  

| Routine (int) | Name                   | Description                                                                 |
|---------------|------------------------|-----------------------------------------------------------------------------|
| `1`           | UFO Intelligence       | Default personality loop: sensors (mic, accel, light), evolving behaviors.  |
| `2`           | Intergalactic Cruising | Bluetooth control via Bluefruit Connect app.                                |
| `3`           | Meditate               | Guided breathing with selectable/adaptive patterns.                         |
| `4`           | Dance Party            | Multi-UFO sync: leader election, beat-reactive light show.                  |

**Selecting Routines:**  
- **Button A**: cycles routines.  
- **config.json**: set `routine` value to boot into a specific one.  

---

## Modes (Sub-Styles Within Routines)

Each Routine has its own **Modes**, which define its style or variation.  

### Routine 2: Intergalactic Cruising — Color Modes

| Mode | Name            | Effect                                   |
|------|-----------------|------------------------------------------|
| `1`  | Rainbow Wheel   | Full spectrum cycling                    |
| `2`  | Pink Nebula     | Magenta/purple cosmic theme              |
| `3`  | Deep Space Blue | Cyan → navy space theme                  |
| `4`  | Forest Canopy   | Green organic palette                    |

### Routine 3: Meditate — Breathing Modes

| Mode | Pattern            | Timing (inhale / hold / exhale) |
|------|--------------------|---------------------------------|
| `1`  | Box Breathing      | 4 – 4 – 4 – 4                   |
| `2`  | 4-7-8 Breathing    | 4 – 7 – 8                       |
| `3`  | Resonant Breathing | Smooth ~5.5 breaths/min         |

### Routine 4: Dance Party — Sync & Performance Modes

- Base mode = audio-reactive FFT.  
- BLE overrides still apply (color, brightness).  
- Sync Manager handles leader/follower roles automatically.  

---

## Bluetooth (Routine 2 Only)

ILLO integrates with the **Adafruit Bluefruit Connect app** (iOS/Android).  

### Advertising
- Duration: 2 minutes on boot.  
- Re-advertises every 5 minutes if idle.  
- Once paired, reconnections work instantly.  

### Control Interfaces
- **Control Pad**  
  - Buttons 1–4: Rainbow Wheel, Pink Nebula, Deep Space Blue, Forest Canopy  
  - Arrows: Speed ↑/↓, Gentle (←), Enhanced (→)  
  - Center: Manual beat trigger  
  - Reset: Return to audio-reactive mode  
- **Color Picker:** Set any custom color instantly.  
- **UART Terminal:** Direct commands  

  ```
  /help
  /status
  /beat
  /mode 1..4
  /speed <0.1–3.0>
  /brightness <0–100>
  ```

### Persistence
- Color mode persists across power cycles.  
- Speed and effects reset each boot.  

---

## Configuration (`config.json`)

ILLO is runtime-configurable via JSON.  

### Example (copy into `config.json`)

```json
{
  "routine": 1,
  "mode": 1,
  "name": "ILLO_1",
  "college": "penn_state",
  "college_spirit_enabled": true,
  "college_chant_detection_enabled": false,
  "ufo_persistent_memory": true,
  "bluetooth_enabled": true,
  "meditate_breath_pattern": 1,
  "meditate_adaptive_timing": true,
  "meditate_ultra_dim": true,
  "is_leader": true
}
```

### Config Fields

| Key                               | Type   | Default     | Purpose                                                                 |
|----------------------------------|--------|-------------|-------------------------------------------------------------------------|
| `routine`                         | int    | `1`         | Startup routine preset.                                                 |
| `mode`                            | int    | `1`         | Sub-mode for active routine.                                            |
| `name`                            | str    | `"ILLO_1"`  | BLE device name.                                                        |
| `college`                         | str    | `"penn_state"` | Loads theme from `/colleges`.                                         |
| `college_spirit_enabled`          | bool   | `true`      | Enable college theme colors.                                            |
| `college_chant_detection_enabled` | bool   | `false`     | Enable chant detection audio trigger.                                   |
| `ufo_persistent_memory`           | bool   | `true`      | Save preferences to flash when writable.                                |
| `bluetooth_enabled`               | bool   | `true`      | Enable BLE advertising and control.                                     |
| `meditate_breath_pattern`         | int    | `1`         | Selects breathing pattern.                                              |
| `meditate_adaptive_timing`        | bool   | `true`      | Auto-adjust breathing timing.                                           |
| `meditate_ultra_dim`              | bool   | `true`      | Low brightness for dark rooms.                                          |
| `is_leader`                       | bool   | `true`      | Preferred leader flag for sync election.                                |

---

## College Spirit System

College themes live in `/colleges/*.json`.  

### Example: `penn_state.json` (documentation example)

```json
{
  "name": "Penn State",
  "short_name": "PSU",
  "colors": {
    "primary": [0, 50, 255],
    "secondary": [255, 255, 255]
  },
  "chants": {
    "primary": {
      "pattern": ["WE", "ARE", "PENN", "STATE"],
      "timing_gaps": [0.4, 0.8, 0.4],
      "frequency_range": [100, 400],
      "energy_threshold": 0.7,
      "min_energy": 400,
      "pattern_length": 3,
      "notes": [[330, 10], [0, 2], [392, 10], ...],
      "bpm": 120
    }
  },
  "fight_song": {
    "name": "Fight On State",
    "bpm": 120,
    "notes": [[294, 8], [330, 4], [370, 4], ...]
  },
  "audio_tones": {
    "chant_response": [500, 0.3],
    "victory_fanfare": [660, 0.5],
    "celebration": [440, 0.3]
  }
}
```

**Schema highlights:**  
- `colors`: RGB values.  
- `chants`: Trigger phrases, timing gaps, FFT ranges, thresholds, and optional notes.  
- `fight_song`: Note arrays + BPM.  
- `audio_tones`: Named tones with frequency and duration.  

---

## Persistence & Memory

- Preferences are saved only if `ufo_persistent_memory` is enabled *and* filesystem is writable.  
- Safe demo mode (USB connected, slide switch OFF) runs volatile to avoid flash corruption.  
- Persistent values: color mode, college, brightness.  
- Session-only values: speed, effects.  

---

## Teacher & STEM Curriculum Ideas

**Lab 1: Sensor Lab**  
- Adjust light/mic thresholds in `config.json`.  
- Observe ILLO’s reactions in UFO Intelligence routine.  

**Lab 2: BLE Lab**  
- Use `/status`, `/mode`, `/speed`, `/brightness` in UART.  
- Measure and chart reaction latency.  

**Lab 3: Chant Detection**  
- Enable `college_chant_detection_enabled`.  
- Test chants against FFT thresholds and see ILLO respond.  

---

## Safety & Privacy

- No Wi-Fi, no cloud, BLE only.  
- No data leaves the device unless user explicitly sends via UART.  
- Handle LiPo batteries safely.  
- Enclosure designed for low-heat LEDs; max brightness capped in firmware.  

---

## License

MIT License.  
Logos, chants, and school branding remain property of their respective institutions.  

