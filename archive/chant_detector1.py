
# Charles Doebler at Feral Cat AI
# Chant Detection System - Isolated audio pattern recognition

import time
import numpy as np


class ChantDetector:
    def __init__(self, college_manager):
        self.college_manager = college_manager
        self.last_detection_time = 0.0
        self.detection_cooldown = 15.0  # Seconds between detections
        self.last_check_time = 0.0
        self.sample_rate = 22050
        
        # Detection state
        self.is_enabled = True
        
    def set_enabled(self, enabled):
        """Enable or disable chant detection."""
        self.is_enabled = enabled
        
    def detect_chant(self, audio_samples):
        """
        Detect college-specific chant patterns in audio samples.
        
        Args:
            audio_samples: numpy array of audio samples
            
        Returns:
            bool: True if chant detected, False otherwise
        """
        if not self.is_enabled or not self.college_manager.is_enabled():
            return False
            
        current_time = time.monotonic()
        
        # Cooldown check
        if current_time - self.last_detection_time < self.detection_cooldown:
            return False
            
        # Rate limiting - don't check too frequently
        if current_time - self.last_check_time < 0.5:
            return False
            
        self.last_check_time = current_time
        
        try:
            chant_data = self.college_manager.get_chant_data()
            if not chant_data or len(audio_samples) < 100:
                return False
                
            # Validate chant configuration
            if not self._validate_chant_config(chant_data):
                return False
                
            # Perform the actual detection
            detection_result = self._analyze_audio_for_chant(audio_samples, chant_data)
            
            if detection_result:
                self.last_detection_time = current_time
                print("[ChantDetector] 🏈 CHANT DETECTED! %s spirit activated!" % 
                      self.college_manager.get_college_name())
                return True
                
        except Exception as e:
            print("[ChantDetector] Detection error: %s" % str(e))
            
        return False
        
    def _validate_chant_config(self, chant_data):
        """Validate that chant configuration has required fields."""
        required_fields = ["frequency_range", "energy_threshold"]
        
        for field in required_fields:
            if field not in chant_data:
                print("[ChantDetector] Error: Missing %s in %s chant data" % 
                      (field, self.college_manager.get_college_name()))
                return False
                
        # Validate frequency range format
        freq_range = chant_data["frequency_range"]
        if not isinstance(freq_range, list) or len(freq_range) != 2:
            print("[ChantDetector] Error: Invalid frequency_range format in %s chant data" % 
                  self.college_manager.get_college_name())
            return False
            
        return True
        
    def _analyze_audio_for_chant(self, audio_samples, chant_data):
        """
        Analyze audio samples for chant patterns.
        
        Args:
            audio_samples: numpy array of audio samples
            chant_data: dictionary with chant detection parameters
            
        Returns:
            bool: True if chant pattern detected
        """
        min_freq, max_freq = chant_data["frequency_range"]
        
        # Calculate frequency bin indices
        samples_per_freq = len(audio_samples) / (self.sample_rate / 2)
        start_idx = max(0, int(min_freq * samples_per_freq))
        end_idx = min(len(audio_samples), int(max_freq * samples_per_freq))
        
        if end_idx <= start_idx:
            return False
            
        # Calculate energy distribution
        target_energy, total_energy = self._calculate_energy_distribution(
            audio_samples, start_idx, end_idx)
            
        if total_energy == 0.0:
            return False
            
        # Check energy ratio threshold
        energy_ratio = target_energy / total_energy
        threshold = float(chant_data["energy_threshold"])
        
        # Check volume threshold
        avg_amplitude = (total_energy / len(audio_samples)) ** 0.5
        min_volume = float(chant_data.get("min_volume", 500))
        
        return (energy_ratio > threshold and avg_amplitude > min_volume)
        
    def _calculate_energy_distribution(self, audio_samples, start_idx, end_idx):
        """Calculate energy in target frequency range vs total energy."""
        target_energy = 0.0
        total_energy = 0.0
        
        for i, sample in enumerate(audio_samples):
            sample_energy = float(sample * sample)
            total_energy += sample_energy
            
            if start_idx <= i < end_idx:
                target_energy += sample_energy
                
        return target_energy, total_energy
        
    def get_detection_status(self):
        """Get current detection status for debugging."""
        return {
            'enabled': self.is_enabled,
            'last_detection': self.last_detection_time,
            'cooldown_remaining': max(0, self.detection_cooldown - (time.monotonic() - self.last_detection_time)),
            'college': self.college_manager.get_college_name() if self.college_manager.is_enabled() else 'None'
        }
