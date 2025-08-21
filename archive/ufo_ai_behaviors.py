
# Charles Doebler at Feral Cat AI
# UFO AI Behavior Patterns - College-Aware

import math
import random

class UFOAIBehaviors:
    def __init__(self, hardware, college_system):
        self.hardware = hardware
        self.college_system = college_system
        self.rotation_offset = 0
        self.audio_reactive_mode = False
        self.last_audio_update = 0

    def execute_behavior(self, mood, color_func, volume, current_time, 
                        curiosity_level, energy_level, audio_history):
        """Execute the UFO's current behavioral state with college awareness."""
        # Let college system modify mood if appropriate
        mood = self.college_system.get_college_behavior_modifier(mood)
        
        if mood == "investigating":
            self._investigate_behavior(color_func, volume, current_time, curiosity_level)
        elif mood == "excited":
            if self.college_system.college_spirit_enabled and self.college_system.school_spirit > 70:
                self._excited_college_behavior(color_func, volume, current_time, energy_level)
            else:
                self._excited_behavior(color_func, volume, current_time, energy_level)
        elif mood == "curious":
            self._audio_curious_behavior(color_func, volume, current_time, audio_history)
        elif mood == "calm":
            self._subtle_college_pride(color_func, current_time)
        else:  # neutral
            self._neutral_behavior(color_func, current_time, energy_level)

    def _investigate_behavior(self, color_func, volume, current_time, curiosity_level):
        """UFO investigates something interesting."""
        sweep_speed = 3.0 * curiosity_level
        sweep_position = (math.sin(current_time * sweep_speed) + 1) / 2
        
        self.hardware.clear_pixels()
        
        center_pixel = int(sweep_position * 9)
        intensity = int(200 + (curiosity_level * 55))
        
        self.hardware.pixels[center_pixel] = color_func(intensity)
        if center_pixel > 0:
            self.hardware.pixels[center_pixel - 1] = color_func(intensity // 3)
        if center_pixel < 9:
            self.hardware.pixels[center_pixel + 1] = color_func(intensity // 3)
        
        self.hardware.pixels.show()
        
        if volume and random.random() < 0.1:
            freq = 400 + int(sweep_position * 200)
            self.hardware.play_tone_if_enabled(freq, 0.05, volume)

    def _excited_behavior(self, color_func, volume, current_time, energy_level):
        """Standard excited UFO behavior."""
        chase_speed = 8.0 * energy_level
        offset = int(current_time * chase_speed) % 10
        
        for i in range(10):
            pixel_phase = (i + offset) % 10
            intensity = int(150 + (105 * math.sin(pixel_phase * 0.628)))
            self.hardware.pixels[i] = color_func(intensity)
        
        self.hardware.pixels.show()
        
        if volume and random.random() < 0.2:
            freq = 600 + random.randint(0, 400)
            self.hardware.play_tone_if_enabled(freq, 0.08, volume)

    def _excited_college_behavior(self, color_func, volume, current_time, energy_level):
        """College-spirited excited behavior."""
        try:
            primary_color, secondary_color = self.college_system.get_college_colors()
            
            chase_speed = 10.0 * energy_level  # Faster for college excitement
            offset = int(current_time * chase_speed) % 10
            
            for i in range(10):
                if (i + offset) % 4 < 2:  # Alternate between college colors
                    self.hardware.pixels[i] = tuple(primary_color)
                else:
                    self.hardware.pixels[i] = tuple(secondary_color)
            
            self.hardware.pixels.show()
            
            # College-spirited sounds
            if volume and random.random() < 0.3:
                college_freqs = [400, 500, 600, 800]  # School chant frequencies
                freq = random.choice(college_freqs)
                self.hardware.play_tone_if_enabled(freq, 0.12, volume)
                
        except Exception as e:
            print("[UFO AI] College behavior error: %s" % str(e))
            self._excited_behavior(color_func, volume, current_time, energy_level)

    def _subtle_college_pride(self, color_func, current_time):
        """Calm behavior with subtle college pride."""
        try:
            if self.college_system.college_spirit_enabled:
                primary_color, secondary_color = self.college_system.get_college_colors()
                
                # Gentle breathing in college colors
                breath_cycle = 8.0  # Slower, more dignified
                breath_phase = (current_time % breath_cycle) / breath_cycle
                
                if breath_phase < 0.3:
                    # Primary color dominance
                    main_color = primary_color
                    accent_color = secondary_color
                elif breath_phase < 0.7:
                    # Blend phase
                    blend_factor = (breath_phase - 0.3) / 0.4
                    main_color = [int(primary_color[i] * (1-blend_factor) + 
                                    secondary_color[i] * blend_factor) for i in range(3)]
                    accent_color = primary_color
                else:
                    # Secondary color dominance  
                    main_color = secondary_color
                    accent_color = primary_color
                
                # Most pixels show main color, few show accent
                for i in range(10):
                    if i % 4 == 0:  # Every 4th pixel
                        self.hardware.pixels[i] = tuple(accent_color)
                    else:
                        self.hardware.pixels[i] = tuple(main_color)
                
            else:
                # Standard calm behavior
                breath_cycle = 6.0
                breath_phase = (current_time % breath_cycle) / breath_cycle
                
                if breath_phase < 0.5:
                    intensity = int(80 + (breath_phase * 2 * 70))
                else:
                    intensity = int(150 - ((breath_phase - 0.5) * 2 * 70))
                
                breath_color = color_func(intensity)
                for i in range(10):
                    self.hardware.pixels[i] = breath_color
                    
            self.hardware.pixels.show()
            
        except Exception as e:
            print("[UFO AI] College pride behavior error: %s" % str(e))
            # Fallback to standard calm behavior
            breath_cycle = 6.0
            breath_phase = (current_time % breath_cycle) / breath_cycle
            
            if breath_phase < 0.5:
                intensity = int(80 + (breath_phase * 2 * 70))
            else:
                intensity = int(150 - ((breath_phase - 0.5) * 2 * 70))
            
            breath_color = color_func(intensity)
            for i in range(10):
                self.hardware.pixels[i] = breath_color
            
            self.hardware.pixels.show()

    def _audio_curious_behavior(self, color_func, volume, current_time, audio_history):
        """Audio-reactive curious behavior."""
        if audio_history and len(audio_history) > 0:
            recent_audio = audio_history[-1]
            focus_pixel = int((recent_audio % 50) / 5)
            focus_pixel = max(0, min(focus_pixel, 9))
            
            self.hardware.clear_pixels()
            self.hardware.pixels[focus_pixel] = color_func(200)
            
            # Add trailing glow
            for i in range(1, 4):
                left_pixel = (focus_pixel - i) % 10
                right_pixel = (focus_pixel + i) % 10
                glow_intensity = max(50, 200 - (i * 50))
                self.hardware.pixels[left_pixel] = color_func(glow_intensity)
                self.hardware.pixels[right_pixel] = color_func(glow_intensity)
        else:
            # Default seeking pattern
            scan_pos = int((current_time * 2) % 10)
            self.hardware.clear_pixels()
            self.hardware.pixels[scan_pos] = color_func(180)
            self.hardware.pixels[(scan_pos + 5) % 10] = color_func(100)
        
        self.hardware.pixels.show()
        
        if volume and random.random() < 0.05:
            freq = 300 + random.randint(0, 300)
            self.hardware.play_tone_if_enabled(freq, 0.1, volume)

    def _neutral_behavior(self, color_func, current_time, energy_level):
        """Default UFO idle behavior."""
        base_intensity = 100 + int(30 * math.sin(current_time * 0.5))
        rotation_speed = 1.0 + (energy_level * 0.5)
        
        for i in range(10):
            phase = (current_time * rotation_speed + i * 0.628) % 6.28
            pixel_intensity = base_intensity + int(20 * math.sin(phase))
            self.hardware.pixels[i] = color_func(pixel_intensity)
        
        self.hardware.pixels.show()
