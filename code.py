# Charles Doebler at Feral Cat AI

# Button A cycles through routines (1-4)
# Button B cycles through color modes (1-3) 
# Switch position controls volume (True/False)
# NeoPixel ring represents UFO lighting effects
# Microphone input creates reactive light patterns
# Accelerometer shake detection for "turbulence" effects

import time
import json
from adafruit_circuitplayground import cp
from intergalactic_cruising import IntergalacticCruising
from physical_actions import PhysicalActions
from dance_party import DanceParty
from meditate import Meditate
from ufo_intelligence import UFOIntelligence  # AI routine - now default!


def load_config():
    """Load configuration from the config.json file."""
    with open('config.json') as config_file:
        data = json.load(config_file)
    return (data['routine'], data['mode'], data['volume'], data['name'], 
            data.get('debug_bluetooth', False), data.get('debug_audio', False),
            data.get('penn_state_enabled', True), data.get('ufo_persistent_memory', False))  # Load persistent memory setting


def save_config(routine, mode, volume, name, debug_bluetooth, debug_audio, penn_state_enabled, ufo_persistent_memory):
    """Save current configuration to config.json file."""
    try:
        config_data = {
            'routine': routine,
            'mode': mode,
            'volume': volume,
            'name': name,
            'debug_bluetooth': debug_bluetooth,
            'debug_audio': debug_audio,
            'penn_state_enabled': penn_state_enabled,  # Save Penn State setting
            'ufo_persistent_memory': ufo_persistent_memory
        }
        
        # Try to preserve ufo_persistent_memory setting from existing config
        try:
            with open('config.json', 'r') as f:
                existing_config = json.load(f)
                config_data['ufo_persistent_memory'] = existing_config.get('ufo_persistent_memory', False)
        except (OSError, ValueError):
            pass  # Use default if it can't read existing config
        
        with open('config.json', 'w') as config_file:
            json.dump(config_data, config_file)
        print("⚙️ Configuration saved: Routine %d, Mode %d" % (routine, mode))
        return True
    except (OSError, RuntimeError) as e:
        print("❌ Failed to save config: %s" % str(e))
        return False


def show_routine_feedback(routine):
    """Display visual feedback for routine selection."""
    cp.pixels.fill((0, 0, 0))  # Clear all pixels
    
    # Define routine colors and names
    routine_info = {
        1: {"color": (100, 0, 255), "name": "UFO Intelligence"},      # Purple
        2: {"color": (0, 255, 100), "name": "Intergalactic Cruising"}, # Green
        3: {"color": (0, 100, 255), "name": "Meditate"},              # Blue
        4: {"color": (255, 100, 0), "name": "Dance Party"}           # Orange
    }
    
    info = routine_info.get(routine, {"color": (255, 255, 255), "name": "Unknown"})
    
    # Light up pixels equal to the routine number
    for i in range(routine):
        cp.pixels[i] = info["color"]
    
    cp.pixels.show()
    print("🚀 Routine %d: %s" % (routine, info["name"]))


def show_mode_feedback(mode):
    """Display visual feedback for mode selection."""
    cp.pixels.fill((0, 0, 0))  # Clear all pixels
    
    # Define mode colors and names
    mode_info = {
        1: {"color": (255, 0, 0), "name": "Rainbow Wheel"},    # Red base
        2: {"color": (255, 0, 255), "name": "Pink Theme"},     # Pink base  
        3: {"color": (0, 0, 255), "name": "Blue Theme"}       # Blue base
    }
    
    info = mode_info.get(mode, {"color": (255, 255, 255), "name": "Unknown"})
    
    # Show mode with different patterns - spread pixels around the ring
    positions = [0, 3, 6, 9]  # Spread around a 10-pixel ring
    for i in range(mode):
        if i < len(positions):
            cp.pixels[positions[i]] = info["color"]
    
    cp.pixels.show()
    print("🎨 Mode %d: %s" % (mode, info["name"]))


