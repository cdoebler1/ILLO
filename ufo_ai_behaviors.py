# Charles Doebler at Feral Cat AI
# UFO AI Behavior Patterns - College-Aware

import math
import random
import time

class UFOAIBehaviors:
    def __init__(self, hardware, college_system):
        self.hardware = hardware
        self.college_system = college_system
        self.rotation_offset = 0
        self.audio_reactive_mode = False
        self.last_audio_update = 0
        self.last_attention_update = 0

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
            self._attention_seeking_visualizer(color_func, volume, current_time, audio_history, curiosity_level)
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
            
            chase_speed = 10.0 * energy_level
            offset = int(current_time * chase_speed) % 10
            
            for i in range(10):
                if (i + offset) % 4 < 2:
                    self.hardware.pixels[i] = tuple(primary_color)
                else:
                    self.hardware.pixels[i] = tuple(secondary_color)
            
            self.hardware.pixels.show()
            
            if volume and random.random() < 0.3:
                college_freqs = [400, 500, 600, 800]
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
                breath_cycle = 8.0
                breath_phase = (current_time % breath_cycle) / breath_cycle
                
                if breath_phase < 0.3:
                    main_color = primary_color
                    accent_color = secondary_color
                elif breath_phase < 0.7:
                    blend_factor = (breath_phase - 0.3) / 0.4
                    main_color = [int(primary_color[i] * (1-blend_factor) + 
                                    secondary_color[i] * blend_factor) for i in range(3)]
                    accent_color = primary_color
                else:
                    main_color = secondary_color
                    accent_color = primary_color
                
                for i in range(10):
                    if i % 4 == 0:
                        self.hardware.pixels[i] = tuple(accent_color)
                    else:
                        self.hardware.pixels[i] = tuple(main_color)
                
            else:
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

    def _attention_seeking_visualizer(self, color_func, volume, current_time, audio_history, curiosity_level):
        """Enhanced audio visualizer for attention-seeking behavior."""
        try:
            # Get fresh audio samples for real-time visualization
            from audio_processor import AudioProcessor
            if not hasattr(self, '_audio_processor'):
                self._audio_processor = AudioProcessor()
            
            # Record fresh samples for visualization
            np_samples = self._audio_processor.record_samples()
            
            if len(np_samples) > 50:
                # Process audio like Intergalactic Cruising
                deltas = self._audio_processor.compute_deltas(np_samples)
                freq = self._audio_processor.calculate_frequency(deltas)
                
                if freq is not None and len(deltas) > 0:
                    # Audio-reactive visualization with attention-seeking enhancements
                    self._attention_audio_reactive(deltas, color_func, volume, current_time, curiosity_level, freq)
                else:
                    # Attention-seeking idle pattern when no audio
                    self._attention_seeking_idle(color_func, volume, current_time, curiosity_level)
            else:
                # Fallback to attention-seeking pattern
                self._attention_seeking_idle(color_func, volume, current_time, curiosity_level)
                
        except Exception as e:
            print("[UFO AI] Attention visualizer error: %s" % str(e))
            # Fallback to simple attention pattern
            self._attention_seeking_idle(color_func, volume, current_time, curiosity_level)

    def _attention_audio_reactive(self, deltas, color_func, volume, current_time, curiosity_level, freq):
        """Audio-reactive visualization optimized for getting attention."""
        # Map audio deltas to pixel intensities
        pixel_data = self.hardware.map_deltas_to_pixels(deltas)
        
        # Enhanced rotation speed for attention-seeking
        attention_multiplier = 1.0 + (curiosity_level * 2.0)
        time_delta = current_time - self.last_attention_update
        self.rotation_offset = (self.rotation_offset + freq * time_delta * 0.02 * attention_multiplier) % 10
        
        # Clear and apply enhanced visualization
        self.hardware.clear_pixels()
        
        # Enhanced intensity and broader threshold for more dramatic effect
        for i in range(10):
            rotated_index = int((i + self.rotation_offset) % 10)
            base_intensity = pixel_data[i] * 4  # More sensitive than cruising
            
            # Add attention-seeking pulse enhancement
            pulse_factor = 1.0 + (0.3 * math.sin(current_time * 8 + i))
            enhanced_intensity = min(255, int(base_intensity * pulse_factor))
            
            # Lower threshold for more pixels lit (more eye-catching)
            if enhanced_intensity > 25:
                self.hardware.pixels[rotated_index] = color_func(enhanced_intensity)
        
        self.hardware.pixels.show()
        
        # Audio feedback for attention-seeking
        if volume and random.random() < 0.15:
            attention_freq = int(freq + (curiosity_level * 100))
            self.hardware.play_tone_if_enabled(attention_freq, 0.08, volume)
        
        # Shorter fade for more dynamic appearance
        time.sleep(0.03)
        for i in range(10):
            current_color = self.hardware.pixels[i]
            if current_color != (0, 0, 0):
                faded_color = tuple(int(c * 0.85) for c in current_color)
                self.hardware.pixels[i] = faded_color
        
        self.last_attention_update = current_time

    def _attention_seeking_idle(self, color_func, volume, current_time, curiosity_level):
        """Eye-catching idle pattern when seeking attention but no audio detected."""
        # Multi-mode attention pattern that cycles
        pattern_cycle = int(current_time * 2) % 4
        
        if pattern_cycle == 0:
            # Scanning comet pattern
            scan_speed = 3.0 + (curiosity_level * 2.0)
            scan_pos = int((current_time * scan_speed) % 10)
            
            self.hardware.clear_pixels()
            # Bright comet head
            self.hardware.pixels[scan_pos] = color_func(220)
            # Fading trail
            for i in range(1, 4):
                trail_pos = (scan_pos - i) % 10
                trail_intensity = max(50, 220 - (i * 60))
                self.hardware.pixels[trail_pos] = color_func(trail_intensity)
        
        elif pattern_cycle == 1:
            # Pulsing all pixels for maximum attention
            pulse_speed = 4.0 + curiosity_level
            pulse_intensity = int(120 + (100 * math.sin(current_time * pulse_speed)))
            
            for i in range(10):
                # Add slight phase offset per pixel for ripple effect
                pixel_pulse = pulse_intensity + int(20 * math.sin(current_time * pulse_speed + i * 0.5))
                pixel_pulse = max(60, min(255, pixel_pulse))
                self.hardware.pixels[i] = color_func(pixel_pulse)
        
        elif pattern_cycle == 2:
            # Alternating segments for attention
            segment_speed = 5.0 + curiosity_level
            offset = int(current_time * segment_speed) % 2
            
            for i in range(10):
                if (i + offset) % 2 == 0:
                    self.hardware.pixels[i] = color_func(200)
                else:
                    self.hardware.pixels[i] = color_func(80)
        
        else:  # pattern_cycle == 3
            # Expanding ring pattern
            ring_speed = 2.0 + curiosity_level
            ring_phase = (current_time * ring_speed) % 2.0
            
            if ring_phase < 1.0:
                # Expanding ring
                ring_size = int(ring_phase * 5)
                self.hardware.clear_pixels()
                for i in range(min(ring_size + 1, 5)):
                    pos1 = (4 + i) % 10  # Ring expanding from center
                    pos2 = (6 - i) % 10
                    intensity = max(80, 200 - (i * 30))
                    self.hardware.pixels[pos1] = color_func(intensity)
                    if pos1 != pos2:
                        self.hardware.pixels[pos2] = color_func(intensity)
            else:
                # Brief pause with dim glow
                for i in range(10):
                    self.hardware.pixels[i] = color_func(60)
        
        self.hardware.pixels.show()
        
        # Occasional attention-seeking beeps
        if volume and random.random() < 0.08:
            attention_freq = 350 + int(curiosity_level * 150) + random.randint(0, 200)
            self.hardware.play_tone_if_enabled(attention_freq, 0.1, volume)

    def _neutral_behavior(self, color_func, current_time, energy_level):
        """Default UFO idle behavior."""
        base_intensity = 100 + int(30 * math.sin(current_time * 0.5))
        rotation_speed = 1.0 + (energy_level * 0.5)
        
        for i in range(10):
            phase = (current_time * rotation_speed + i * 0.628) % 6.28
            pixel_intensity = base_intensity + int(20 * math.sin(phase))
            self.hardware.pixels[i] = color_func(pixel_intensity)
        
        self.hardware.pixels.show()
