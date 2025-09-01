
ILLO Bluetooth Control Guide
Intergalactic Cruising with Bluefruit Connect

Congratulations on making your first Bluetooth connection! Your ILLO UFO now 
supports wireless control through the Adafruit Bluefruit Connect app.

================================================================================
APP SETUP
================================================================================

Download Bluefruit Connect:
- iOS: App Store - Bluefruit Connect
- Android: Google Play - Bluefruit Connect

First Connection:
1. Switch to Intergalactic Cruising (Routine 2) using Button A on your Circuit 
   Playground Bluefruit
2. Power on your ILLO UFO - it will automatically start advertising as 
   "UFO" (or your configured device name)
3. Open Bluefruit Connect on your phone
4. Tap "Connect" and look for "UFO" in the device list
5. Connect within 2 minutes of powering on (advertising timeout)

TIP: Once paired, you can reconnect anytime even without active advertising!

================================================================================
CONTROL INTERFACES
================================================================================

1. Control Pad - Quick Actions
-------------------------------

The Control Pad provides instant access to color modes and effects:

**Numbered Buttons (1-4) - Color Modes:**
Button 1        | Rainbow Wheel     | Full spectrum color cycling
Button 2        | Pink Nebula       | Cosmic pink and magenta themes
Button 3        | Deep Space Blue   | Rich blue cosmic variations
Button 4        | Forest Canopy     | Natural green color palette

**Arrow Buttons - Settings:**
Up Arrow        | Speed Boost       | Increase rotation speed
Down Arrow      | Speed Reduce      | Decrease rotation speed  
Left Arrow      | Gentle Mode       | Softer effects and transitions
Right Arrow     | Enhanced Mode     | Intense effects and persistence

**Special Functions:**
Center          | Manual Beat       | Trigger instant beat sync for music
Reset Button    | Audio Mode        | Return to audio-reactive mode

2. Color Picker - Custom Colors
--------------------------------

Create your own color schemes:
- Tap the Color Picker in Bluefruit Connect
- Select any color from the wheel
- Your UFO instantly switches to that custom color
- Works with intensity: Brighter audio = brighter custom color

3. UART Terminal - Advanced Commands
-------------------------------------

For power users, type commands directly:

Basic Commands:
/help                    - Show all available commands
/status                  - Display current settings
/beat                    - Manual beat trigger

Color Mode Commands:
/mode 1                  - Switch to Rainbow Wheel
/mode 2                  - Switch to Pink Nebula
/mode 3                  - Switch to Deep Space Blue
/mode 4                  - Switch to Forest Canopy

Performance Tuning:
/speed 0.5               - Slow rotation (0.1x - 3.0x)
/speed 1.5               - Fast rotation
/brightness 50           - Set brightness to 50%
/brightness 100          - Maximum brightness

Example Session:
> /speed 2.0
Rotation speed: 2.0x

> /brightness 75
Brightness: 75%

> /mode 2
Mode: Pink Nebula

> /status
Current Settings:
Mode Override: 4
Speed: 2.0x
Brightness: 75%
Effect: normal

================================================================================
COLOR MODE DETAILS
================================================================================

1. Rainbow Wheel
- Full spectrum color cycling
- Smooth transitions through all hues
- Classic rainbow effect with dynamic intensity

2. Pink Nebula  
- Cosmic pink and magenta themes
- Deep space nebula-inspired colors
- Rich purples, magentas, and hot pinks

3. Deep Space Blue
- Rich blue cosmic variations
- From light cyan to deep navy
- Evokes the depths of space

4. Forest Canopy
- Natural green color palette
- From bright lime to deep forest green
- Earth-inspired organic tones

================================================================================
MUSIC INTEGRATION
================================================================================

Audio Sync Methods:

1. Ambient Audio (Default):
- UFO uses its built-in microphone
- Play music from any source (phone speaker, stereo, etc.)
- UFO automatically reacts to ambient sound

