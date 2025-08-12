# Charles Doebler at Feral Cat AI
# Shared audio processing utilities for UFO routines

from ulab import numpy as np
from adafruit_circuitplayground.bluefruit import cpb
import array

# Audio processing constants
SAMPLE_RATE = 16000  # Audio sampling rate for microphone input
SAMPLES = 1024       # Number of audio samples to process
THRESHOLD = 100      # Microphone sensitivity threshold
MIN_DELTAS = 5       # Minimum audio events needed for visualization
FREQ_LOW = 200       # Low frequency range
FREQ_HIGH = 3000     # High frequency range

# Global audio setup
samples = array.array("H", [0] * (SAMPLES + 6))
mic = cpb._mic

class AudioProcessor:
    @staticmethod
    def record_samples():
        """Record samples from the microphone."""
        mic.record(samples, SAMPLES)
        return np.array(samples[3:-3])

    @staticmethod
    def compute_deltas(np_samples):
        """Compute deltas between mean crossing points."""
        mean = int(np.mean(np_samples) + 0.5)
        threshold = mean + THRESHOLD
        new_deltas = []
        last_xing_point = None
        crossed_threshold = False
        
        for ii, sample in enumerate(np_samples[:-1]):
            if sample > threshold:
                crossed_threshold = True
            if crossed_threshold and sample < mean:
                if last_xing_point is not None:
                    new_deltas.append(ii - last_xing_point)
                last_xing_point = ii
                crossed_threshold = False
        
        return new_deltas

    @staticmethod
    def calculate_frequency(deltas):
        """Calculate frequency from deltas."""
        if len(deltas) < MIN_DELTAS:
            return None
        return SAMPLE_RATE / (sum(deltas) / len(deltas))