def main():
    """Main application loop."""
    # Initialize default conditions
    routine, mode, volume, name, debug_bluetooth, debug_audio, penn_state_enabled, ufo_persistent_memory = load_config()
    
    # Create routine instances with debug settings
    ufo_ai = UFOIntelligence(persistent_memory=ufo_persistent_memory, penn_state_enabled=penn_state_enabled)  # Use config setting
    cruiser = IntergalacticCruising()  # Audio-reactive routine
    meditator = Meditate()  # Breathing pattern routine
    dancer = DanceParty(name, debug_bluetooth, debug_audio)  # Synchronized dance routine
    
    # Button debouncing variables
    last_button_a_time = 0
    last_button_b_time = 0
    button_debounce_delay = 0.3  # 300ms debounce delay
    config_save_timer = 0
    config_changed = False
    
    # Show the initial state
    print("🛸 UFO System Initialized")
    print("📋 Current: Routine %d, Mode %d, Volume %s" % (routine, mode, "ON" if volume else "OFF"))
    print("🏈 Penn State detection: %s" % ("ENABLED" if penn_state_enabled else "DISABLED"))
    print("💾 UFO persistent memory: %s" % ("ENABLED" if ufo_persistent_memory else "DISABLED"))
    
    # Main application loop
    cp.detect_taps = 1
    
    while True:
        current_time = time.monotonic()
        
        # Update volume based on switch position
        volume = cp.switch
        
        # Handle physical interactions - UFO AI learns from ALL interactions
        if cp.tapped:
            PhysicalActions.tapped(volume)
            # UFO AI learns from interactions on any routine
            if routine == 1:  # UFO Intelligence is now routine 1
                ufo_ai.last_interaction = time.monotonic()
                # If UFO was seeking attention, record success
                if ufo_ai.mood == "curious":
                    ufo_ai.record_successful_attention()
        
        if cp.shake(shake_threshold=11):
            PhysicalActions.shaken(volume)
            # UFO AI responds to shake as interaction
            if routine == 1:  # UFO Intelligence is now routine 1
                ufo_ai.last_interaction = time.monotonic()
                ufo_ai.energy_level = min(1.0, ufo_ai.energy_level + 0.3)
                # If UFO was seeking attention, record success
                if ufo_ai.mood == "curious":
                    ufo_ai.record_successful_attention()
        
        # Handle button presses with debouncing and improved feedback
        if cp.button_a and (current_time - last_button_a_time > button_debounce_delay):
            routine = (routine % 4) + 1  # Cycle through routines 1-4
            show_routine_feedback(routine)
            last_button_a_time = current_time
            config_changed = True
            config_save_timer = current_time
            
            # Brief delay to show feedback, then clear
            time.sleep(0.8)
            cp.pixels.fill((0, 0, 0))
            cp.pixels.show()
        
        if cp.button_b and (current_time - last_button_b_time > button_debounce_delay):
            mode = (mode % 3) + 1  # Cycle through modes 1-3
            show_mode_feedback(mode)
            last_button_b_time = current_time
            config_changed = True
            config_save_timer = current_time
            
            # Brief delay to show feedback, then clear
            time.sleep(0.8)
            cp.pixels.fill((0, 0, 0))
            cp.pixels.show()
        
        # Save config after a delay (to batch multiple rapid changes)
        if config_changed and (current_time - config_save_timer > 2.0):
            save_config(routine, mode, volume, name, debug_bluetooth, debug_audio, penn_state_enabled, ufo_persistent_memory)
            config_changed = False
        
        # Execute the selected routine
        if routine == 1:
            ufo_ai.run(mode, volume)        # 🧠 UFO Intelligence (AI behavior)
        elif routine == 2:
            cruiser.run(mode, volume)       # 🌌 Intergalactic Cruising (Audio-reactive)
        elif routine == 3:
            meditator.run(mode, volume)     # 🧘 Meditate (Breathing patterns)
        elif routine == 4:
            dancer.run(mode, volume)        # 🎵 Dance Party (Synchronized)


if __name__ == "__main__":
    main()