2. Manual Beat Sync:
- Use Control Pad Center button or /beat command
- Perfect for syncing to silent music or creating your own rhythm
- Great for video recording with controlled lighting

3. Motion Sync (Future Feature):
- Accelerometer data could trigger beats
- Dance movements = light reactions

================================================================================
EFFECT MODES
================================================================================

Normal Mode (Default):
- Balanced intensity and fade
- Good for most music genres

Enhanced Mode (Right Arrow):
- More intense colors and effects
- Slower fade for persistence
- Perfect for electronic/dance music

Gentle Mode (Left Arrow):
- Softer colors and transitions  
- Faster fade for subtle effects
- Great for ambient/classical music

================================================================================
PERSISTENT SETTINGS
================================================================================

Your color mode selections are automatically saved and will persist:
- Across power cycles
- When switching between routines
- Until manually changed

This means once you select "Pink Nebula", your UFO will remember and use 
that color scheme even after restart!

Speed and effect settings are session-only and reset on restart.

================================================================================
CONNECTION MANAGEMENT
================================================================================

Connection Status:
- Green Status: Connected and receiving commands
- Advertising: Looking for connections (2 minutes)
- Standby: Can accept reconnections

Reconnection:
- Previously paired devices can reconnect anytime
- No need to wait for advertising
- Connection history stored in Bluefruit Connect

Troubleshooting:
- Can't connect? Wait for "Advertising..." message
- Lost connection? UFO will auto-restart advertising after 5 minutes
- Commands not working? Check UART Terminal for responses

================================================================================
CREATIVE USAGE IDEAS
================================================================================

Performance Mode:
1. Set custom colors with Color Picker
2. Use manual beat triggers for precise timing
3. Adjust speed and brightness for the scene

Party Mode:
1. Enhanced effects for maximum impact
2. High speed rotation (2.0x - 3.0x)
3. Let audio-reactive mode respond to music

Ambient Mode:
1. Gentle effects (Left arrow) for background ambiance
2. Deep Space Blue or Forest Canopy for calming colors
3. Speed reduction (Down arrow) for relaxed movement

Video Production:
1. Manual beat control for consistent lighting
2. Custom colors to match your aesthetic
3. Precise timing control via UART commands

================================================================================
QUICK REFERENCE CARD
================================================================================

**Color Modes:**
- Button 1: Rainbow Wheel
- Button 2: Pink Nebula  
- Button 3: Deep Space Blue
- Button 4: Forest Canopy

**Speed Control:**
- Up Arrow: Faster rotation
- Down Arrow: Slower rotation

**Effects:**
- Right Arrow: Enhanced mode
- Left Arrow: Gentle mode
- Reset: Return to audio-reactive

**Special:**
- Center: Manual beat trigger
- Color Picker: Custom colors
- Terminal: /help for commands

Connection: Look for "UFO" in Bluefruit Connect
Timeout: 2 minutes initial, auto-readvertise every 5 minutes

================================================================================
WHAT'S NEXT?
================================================================================

Your ILLO UFO now supports advanced Bluetooth control! Try experimenting with:
- Different color modes with various music genres
- Speed adjustments for different energy levels
- Custom color combinations for specific moods
- Manual beat sync for creative video projects

The numbered buttons (1-4) give you instant access to the four signature 
color themes, while the arrows let you fine-tune the experience. Your 
selections are automatically saved, so your UFO remembers your preferences!

Enjoy your wirelessly controlled intergalactic cruising experience!

================================================================================
Technical Notes:

- Device Name: UFO (or your configured name from config.json)
- Bluetooth LE Protocol: Uses Adafruit Bluefruit Connect protocol
- Advertising Timeout: 2 minutes initial, 5 minute intervals for re-advertising
- Commands: Control Pad (!B), Color Picker (!C), UART Terminal (/)
- Persistent Storage: Color modes saved to config.json automatically
- Memory Optimized: Uses lazy imports to conserve CircuitPython memory
- Compatible: iOS and Android via Bluefruit Connect app
