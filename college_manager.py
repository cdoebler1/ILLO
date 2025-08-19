# Charles Doebler at Feral Cat AI

import json

class CollegeManager:
    def __init__(self, college_name="none"):
        self.college_name = college_name
        self.college_data = None
        self.load_college_data()
    
    def load_college_data(self):
        """Load college-specific data from JSON file."""
        if self.college_name == "none":
            self.college_data = None
            return
            
        try:
            file_path = 'colleges/{}.json'.format(self.college_name)
            with open(file_path, 'r') as f:
                self.college_data = json.load(f)
        except (OSError, ValueError) as e:
            print("[COLLEGE] ❌ Could not load college data: {}".format(str(e)))
            self.college_data = None
    
    def is_enabled(self):
        """Check if college spirit is enabled and loaded."""
        return self.college_data is not None
    
    def get_colors(self):
        """Get college colors."""
        if not self.college_data:
            return {"primary": [255, 255, 255], "secondary": [128, 128, 128]}
        return self.college_data["colors"]
    
    def get_chant_data(self):
        """Get chant detection parameters."""
        if not self.college_data:
            return None
        
        if "chants" not in self.college_data:
            return None
            
        if "primary" not in self.college_data["chants"]:
            return None
            
        chant_data = self.college_data["chants"]["primary"]
        return chant_data
    
    def get_fight_song_notes(self):
        """Get fight song note sequence."""
        if not self.college_data:
            return []
        return self.college_data["fight_song"]["notes"]
    
    def get_response_tone(self, tone_type="chant_response"):
        """Get audio tone for specific response type."""
        if not self.college_data:
            return [200, 0.3]  # Default tone
        return self.college_data["audio_tones"].get(tone_type, [200, 0.3])
    
    def get_college_name(self):
        """Get full college name."""
        if not self.college_data:
            return "Generic"
        return self.college_data["name"]

    def get_chant_notes(self):
        """Get chant note sequence."""
        if not self.college_data:
            return []
        
        if "chants" not in self.college_data:
            return []
            
        if "primary" not in self.college_data["chants"]:
            return []
        
        chant_data = self.college_data["chants"]["primary"]
        return chant_data.get("notes", [])
