# Charles Doebler at Feral Cat AI
# UFO College System - College spirit and chant detection

import time
import random
from college_manager import CollegeManager
from music_player import MusicPlayer


class UFOCollegeSystem:
    def __init__(self, college_spirit_enabled=True, college="penn_state"):
        self.college_spirit_enabled = college_spirit_enabled
        self.college_manager = CollegeManager(college)
        self.music_player = MusicPlayer()

        # College spirit state
        self.school_spirit = 50  # 0-100 scale
        self.last_college_trigger = 0.0  # Ensure a float type
        self.college_cooldown = 15.0  # Seconds between college celebrations
        self._last_college_check = 0.0  # Ensure a float type

        # Random college behavior timing (when chant detection is off)
        self.last_random_college_event = 0.0
        self.random_college_interval = 45.0  # Random college behavior every 45-90 seconds
        self.last_random_behavior = None  # NEW: Track last behavior to avoid repeats

        # Get college-specific data
        if self.college_manager.is_enabled():
            college_colors = self.college_manager.get_colors()
            self.college_primary = college_colors["primary"]
            self.college_secondary = college_colors["secondary"]
        else:
            self.college_primary = [255, 255, 255]
            self.college_secondary = [128, 128, 128]

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
            self.last_random_behavior = behavior  # NEW: Remember this behavior

            return True

        return False

    def _random_college_chant(self, hardware, sound_enabled):
        """UFO randomly shows college spirit with chant-like behavior."""
        if not sound_enabled:
            return

        try:
            # Try to play the detailed chant first
            if self._play_chant(hardware, sound_enabled):
                print(
                    "[UFO AI] 📣 Random detailed %s chant!" % self.college_manager.get_college_name())
                return

            # Fallback to simple tone sequence if detailed chant isn't available
            chant_tones = [400, 500, 600, 500, 400, 600, 800]  # School spirit melody

            for tone in chant_tones:
                if sound_enabled:  # Check each time in case switch changes
                    hardware.play_tone_if_enabled(int(tone), 0.25, sound_enabled)
                    time.sleep(0.1)

            print(
                "[UFO AI] 📣 Random %s chant!" % self.college_manager.get_college_name())

        except Exception as e:
            print("[UFO AI] Random chant error: %s" % str(e))

    def detect_college_chant(self, np_samples):
        """Detect college-specific chant patterns in audio."""
        if not self.college_spirit_enabled or not self.college_manager.is_enabled():
            return False

        current_time = time.monotonic()
        if current_time - self.last_college_trigger < self.college_cooldown:
            return False

        if current_time - self._last_college_check < 0.5:
            return False

        self._last_college_check = current_time

        try:
            chant_data = self.college_manager.get_chant_data()
            if not chant_data or len(np_samples) < 100:
                return False

            # Validate required chant data fields
            if "frequency_range" not in chant_data:
                print(
                    "[UFO AI] Error: Missing frequency_range in %s chant data" % self.college_manager.get_college_name())
                return False

            if "energy_threshold" not in chant_data:
                print(
                    "[UFO AI] Error: Missing energy_threshold in %s chant data" % self.college_manager.get_college_name())
                return False

            # Calculate audio energy in target frequency range
            target_freq_range = chant_data["frequency_range"]
            if not isinstance(target_freq_range, list) or len(target_freq_range) != 2:
                print(
                    "[UFO AI] Error: Invalid frequency_range format in %s chant data" % self.college_manager.get_college_name())
                return False

            min_freq, max_freq = target_freq_range

            # Simple frequency analysis
            sample_rate = 22050
            samples_per_freq = len(np_samples) / (sample_rate / 2)

            start_idx = int(min_freq * samples_per_freq)
            end_idx = int(max_freq * samples_per_freq)
            start_idx = max(0, min(start_idx, len(np_samples) - 1))
            end_idx = max(start_idx + 1, min(end_idx, len(np_samples)))

            if end_idx <= start_idx:
                return False

            # Calculate energy in the target range
            target_energy = 0.0
            total_energy = 0.0

            for i in range(len(np_samples)):
                sample_energy = float(np_samples[i] * np_samples[i])
                total_energy += sample_energy

                if start_idx <= i < end_idx:
                    target_energy += sample_energy

            if total_energy == 0.0:
                return False

            # Check if the target frequency has a high enough proportion
            energy_ratio = target_energy / total_energy
            threshold = float(chant_data["energy_threshold"])

            # Also check the minimum volume threshold
            avg_amplitude = (total_energy / len(np_samples)) ** 0.5
            min_volume = float(chant_data.get("min_volume", 500))

            chant_detected = (energy_ratio > threshold and
                              avg_amplitude > min_volume)

            if chant_detected:
                self.last_college_trigger = current_time
                print("[UFO AI] 🏈 CHANT DETECTED! %s spirit activated!" %
                      self.college_manager.get_college_name())
                return True

        except KeyError as e:
            print("[UFO AI] Missing chant data field: %s" % str(e))
        except (IndexError, ZeroDivisionError, TypeError) as e:
            print("[UFO AI] Chant detection error: %s" % str(e))
        except Exception as e:
            print("[UFO AI] Unexpected chant detection error: %s" % str(e))

        return False

    def execute_college_celebration(self, hardware, sound_enabled):
        """Execute college celebration sequence."""
        if not self.college_spirit_enabled:
            return

        print(
            "[UFO AI] 🎉 %s celebration mode!" % self.college_manager.get_college_name())

        # Celebration sequence
        self._play_chant(hardware, sound_enabled)
        self._college_light_show(hardware)
        self._play_fight_song(hardware, sound_enabled)

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

            print("[UFO AI] DEBUG: college_data exists: %s" % (
                        self.college_manager.college_data is not None))

            if self.college_manager.college_data:
                print("[UFO AI] DEBUG: college_data keys: %s" % list(
                    self.college_manager.college_data.keys()))

                if 'chants' in self.college_manager.college_data:
                    print("[UFO AI] DEBUG: chants data: %s" %
                          self.college_manager.college_data['chants'])

                    if 'primary' in self.college_manager.college_data['chants']:
                        chant_primary = self.college_manager.college_data['chants'][
                            'primary']
                        print("[UFO AI] DEBUG: primary chant data: %s" % chant_primary)

                        if 'bpm' in chant_primary:
                            bpm = chant_primary['bpm']
                            print("[UFO AI] DEBUG: Retrieved BPM: %d" % bpm)
                        else:
                            print("[UFO AI] DEBUG: No 'bpm' key in primary chant data")
                    else:
                        print("[UFO AI] DEBUG: No 'primary' key in chants")
                else:
                    print("[UFO AI] DEBUG: No 'chants' key in college_data")
            else:
                print("[UFO AI] DEBUG: college_data is None")

            print("[UFO AI] Using chant BPM: %d" % bpm)

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

            # Phase 1: Opening fanfare - expanding rings
            for ring_cycle in range(3):
                primary_color = tuple(self.college_primary)
                secondary_color = tuple(self.college_secondary)

                # Expanding ring from the center
                hardware.clear_pixels()
                for ring in range(5):
                    start_pos = 5 - ring
                    end_pos = 5 + ring
                    for i in range(max(0, start_pos), min(10, end_pos)):
                        hardware.pixels[
                            i] = primary_color if ring_cycle % 2 == 0 else secondary_color
                    hardware.pixels.show()
                    time.sleep(0.1)

                time.sleep(0.2)

            # Phase 2: Alternating wave pattern
            for wave_cycle in range(6):
                primary_color = tuple(self.college_primary)
                secondary_color = tuple(self.college_secondary)

                # Wave going right
                for pos in range(12):  # Go beyond 10 to clear
                    hardware.clear_pixels()
                    for i in range(3):  # 3-pixel wave
                        pixel_pos = (pos - i) % 10
                        if 0 <= pixel_pos < 10:
                            color = primary_color if wave_cycle % 2 == 0 else secondary_color
                            intensity = 1.0 - (i * 0.3)  # Fade trail
                            adjusted_color = tuple(int(c * intensity) for c in color)
                            hardware.pixels[pixel_pos] = adjusted_color
                    hardware.pixels.show()
                    time.sleep(0.08)

                # Brief pause between waves
                time.sleep(0.1)

            # Phase 3: Pulsing celebration
            for pulse_cycle in range(8):
                primary_color = tuple(self.college_primary)
                secondary_color = tuple(self.college_secondary)

                # Pulse all pixels with both colors
                for intensity in [0.2, 0.5, 0.8, 1.0, 0.8, 0.5, 0.2]:
                    color = primary_color if pulse_cycle % 2 == 0 else secondary_color
                    adjusted_color = tuple(int(c * intensity) for c in color)

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
                primary_color = tuple(self.college_primary)
                secondary_color = tuple(self.college_secondary)

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
            finale_colors = [tuple(self.college_primary), tuple(self.college_secondary)]

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
            primary_color = tuple(self.college_primary)
            for i in range(10):
                hardware.pixels[i] = primary_color
            hardware.pixels.show()
            time.sleep(1.0)

            # Fade out slowly
            for fade_step in range(10, 0, -1):
                fade_intensity = fade_step / 10.0
                faded_color = tuple(int(c * fade_intensity) for c in primary_color)
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

    def get_college_behavior_modifier(self, base_mood):
        """Modify behavior based on college spirit level."""
        if not self.college_spirit_enabled:
            return base_mood

        # Higher school spirit makes UFO more energetic
        if self.school_spirit > 70:
            if base_mood == "neutral":
                return "excited"
            elif base_mood == "calm":
                return "neutral"

        return base_mood

    def update_school_spirit(self, interaction_success=False):
        """Update school spirit based on interactions."""
        if not self.college_spirit_enabled:
            return

        if interaction_success:
            self.school_spirit = min(100, self.school_spirit + 5)
        else:
            # Slow decay when no college interactions
            self.school_spirit = max(30, int(self.school_spirit - 0.1))

    def get_college_colors(self):
        """Get college colors for display."""
        return self.college_primary, self.college_secondary

    def is_college_celebration_ready(self):
        """Check if enough time has passed for another college celebration."""
        current_time = time.monotonic()
        return (current_time - self.last_college_trigger) >= self.college_cooldown
