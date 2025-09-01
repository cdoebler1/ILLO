# Charles Doebler at Feral Cat AI
# Interaction Manager - Centralized interaction detection and routing

import time
from adafruit_circuitplayground import cp
from physical_actions import PhysicalActions
from light_manager import LightManager


class InteractionManager:
    def __init__(self, enable_debug=False):
        """
        Initialize Interaction Manager.
        
        Args:
            enable_debug: Whether to enable interaction debug output
        """
        self.enable_debug = enable_debug
        
        # Interaction debouncing
        self.last_tap_time = 0
        self.last_shake_time = 0
        self.tap_debounce_delay = 0.5  # 500ms between taps
        self.shake_debounce_delay = 1.0  # 1 second between shakes
        
        # Light manager for light interactions (created when needed)
        self.light_manager = None
        
        # Routine interaction preferences
        self.routine_interactions = {
            1: {  # UFO Intelligence - all interactions
                'tap': True,
                'shake': True,
                'light_interactions': True,
                'light_brightness': True
            },
            2: {  # Intergalactic Cruising - only brightness adjustment
                'tap': False,
                'shake': False,
                'light_interactions': False,
                'light_brightness': True
            },
            3: {  # Meditate - minimal interactions
                'tap': False,
                'shake': False,
                'light_interactions': False,
                'light_brightness': True
            },
            4: {  # Dance Party - all interactions
                'tap': True,
                'shake': True,
                'light_interactions': True,
                'light_brightness': True
            }
        }
        
        print("[INTERACT] Interaction Manager initialized (debug: %s)" % enable_debug)
    
    def setup_for_routine(self, routine_number):
        """
        Set up interaction detection for the specified routine.
        
        Args:
            routine_number: The active routine number (1-4)
        """
        preferences = self.routine_interactions.get(routine_number, {})
        
        # Create light manager if any light features are needed
        needs_light_interactions = preferences.get('light_interactions', False)
        needs_light_brightness = preferences.get('light_brightness', False)
        
        if needs_light_interactions or needs_light_brightness:
            if self.light_manager is None:
                self.light_manager = LightManager(enable_interactions=needs_light_interactions)
            elif self.light_manager.enable_interactions != needs_light_interactions:
                # Recreate with correct interaction setting
                self.light_manager = LightManager(enable_interactions=needs_light_interactions)
        else:
            # Clean up light manager if not needed
            if self.light_manager is not None:
                self.light_manager = None
        
        if self.enable_debug:
            print("[INTERACT] Setup for routine %d - tap:%s, shake:%s, light_int:%s, light_bright:%s" %
                  (routine_number, preferences.get('tap', False), preferences.get('shake', False),
                   preferences.get('light_interactions', False), preferences.get('light_brightness', False)))
    
    def check_interactions(self, routine_number, volume, pixels=None):
        """
        Check for all relevant interactions for the current routine.
        
        Args:
            routine_number: Current active routine (1-4)
            volume: Current volume/sound setting
            pixels: NeoPixel object for brightness adjustment
            
        Returns:
            dict: Dictionary of detected interactions
        """
        interactions = {
            'tap': False,
            'shake': False,
            'light_interaction': False,
            'light_change': 0,
            'current_light': 0,
            'brightness_adjusted': False
        }
        
        preferences = self.routine_interactions.get(routine_number, {})
        current_time = time.monotonic()
        
        # Check tap interactions
        if preferences.get('tap', False) and cp.tapped:
            if current_time - self.last_tap_time > self.tap_debounce_delay:
                interactions['tap'] = True
                self.last_tap_time = current_time
                PhysicalActions.tapped(volume)
                
                if self.enable_debug:
                    print("[INTERACT] Tap detected for routine %d" % routine_number)
        
        # Check shake interactions
        if preferences.get('shake', False) and cp.shake(shake_threshold=11):
            if current_time - self.last_shake_time > self.shake_debounce_delay:
                interactions['shake'] = True
                self.last_shake_time = current_time
                PhysicalActions.shaken(volume)
                
                if self.enable_debug:
                    print("[INTERACT] Shake detected for routine %d" % routine_number)
        
        # Light-based interactions and brightness adjustment
        if self.light_manager is not None:
            # Brightness adjustment (if enabled and pixels provided)
            if preferences.get('light_brightness', False) and pixels is not None:
                current_light = self.light_manager.update_brightness_for_ambient_light(pixels)
                interactions['current_light'] = current_light
                interactions['brightness_adjusted'] = True
            
            # Light interaction detection (if enabled)
            if preferences.get('light_interactions', False):
                light_detected, light_change, current_light = self.light_manager.check_light_interaction()
                interactions['light_interaction'] = light_detected
                interactions['light_change'] = light_change
                interactions['current_light'] = current_light
                
                if light_detected and self.enable_debug:
                    print("[INTERACT] Light interaction detected for routine %d (change: %.1f)" %
                          (routine_number, light_change))
        
        return interactions
    
    def get_light_manager(self):
        """Get the light manager instance (if available)."""
        return self.light_manager
    
    def set_debug(self, enabled):
        """Enable or disable interaction debug output."""
        self.enable_debug = enabled
        print("[INTERACT] Debug output %s" % ("enabled" if enabled else "disabled"))
