# Charles Doebler at Feral Cat AI  
# Chant Detection System - Rolling buffer for multi-second pattern matching

import time
# import numpy as np


class ChantDetector:
    def __init__(self, college_manager):
        self.college_manager = college_manager
        self.last_detection_time = 0.0
        self.detection_cooldown = 15.0  # Seconds between detections
        self.last_check_time = 0.0
        self.sample_rate = 22050
        
        # Detection state
        self.is_enabled = True
        
        # Rolling buffer for 3-4 second chant detection
        self.audio_buffer = []
        self.max_buffer_size = 50  # ~4 seconds at 80ms per clip
        self.chant_analysis_window = 35  # Analyze last 35 clips (~2.8 seconds)
        
        # Pattern detection state
        self.recent_energy_pattern = []
        self.silence_gaps = []

    def set_enabled(self, enabled):
        """Enable or disable chant detection."""
        self.is_enabled = enabled
        
    def detect_chant(self, audio_samples):
        """Detect chant using rolling buffer of ~50 clips."""
        if not self.is_enabled or not self.college_manager.is_enabled():
            return False
            
        current_time = time.monotonic()

        # Cooldown and rate limiting
        if current_time - self.last_detection_time < self.detection_cooldown:
            return False
        if current_time - self.last_check_time < 0.1:  # Check every 100ms
            return False
        self.last_check_time = current_time
        
        try:
            # Add new clip to rolling buffer
            self._add_to_buffer(audio_samples, current_time)
            
            # Need sufficient clips for pattern analysis
            if len(self.audio_buffer) < self.chant_analysis_window:
                return False
                
            chant_data = self.college_manager.get_chant_data()
            if not chant_data:
                return False
                
            # Analyze the pattern in recent clips
            if self._analyze_chant_sequence(chant_data):
                self.last_detection_time = current_time
                print("[ChantDetector] 🏈 CHANT SEQUENCE DETECTED! %s" % 
                      self.college_manager.get_college_name())
                return True
                
        except Exception as e:
            print("[ChantDetector] Pattern detection error: %s" % str(e))
            
        return False
        
    def _add_to_buffer(self, audio_samples, timestamp):
        """Add audio clip to rolling buffer with analysis."""
        # Calculate energy and basic features for this clip
        energy = self._calculate_energy(audio_samples)
        is_speech = self._is_likely_speech(audio_samples, energy)
        
        clip_data = {
            'timestamp': timestamp,
            'energy': energy,
            'is_speech': is_speech,
            'duration': len(audio_samples) / self.sample_rate  # Actual duration
        }
        
        self.audio_buffer.append(clip_data)
        
        # Maintain buffer size (memory constraint)
        if len(self.audio_buffer) > self.max_buffer_size:
            self.audio_buffer.pop(0)
            
    def _calculate_energy(self, audio_samples):
        """Calculate RMS energy for the clip."""
        if len(audio_samples) == 0:
            return 0.0
        return (sum(s * s for s in audio_samples) / len(audio_samples)) ** 0.5
        
    def _is_likely_speech(self, audio_samples, energy):
        """Simple speech detection based on energy and zero crossings."""
        if energy < 100:  # Too quiet for speech
            return False
            
        # Count zero crossings (speech has more than pure tones)
        zero_crossings = 0
        for i in range(1, min(len(audio_samples), 500)):  # Limit for speed
            if (audio_samples[i-1] >= 0) != (audio_samples[i] >= 0):
                zero_crossings += 1
                
        # Speech typically has 10-50 zero crossings per 100 samples
        crossing_rate = (zero_crossings / min(len(audio_samples), 500)) * 100
        return 8 <= crossing_rate <= 60
        
    def _analyze_chant_sequence(self, chant_data):
        """
        Analyze recent buffer for 'We Are Penn State' pattern.
        
        Expected pattern over ~3 seconds:
        - High energy burst: "WE" (~0.3s) 
        - Brief gap (~0.2s)
        - High energy burst: "ARE" (~0.3s)
        - Longer gap (~0.8s) 
        - High energy burst: "PENN STATE" (~0.8s)
        """
        if len(self.audio_buffer) < self.chant_analysis_window:
            return False
            
        # Analyze the most recent window
        recent_clips = self.audio_buffer[-self.chant_analysis_window:]
        
        # Get energy and speech pattern over time
        energy_pattern = [clip['energy'] for clip in recent_clips]
        speech_pattern = [clip['is_speech'] for clip in recent_clips]
        
        # Find energy peaks that could be words
        energy_peaks = self._find_energy_peaks(energy_pattern, speech_pattern)
        
        if len(energy_peaks) < 2:  # Need at least 2 peaks for "WE ARE" or "PENN STATE"
            return False
            
        # Check if peak timing matches "We Are ... Penn State" pattern
        return self._matches_chant_timing(energy_peaks, recent_clips, chant_data)
        
    def _find_energy_peaks(self, energy_pattern, speech_pattern):
        """Find significant energy peaks that contain speech."""
        min_energy = 200  # Minimum energy for shouting
        peaks = []
        
        i = 0
        while i < len(energy_pattern):
            if energy_pattern[i] > min_energy and speech_pattern[i]:
                # Found start of potential word
                peak_start = i
                peak_energy = energy_pattern[i]
                
                # Find extent of this energy burst
                while (i < len(energy_pattern) and 
                       energy_pattern[i] > min_energy * 0.6 and  # Allow some variation
                       speech_pattern[i]):
                    peak_energy = max(peak_energy, energy_pattern[i])
                    i += 1
                    
                peaks.append({
                    'start_idx': peak_start,
                    'end_idx': i - 1,
                    'duration': (i - peak_start) * 0.08,  # Assume 80ms per clip
                    'max_energy': peak_energy
                })
            else:
                i += 1
                
        return peaks
        
    def _matches_chant_timing(self, peaks, clips, chant_data):
        """Check if energy peaks match expected 'We Are Penn State' timing."""
        if len(peaks) < 2:
            return False
            
        # Get timing parameters from config
        min_word_energy = float(chant_data.get("min_energy", 300))
        expected_gaps = chant_data.get("timing_gaps", [0.2, 0.8])  # Seconds between words
        
        # Check that peaks have sufficient energy
        if not all(peak['max_energy'] > min_word_energy for peak in peaks):
            return False
            
        # For "We Are ... Penn State", expect specific timing patterns:
        if len(peaks) >= 3:
            # Three clear peaks: "WE", "ARE", "PENN STATE"
            gap1 = (peaks[1]['start_idx'] - peaks[0]['end_idx']) * 0.08
            gap2 = (peaks[2]['start_idx'] - peaks[1]['end_idx']) * 0.08
            
            # "We Are" should be close together, then gap, then "Penn State"
            if 0.1 <= gap1 <= 0.5 and 0.4 <= gap2 <= 1.2:
                return True
                
        elif len(peaks) == 2:
            # Two peaks: "WE ARE" and "PENN STATE" 
            gap = (peaks[1]['start_idx'] - peaks[0]['end_idx']) * 0.08
            
            # Should be separated by pause
            if 0.3 <= gap <= 1.5:
                # Check duration - "PENN STATE" should be longer
                if peaks[1]['duration'] > peaks[0]['duration'] * 1.2:
                    return True
                    
        return False
        
    def get_buffer_status(self):
        """Debug info about current buffer state."""
        return {
            'buffer_size': len(self.audio_buffer),
            'duration_seconds': len(self.audio_buffer) * 0.08,
            'recent_speech_clips': sum(1 for clip in self.audio_buffer[-10:] if clip['is_speech']),
            'avg_recent_energy': sum(clip['energy'] for clip in self.audio_buffer[-5:]) / min(5, len(self.audio_buffer))
        }
