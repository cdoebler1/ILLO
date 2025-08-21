# Charles Doebler at Feral Cat AI
# Unified Music Player - Handles both chants and fight songs

import time


class MusicPlayer:
    def __init__(self):
        # Standard note duration mappings (in seconds at 120 BPM)
        self.base_sixteenth_duration = 0.1  # 1/16th note at 120 BPM .063
        
    def play_music(self, hardware, sound_enabled, notes, tempo_bpm, repeat_count=1, music_type="music"):
        """
        Play music with unified timing system - blocking version.
        
        Args:
            hardware: Hardware manager instance
            sound_enabled: Whether sound is enabled
            notes: List of [frequency, duration] pairs where duration is in 16th notes
            tempo_bpm: Beats per minute (quarter note = 1 beat)
            repeat_count: How many times to repeat (1 for fight song, 3 for chant)
            music_type: "chant" or "fight_song" for logging
        """
        if not sound_enabled or not notes:
            return False
            
        try:
            # Calculate actual duration of a 16th note at given BPM
            sixteenth_note_duration = 30.0 / (tempo_bpm * 4)
            
            print("[Music] 🎵 Playing %s at %d BPM (%.3fs per 16th note)" % 
                  (music_type, tempo_bpm, sixteenth_note_duration))
            
            # Set college colors during music playback if this is college music
            if music_type in ["chant", "fight_song"]:
                self._set_college_colors_during_music(hardware)
            
            total_notes_played = 0
            
            for repeat in range(repeat_count):
                if repeat_count > 1:
                    print("[Music] 🎵 %s repetition %d of %d" % (music_type, repeat + 1, repeat_count))
                
                note_count = 0
                for note_data in notes:
                    if not sound_enabled:  # Check if sound was disabled during playback
                        print("[Music] 🔇 Sound disabled at note %d" % (total_notes_played + 1))
                        return False
                    
                    note_count += 1
                    total_notes_played += 1
                    
                    if isinstance(note_data, list) and len(note_data) == 2:
                        freq = int(note_data[0])
                        duration_in_sixteenths = int(note_data[1])
                        
                        # Calculate actual duration in seconds
                        duration_seconds = duration_in_sixteenths * sixteenth_note_duration
                        
                        if freq > 0:  # Play tone
                            hardware.play_tone_if_enabled(freq, duration_seconds, sound_enabled)
                        else:  # Rest - just wait silently
                            time.sleep(duration_seconds)
                        
                        # Small gap between notes (1/32nd note duration)
                        gap_duration = sixteenth_note_duration / 2
                        time.sleep(gap_duration)
                        
                    else:
                        print("[Music] ⚠️ Invalid note format at position %d: %s" % (note_count, note_data))
                        continue
                
                # Pause between repetitions (half a beat)
                if repeat < repeat_count - 1:
                    pause_duration = (60.0 / tempo_bpm) / 2  # Half beat pause
                    time.sleep(pause_duration)
            
            print("[Music] ✅ %s complete - played %d total notes" % (music_type, total_notes_played))
            return True
            
        except Exception as e:
            print("[Music] ❌ Playback error: %s" % str(e))
            return False
    
    def _set_college_colors_during_music(self, hardware):
        """Set simple college colors during music playback."""
        try:
            # Simple college color pattern - blue and white alternating
            college_blue = (4, 30, 66)    # Penn State blue
            college_white = (255, 255, 255)  # White
            
            for i in range(10):
                if i % 2 == 0:
                    hardware.pixels[i] = college_blue
                else:
                    hardware.pixels[i] = college_white
            
            hardware.pixels.show()
        except Exception as e:
            print("[Music] Color error: %s" % str(e))
    
    def play_chant(self, hardware, sound_enabled, notes, tempo_bpm):
        """Play a chant (short, 3 repetitions)."""
        return self.play_music(hardware, sound_enabled, notes, tempo_bpm, 
                             repeat_count=3, music_type="chant")
    
    def play_fight_song(self, hardware, sound_enabled, notes, tempo_bpm):
        """Play a fight song (long, single play)."""
        return self.play_music(hardware, sound_enabled, notes, tempo_bpm, 
                             repeat_count=1, music_type="fight_song")
    
    def play_music_with_lights(self, hardware, sound_enabled, notes, tempo_bpm, 
                              repeat_count=1, music_type="music", light_callback=None):
        """
        Play music with synchronized light callback.
        
        Args:
            hardware: Hardware manager instance
            sound_enabled: Whether sound is enabled
            notes: List of [frequency, duration] pairs where duration is in 16th notes
            tempo_bpm: Beats per minute (quarter note = 1 beat)
            repeat_count: How many times to repeat
            music_type: "chant" or "fight_song" for logging
            light_callback: Function to call for light updates (hardware, beat_count, note_info)
        """
        if not sound_enabled or not notes:
            return False
            
        try:
            # Calculate actual duration of a 16th note at given BPM
            sixteenth_note_duration = 30.0 / (tempo_bpm * 4)
            
            print("[Music] 🎵 Playing %s with lights at %d BPM" % (music_type, tempo_bpm))
            
            total_notes_played = 0
            beat_count = 0
            
            for repeat in range(repeat_count):
                if repeat_count > 1:
                    print("[Music] 🎵 %s repetition %d of %d" % (music_type, repeat + 1, repeat_count))
                
                note_count = 0
                for note_data in notes:
                    if not sound_enabled:
                        print("[Music] 🔇 Sound disabled at note %d" % (total_notes_played + 1))
                        return False
                    
                    note_count += 1
                    total_notes_played += 1
                    
                    if isinstance(note_data, list) and len(note_data) == 2:
                        freq = int(note_data[0])
                        duration_in_sixteenths = int(note_data[1])
                        
                        # Calculate actual duration in seconds
                        duration_seconds = duration_in_sixteenths * sixteenth_note_duration
                        
                        # Call light callback before playing note
                        if light_callback:
                            try:
                                note_info = {
                                    'frequency': freq,
                                    'duration': duration_seconds,
                                    'note_position': note_count,
                                    'repetition': repeat + 1
                                }
                                light_callback(hardware, beat_count, note_info)
                            except Exception as e:
                                print("[Music] Light callback error: %s" % str(e))
                        
                        if freq > 0:  # Play tone
                            hardware.play_tone_if_enabled(freq, duration_seconds, sound_enabled)
                        else:  # Rest - just wait silently
                            time.sleep(duration_seconds)
                        
                        # Update beat count (every 4 sixteenth notes = 1 beat)
                        beat_count += duration_in_sixteenths / 4.0
                        
                        # Small gap between notes
                        gap_duration = sixteenth_note_duration / 2
                        time.sleep(gap_duration)
                        
                    else:
                        print("[Music] ⚠️ Invalid note format at position %d: %s" % (note_count, note_data))
                        continue
                
                # Pause between repetitions
                if repeat < repeat_count - 1:
                    pause_duration = (60.0 / tempo_bpm) / 2
                    time.sleep(pause_duration)
                    beat_count += 0.5  # Half beat pause
            
            print("[Music] ✅ %s with lights complete - played %d total notes" % (music_type, total_notes_played))
            return True
            
        except Exception as e:
            print("[Music] ❌ Playback with lights error: %s" % str(e))
            return False

    @staticmethod
    def convert_duration_to_sixteenths(seconds, tempo_bpm=120):
        """Helper method to convert old duration format to 16th note format."""
        sixteenth_note_duration = 60.0 / (tempo_bpm * 4)
        return int(round(seconds / sixteenth_note_duration))
