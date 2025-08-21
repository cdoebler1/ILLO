# Charles Doebler at Feral Cat AI
# UFO College System - College spirit and celebration management

import time
import random
from college_manager import CollegeManager
from music_player import MusicPlayer
from chant_detector import ChantDetector


class UFOCollegeSystem:
    def __init__(self, college_spirit_enabled=True, college="penn_state"):
        self.college_spirit_enabled = college_spirit_enabled
        self.college_manager = CollegeManager(college)
        self.music_player = MusicPlayer()

        # NEW: Separate chant detection system
        self.chant_detector = ChantDetector(self.college_manager)

        # College spirit state
        self.school_spirit = 50  # 0-100 scale
        self.last_college_trigger = 0.0  # Ensure a float type
        self.college_cooldown = 15.0  # Seconds between college celebrations

        # Random college behavior timing (when chant detection is off)
        self.last_random_college_event = 0.0
        self.random_college_interval = 45.0  # Random college behavior every 45-90 seconds
        self.last_random_behavior = None  # Track last behavior to avoid repeats

        # Get college-specific data
        if self.college_manager.is_enabled():
            college_colors = self.college_manager.get_colors()
            self.college_primary = college_colors["primary"]
            self.college_secondary = college_colors["secondary"]
        else:
            self.college_primary = [255, 255, 255]
            self.college_secondary = [128, 128, 128]

    def set_chant_detection_enabled(self, enabled):
        """Enable or disable chant detection."""
        self.chant_detector.set_enabled(enabled)

    def is_college_celebration_ready(self):
        """Check if enough time has passed since last college celebration."""
        current_time = time.monotonic()
        return (current_time - self.last_college_trigger) >= self.college_cooldown

    def execute_college_celebration(self, hardware, sound_enabled):
        """Execute a college celebration when chant is detected."""
        print(
            "[UFO AI] 🏈 COLLEGE CELEBRATION! %s!" % self.college_manager.get_college_name())

        # Start synchronized celebration - light pattern during music
        if sound_enabled:
            # Play chant with synchronized light pattern
            chant_played = self._play_chant_with_lights(hardware, sound_enabled)
        else:
            # If sound disabled, show full light show
            chant_played = False
            self._college_light_show(hardware)

        # Boost school spirit
        self.school_spirit = min(100, self.school_spirit + 15)
        print("[UFO AI] 📈 School spirit boosted to %d!" % self.school_spirit)

        return chant_played

    def _play_chant_with_lights(self, hardware, sound_enabled):
        """Play chant with synchronized light pattern instead of blocking light show."""
        if not sound_enabled:
            return False

        chant_notes = self.college_manager.get_chant_notes()
        if not chant_notes:
            return self._fallback_chant_tones(hardware, sound_enabled)

        try:
            # Get BPM for synchronization
            bpm = 120
            if self.college_manager.college_data:
                if 'chants' in self.college_manager.college_data:
                    if 'primary' in self.college_manager.college_data['chants']:
                        chant_primary = self.college_manager.college_data['chants'][
                            'primary']
                        if 'bpm' in chant_primary:
                            bpm = chant_primary['bpm']

            # Play music with synchronized light callback
            return self.music_player.play_music_with_lights(
                hardware, sound_enabled, chant_notes, bpm, 3, "chant",
                self._chant_light_callback
            )

        except Exception as e:
            print("[UFO AI] Chant with lights error: %s" % str(e))
            return self._fallback_chant_tones(hardware, sound_enabled)

    def _chant_light_callback(self, hardware, beat_count, note_info):
        """Light pattern callback synchronized with chant music using college colors."""
        try:
            # Get college colors using the proper method
            primary_color, secondary_color = self.get_college_colors()

            # Use note information for more sophisticated patterns
            frequency = note_info.get('frequency', 0)
            duration = note_info.get('duration', 0)
            note_position = note_info.get('note_position', 0)
            repetition = note_info.get('repetition', 1)

            # Create dynamic patterns based on note characteristics
            if frequency == 0:  # Rest/silence
                # Dim lights during rests
                dimmed_primary = tuple(int(c * 0.2) for c in primary_color)
                for i in range(10):
                    hardware.pixels[i] = dimmed_primary

            elif frequency > 600:  # High notes - bright primary color
                for i in range(10):
                    hardware.pixels[i] = primary_color

            elif frequency > 400:  # Medium notes - alternating pattern
                for i in range(10):
                    if (i + note_position) % 2 == 0:
                        hardware.pixels[i] = primary_color
                    else:
                        hardware.pixels[i] = secondary_color

            else:  # Low notes - secondary color with pulsing
                intensity = min(1.0, 0.5 + (duration * 2))  # Longer notes = brighter
                pulsed_secondary = tuple(int(c * intensity) for c in secondary_color)
                for i in range(10):
                    hardware.pixels[i] = pulsed_secondary

            # Add special effects based on repetition
            if repetition > 1:
                # Later repetitions get more energetic patterns
                if int(beat_count) % (4 // repetition) == 0:
                    # Flash opposite color briefly for emphasis
                    flash_color = secondary_color if frequency > 400 else primary_color
                    for i in range(10):
                        if i % 2 == 0:
                            hardware.pixels[i] = flash_color

            hardware.pixels.show()

        except Exception as e:
            print("[UFO AI] Light callback error: %s" % str(e))
            # Fallback to simple college color flash
            try:
                primary_color, _ = self.get_college_colors()
                if int(beat_count) % 2 == 0:
                    for i in range(10):
                        hardware.pixels[i] = primary_color
                    hardware.pixels.show()
                else:
                    hardware.clear_pixels()
                    hardware.pixels.show()
            except (OSError, RuntimeError, AttributeError, KeyError,
                    ValueError) as fallback_error:
                print("[UFO AI] Fallback error: %s" % str(fallback_error))
                # Ultimate fallback to white flash
                if int(beat_count) % 2 == 0:
                    for i in range(10):
                        hardware.pixels[i] = (255, 255, 255)
                    hardware.pixels.show()
                else:
                    hardware.clear_pixels()
                    hardware.pixels.show()

    def update_school_spirit(self, interaction_success=False):
        """Update school spirit based on interactions."""
        if not self.college_spirit_enabled:
            return

        current_time = time.monotonic()

        if interaction_success:
            # Boost spirit on successful interactions
            old_spirit = self.school_spirit
            self.school_spirit = min(100, self.school_spirit + 5)
            if self.school_spirit > old_spirit:
                print("[UFO AI] 🏈 School spirit increased to %d!" % self.school_spirit)
        else:
            # Natural decay over time (very slow)
            time_since_last_boost = current_time - self.last_college_trigger
            if time_since_last_boost > 300:  # 5 minutes
                if self.school_spirit > 40:  # Don't let it go too low
                    self.school_spirit = max(40, self.school_spirit - 1)

    def get_college_behavior_modifier(self, base_mood):
        """Modify behavior based on college spirit level."""
        if not self.college_spirit_enabled:
            return base_mood

        # High school spirit can enhance certain moods
        if self.school_spirit > 80:
            if base_mood == "excited":
                return "college_excited"  # Special college-spirited excited behavior
            elif base_mood == "neutral" and random.random() < 0.1:
                return "college_pride"  # Occasional pride display

        return base_mood

    def get_college_colors(self):
        """Get college primary and secondary colors as RGB tuples."""
        if not self.college_spirit_enabled or not self.college_manager.is_enabled():
            # Return default colors if college system disabled
            return (255, 255, 255), (128, 128, 128)

        try:
            colors = self.college_manager.get_colors()
            primary = tuple(int(c) for c in colors["primary"])
            secondary = tuple(int(c) for c in colors["secondary"])
            return primary, secondary
        except Exception as e:
            print("[UFO AI] Error getting college colors: %s" % str(e))
            return (255, 255, 255), (128, 128, 128)

    def detect_college_chant(self, np_samples):
        """Detect college-specific chant patterns in audio."""
        if not self.college_spirit_enabled:
            return False

        # Check cooldown at the system level
        current_time = time.monotonic()
        if current_time - self.last_college_trigger < self.college_cooldown:
            return False

        # Use the dedicated chant detector
        chant_detected = self.chant_detector.detect_chant(np_samples)

        if chant_detected:
            self.last_college_trigger = current_time

        return chant_detected

    def check_for_random_college_behavior(self, hardware, sound_enabled,
                                          chant_detection_enabled):
        """Trigger random college behaviors when chant detection is disabled but college spirit is enabled."""
        if not self.college_spirit_enabled or chant_detection_enabled:
            return False

        current_time = time.monotonic()

        # Random timing - vary between 45-90 seconds
        time_since_last = current_time - self.last_random_college_event
        random_interval = self.random_college_interval + (random.random() * 45.0)

        if time_since_last > random_interval:
            # Random college spirit boost
            college_behaviors = ['chant', 'fight_song', 'light_show', 'spirit_boost']

            # Remove the last behavior to prevent immediate repeats
            if self.last_random_behavior in college_behaviors:
                available_behaviors = [b for b in college_behaviors if
                                       b != self.last_random_behavior]
                behavior = random.choice(available_behaviors)
            else:
                behavior = random.choice(college_behaviors)

            print("[UFO AI] 🏈 Random %s spirit! (%s)" % (
                self.college_manager.get_college_name(), behavior))

            if behavior == 'chant':
                self._play_chant(hardware, sound_enabled)
            elif behavior == 'fight_song':
                self._play_fight_song(hardware, sound_enabled)
            elif behavior == 'light_show':
                self._college_light_show(hardware)
            elif behavior == 'spirit_boost':
                self.school_spirit = min(100, self.school_spirit + 10)
                print("[UFO AI] 📈 School spirit boosted to %d!" % self.school_spirit)

            self.last_random_college_event = current_time
            self.last_random_behavior = behavior

            return True

        return False

    def _play_chant(self, hardware, sound_enabled):
        """Play college chant using unified music player."""
        if not sound_enabled:
            return False

        chant_notes = self.college_manager.get_chant_notes()
        if not chant_notes:
            return self._fallback_chant_tones(hardware, sound_enabled)

        try:
            # Get BPM from college data (default to 120 BPM if not specified)
            bpm = 120  # Default fallback

            if self.college_manager.college_data:
                if 'chants' in self.college_manager.college_data:
                    if 'primary' in self.college_manager.college_data['chants']:
                        chant_primary = self.college_manager.college_data['chants'][
                            'primary']
                        if 'bpm' in chant_primary:
                            bpm = chant_primary['bpm']

            # Chants repeat 3 times
            return self.music_player.play_music(hardware, sound_enabled, chant_notes,
                                                bpm, 3, "chant")

        except Exception as e:
            print("[UFO AI] Chant playback error: %s" % str(e))
            return self._fallback_chant_tones(hardware, sound_enabled)

    def _play_fight_song(self, hardware, sound_enabled):
        """Play college fight song using unified music player."""
        if not sound_enabled:
            return False

        fight_song_notes = self.college_manager.get_fight_song_notes()
        if not fight_song_notes:
            return False

        try:
            # Get BPM from college data (default to 120 BPM if not specified)
            bpm = 120
            if self.college_manager.college_data and 'fight_song' in self.college_manager.college_data:
                bpm = self.college_manager.college_data['fight_song'].get('bpm', 120)

            # Fight songs play once
            return self.music_player.play_music(hardware, sound_enabled,
                                                fight_song_notes, bpm, 1, "fight_song")

        except Exception as e:
            print("[UFO AI] Fight song error: %s" % str(e))
            return False

    def _fallback_chant_tones(self, hardware, sound_enabled):
        """Fallback chant using simple tone sequence when no chant notes available."""
        try:
            response_tone = self.college_manager.get_response_tone("chant_response")
            base_freq, duration = response_tone

            # Enthusiastic rising tone sequence - repeat 3 times
            for rep in range(3):
                for i in range(3):
                    freq = int(float(base_freq) + (i * 100))
                    hardware.play_tone_if_enabled(freq, float(duration) * 0.8,
                                                  sound_enabled)
                    time.sleep(0.1)
                time.sleep(0.3)  # Pause between repetitions

            # Victory fanfare
            fanfare_tone = self.college_manager.get_response_tone("victory_fanfare")
            fanfare_freq, fanfare_duration = fanfare_tone
            hardware.play_tone_if_enabled(int(fanfare_freq), float(fanfare_duration),
                                          sound_enabled)
            return True

        except Exception as e:
            print("[UFO AI] Fallback chant error: %s" % str(e))
            return False

    def _college_light_show(self, hardware):
        """Display college colors in celebration pattern."""
        try:
            print("[UFO AI] 🎨 %s light show!" % self.college_manager.get_college_name())

            # Ensure color values are integers
            primary_color = tuple(int(c) for c in self.college_primary)
            secondary_color = tuple(int(c) for c in self.college_secondary)

            # Phase 1: Opening fanfare - expanding rings
            for ring_cycle in range(3):
                # Expanding ring from the center
                hardware.clear_pixels()
                for ring in range(5):
                    start_pos = int(5 - ring)
                    end_pos = int(5 + ring)
                    for i in range(max(0, start_pos), min(10, end_pos)):
                        hardware.pixels[
                            i] = primary_color if ring_cycle % 2 == 0 else secondary_color
                    hardware.pixels.show()
                    time.sleep(0.1)
                time.sleep(0.2)

            # Phase 2: Alternating wave pattern
            for wave_cycle in range(6):
                # Wave going right
                for pos in range(12):  # Go beyond 10 to clear
                    hardware.clear_pixels()
                    for i in range(3):  # 3-pixel wave
                        pixel_pos = int((pos - i) % 10)
                        if 0 <= pixel_pos < 10:
                            color = primary_color if wave_cycle % 2 == 0 else secondary_color
                            intensity = 1.0 - (i * 0.3)  # Fade trail
                            adjusted_color = tuple(
                                max(0, min(255, int(c * intensity))) for c in color)
                            hardware.pixels[pixel_pos] = adjusted_color
                    hardware.pixels.show()
                    time.sleep(0.08)
                time.sleep(0.1)

            # Phase 3: Pulsing celebration
            for pulse_cycle in range(8):
                # Pulse all pixels with both colors
                intensity_levels = [0.2, 0.5, 0.8, 1.0, 0.8, 0.5, 0.2]
                for intensity in intensity_levels:
                    color = primary_color if pulse_cycle % 2 == 0 else secondary_color
                    adjusted_color = tuple(
                        max(0, min(255, int(c * intensity))) for c in color)
                    for i in range(10):
                        hardware.pixels[i] = adjusted_color
                    hardware.pixels.show()
                    time.sleep(0.1)

                # Quick flash opposite color
                opposite_color = secondary_color if pulse_cycle % 2 == 0 else primary_color
                for i in range(10):
                    hardware.pixels[i] = opposite_color
                hardware.pixels.show()
                time.sleep(0.05)

            # Phase 4: Alternating stripes
            for stripe_cycle in range(10):
                hardware.clear_pixels()
                # Create an alternating pattern
                for i in range(10):
                    if (i + stripe_cycle) % 2 == 0:
                        hardware.pixels[i] = primary_color
                    else:
                        hardware.pixels[i] = secondary_color
                hardware.pixels.show()
                time.sleep(0.15)

            # Phase 5: Grand finale - rapid flash sequence
            finale_colors = [primary_color, secondary_color]
            for finale_flash in range(20):
                color = finale_colors[finale_flash % 2]
                # All pixels flash
                for i in range(10):
                    hardware.pixels[i] = color
                hardware.pixels.show()
                time.sleep(0.08)
                # Brief darkness
                hardware.clear_pixels()
                hardware.pixels.show()
                time.sleep(0.05)

            # Phase 6: Final sustained glow
            for i in range(10):
                hardware.pixels[i] = primary_color
            hardware.pixels.show()
            time.sleep(1.0)

            # Fade out slowly - FIXED: Ensure all values are integers
            for fade_step in range(10, 0, -1):  # This should be integers
                fade_intensity = float(fade_step) / 10.0
                faded_color = tuple(
                    max(0, min(255, int(c * fade_intensity))) for c in primary_color)
                for i in range(10):
                    hardware.pixels[i] = faded_color
                hardware.pixels.show()
                time.sleep(0.1)

        except Exception as e:
            print("[UFO AI] College light show error: %s" % str(e))
        finally:
            # Always clear pixels at the end
            hardware.clear_pixels()
            hardware.pixels.show()
