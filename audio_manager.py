"""
Audio Manager for Tomb Bound
Handles all audio-related functionality including background music and sound effects
"""

import pygame
import os
import time

class AudioManager:
    def __init__(self):
        """Initialize the audio manager"""
        self.sounds = {}
        self.music_file = None
        self.music_volume = 0.5
        self.sound_volume = 0.7
        self.music_enabled = True  # Default music to ON
        self.sound_enabled = True
        
        # Try to initialize the mixer
        self.audio_available = False
        try:
            pygame.mixer.init()
            self.audio_available = True
            print("Audio system initialized successfully")
        except pygame.error as e:
            print(f"Audio system initialization failed: {e}")
            print("Game will run without sound")
            return
            
        # Load background music
        self.load_music()
        
        # Load sound effects
        self.load_sounds()
    
    def load_music(self):
        """Load background music from the audio directory"""
        if not self.audio_available:
            return
            
        # Look for background music file in the audio directory
        if os.path.exists('audio'):
            bgm_path = os.path.join('audio', 'gamebgm.mp3')
            if os.path.exists(bgm_path):
                self.music_file = bgm_path
                print(f"Background music loaded: {self.music_file}")
            else:
                print("Background music file 'gamebgm.mp3' not found")
        
        if not self.music_file:
            print("No background music found in audio directory")
    
    def load_sounds(self):
        """Load sound effects from the audio directory"""
        if not self.audio_available:
            return
        
        # Create sound categories
        self.sound_categories = {
            'menu': {},    # Menu navigation sounds
            'player': {},  # Player action sounds
            'game': {}     # Game event sounds
        }
        
        # Load hurt sound (when player collides with trap)
        hurt_path = os.path.join('audio', 'hurtsound.mp3')
        if os.path.exists(hurt_path):
            try:
                self.sound_categories['game']['hurt'] = pygame.mixer.Sound(hurt_path)
                self.sound_categories['game']['hurt'].set_volume(self.sound_volume)
                print(f"Hurt sound loaded: {hurt_path}")
            except pygame.error as e:
                print(f"Could not load hurt sound: {e}")
        
        # Jump sound removed as per requirements
        
        # Load death sound (when player loses all health)
        death_path = os.path.join('audio', 'mandeathsound.mp3')
        if os.path.exists(death_path):
            try:
                self.sound_categories['game']['death'] = pygame.mixer.Sound(death_path)
                self.sound_categories['game']['death'].set_volume(self.sound_volume)
                print(f"Death sound loaded: {death_path}")
            except pygame.error as e:
                print(f"Could not load death sound: {e}")
        
        # Load game over sound
        game_over_path = os.path.join('audio', 'gameover.mp3')
        if os.path.exists(game_over_path):
            try:
                self.sound_categories['game']['game_over'] = pygame.mixer.Sound(game_over_path)
                self.sound_categories['game']['game_over'].set_volume(self.sound_volume)
                print(f"Game over sound loaded: {game_over_path}")
            except pygame.error as e:
                print(f"Could not load game over sound: {e}")
                
        # Load menu sounds
        # Click sound removed as per requirements
        
        # Hover sound removed as per requirements
        
        # For backward compatibility, create a flat dictionary of all sounds
        self.sounds = {}
        for category in self.sound_categories:
            for sound_name, sound in self.sound_categories[category].items():
                self.sounds[sound_name] = sound
    
    def play_music(self):
        """Start playing background music in a loop"""
        if not self.audio_available or not self.music_file or not self.music_enabled:
            return
            
        try:
            pygame.mixer.music.load(self.music_file)
            pygame.mixer.music.set_volume(self.music_volume)
            pygame.mixer.music.play(-1)  # -1 means loop indefinitely
            print("Background music started")
        except pygame.error as e:
            print(f"Could not play background music: {e}")
    
    def stop_music(self):
        """Stop the background music"""
        if not self.audio_available:
            return
            
        try:
            pygame.mixer.music.stop()
            print("Background music stopped")
        except pygame.error as e:
            print(f"Error stopping music: {e}")
    
    def pause_music(self):
        """Pause the background music"""
        if not self.audio_available:
            return
            
        try:
            pygame.mixer.music.pause()
        except pygame.error:
            pass
    
    def unpause_music(self):
        """Unpause the background music"""
        if not self.audio_available:
            return
            
        try:
            pygame.mixer.music.unpause()
        except pygame.error:
            pass
    
    def play_sound(self, sound_name, category=None):
        """Play a sound effect by name, optionally from a specific category"""
        if not self.audio_available or not self.sound_enabled:
            return
        
        # If category is specified, try to play from that category
        if category and category in self.sound_categories:
            if sound_name in self.sound_categories[category]:
                try:
                    self.sound_categories[category][sound_name].play()
                    return
                except pygame.error:
                    pass
        
        # Fall back to flat dictionary if category not specified or sound not found in category
        if sound_name in self.sounds:
            try:
                self.sounds[sound_name].play()
            except pygame.error:
                pass
    
    def toggle_music(self):
        """Toggle background music on/off"""
        if not self.audio_available:
            return
            
        self.music_enabled = not self.music_enabled
        
        if self.music_enabled:
            self.play_music()
        else:
            self.stop_music()
        
        return self.music_enabled
    
    def toggle_sound(self):
        """Toggle sound effects on/off"""
        if not self.audio_available:
            return
            
        self.sound_enabled = not self.sound_enabled
        return self.sound_enabled
    
    def set_music_volume(self, volume):
        """Set music volume (0.0 to 1.0)"""
        if not self.audio_available:
            return
            
        self.music_volume = max(0.0, min(1.0, volume))
        try:
            pygame.mixer.music.set_volume(self.music_volume)
        except pygame.error:
            pass
    
    def set_sound_volume(self, volume):
        """Set sound effects volume (0.0 to 1.0)"""
        if not self.audio_available:
            return
            
        self.sound_volume = max(0.0, min(1.0, volume))
        
        for sound in self.sounds.values():
            try:
                sound.set_volume(self.sound_volume)
            except pygame.error:
                pass

# Create a global instance for easy importing
audio_manager = None

def initialize():
    """Initialize the audio manager"""
    global audio_manager
    audio_manager = AudioManager()
    return audio_manager

def get_instance():
    """Get the audio manager instance, creating it if necessary"""
    global audio_manager
    if audio_manager is None:
        audio_manager = AudioManager()
    return audio_manager
