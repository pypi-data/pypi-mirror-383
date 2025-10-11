"""Preferences Manager - persists user preferences."""

import json
from pathlib import Path
from typing import Optional


class PreferencesManager:
    """Manages user preferences persistence."""
    
    def __init__(self):
        """Initialize preferences manager."""
        self.prefs_file = Path.home() / '.vera_syntaxis_prefs.json'
        self.preferences = self._load_preferences()
    
    def _load_preferences(self) -> dict:
        """
        Load preferences from file.
        
        Returns:
            Dictionary of preferences
        """
        if self.prefs_file.exists():
            try:
                with open(self.prefs_file, 'r') as f:
                    return json.load(f)
            except:
                pass
        
        return {
            'last_folder': None,
            'window_geometry': '1200x800',
            'theme': 'flatly'
        }
    
    def _save_preferences(self):
        """Save preferences to file."""
        try:
            with open(self.prefs_file, 'w') as f:
                json.dump(self.preferences, f, indent=2)
        except:
            pass
    
    def get_last_folder(self) -> Optional[Path]:
        """
        Get the last opened folder.
        
        Returns:
            Path to last folder or None
        """
        folder = self.preferences.get('last_folder')
        return Path(folder) if folder else None
    
    def set_last_folder(self, folder: Path):
        """
        Save the last opened folder.
        
        Args:
            folder: Path to folder
        """
        self.preferences['last_folder'] = str(folder)
        self._save_preferences()
    
    def get_window_geometry(self) -> str:
        """Get saved window geometry."""
        return self.preferences.get('window_geometry', '1200x800')
    
    def set_window_geometry(self, geometry: str):
        """Save window geometry."""
        self.preferences['window_geometry'] = geometry
        self._save_preferences()
