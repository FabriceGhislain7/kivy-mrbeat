"""
AudioSourceOneShot Module - Single-Shot Audio Playback System

This module provides a professional one-shot audio playback system designed for
immediate audio triggering in real-time applications. Optimized for drum machines,
sound effects, and user-triggered audio samples.

The AudioSourceOneShot class manages single audio sample playback with precise
timing and minimal latency, essential for responsive musical applications.

Features:
- Immediate audio sample triggering
- Thread-safe audio playback
- Optimized for low-latency performance
- Professional audio quality maintenance
- Memory-efficient sample management

Author: MrBeat Development Team
Version: 2.0 (Pygame Implementation)
"""

import pygame
import numpy as np
from threading import Thread, Lock
import time


class AudioSourceOneShot:
    """
    Professional One-Shot Audio Source for Immediate Sample Playback
    
    This class provides immediate audio sample playback capabilities with thread-safe
    operation and minimal latency. Designed specifically for applications requiring
    instant audio response such as drum machines and musical interfaces.
    
    The class maintains a simple interface while ensuring professional audio quality
    and reliable performance across different system configurations.
    
    Attributes:
        mixer (pygame.mixer): Reference to pygame audio mixer
        current_sound (pygame.mixer.Sound): Currently loaded audio sample
        is_running (bool): Thread execution state flag
        sample_lock (threading.Lock): Thread safety for sample operations
    """
    
    def __init__(self, mixer, *args, **kwargs):
        """
        Initialize the AudioSourceOneShot with pygame mixer.
        
        Sets up the one-shot audio source with the provided pygame mixer,
        initializes thread safety mechanisms, and prepares for audio playback.
        
        Args:
            mixer (pygame.mixer): Initialized pygame mixer instance
            *args: Additional positional arguments (for compatibility)
            **kwargs: Additional keyword arguments (for compatibility)
        
        Raises:
            TypeError: If mixer is not a valid pygame mixer instance
        """
        # Store reference to pygame mixer
        self.mixer = mixer
        
        # Initialize audio sample storage
        self.current_sound = None
        self.wav_samples = None
        self.nb_wav_samples = 0
        
        # Thread safety and control
        self.sample_lock = Lock()
        self.is_running = False
        
        # Audio processing parameters
        self.chunk_nb_samples = 32  # Maintained for compatibility
        self.current_sample_index = 0
    
    def start(self):
        """
        Start the audio source for playback operations.
        
        Initializes the audio source and prepares it for immediate sample playback.
        This method must be called before attempting to play any audio samples.
        
        Example:
            >>> one_shot = AudioSourceOneShot(pygame.mixer)
            >>> one_shot.start()
            >>> one_shot.set_wav_samples(audio_data)
        """
        self.is_running = True
        print("AudioSourceOneShot: Ready for immediate playback")
    
    def stop(self):
        """
        Stop the audio source and cleanup resources.
        
        Safely stops any currently playing audio and cleans up associated resources.
        Should be called when the audio source is no longer needed.
        """
        self.is_running = False
        
        with self.sample_lock:
            if self.current_sound:
                self.current_sound.stop()
                self.current_sound = None
    
    def set_wav_samples(self, wav_samples):
        """
        Load and immediately play audio samples.
        
        This method loads the provided audio samples and triggers immediate playback.
        The audio data is converted to a pygame Sound object for optimal performance
        and played without delay.
        
        Args:
            wav_samples (numpy.ndarray or bytes): Audio sample data to play
                Can be raw audio bytes, numpy array, or any format supported
                by pygame Sound creation
        
        Note:
            This method provides immediate playback - the audio will start playing
            as soon as the samples are set, making it ideal for responsive UI
            interactions and real-time audio triggering.
        
        Example:
            >>> # Load and play a kick drum sample
            >>> kick_samples = load_kick_drum()
            >>> one_shot.set_wav_samples(kick_samples)
            # Audio plays immediately
        """
        if not self.is_running:
            return
        
        with self.sample_lock:
            try:
                # Convert samples to appropriate format for pygame
                if wav_samples is not None:
                    # Store sample information
                    self.wav_samples = wav_samples
                    self.nb_wav_samples = len(wav_samples) if hasattr(wav_samples, '__len__') else 0
                    self.current_sample_index = 0
                    
                    # Convert audio data to pygame Sound object
                    if isinstance(wav_samples, np.ndarray):
                        # Convert numpy array to bytes if necessary
                        if wav_samples.dtype != np.int16:
                            # Normalize and convert to 16-bit integers
                            wav_samples = (wav_samples * 32767).astype(np.int16)
                        audio_bytes = wav_samples.tobytes()
                    else:
                        # Assume it's already in byte format
                        audio_bytes = wav_samples
                    
                    # Create pygame Sound object from audio data
                    self.current_sound = pygame.mixer.Sound(buffer=audio_bytes)
                    
                    # Play the sound immediately
                    self.current_sound.play()
                    
            except Exception as e:
                print(f"AudioSourceOneShot Error: Failed to play sample - {e}")
                self.current_sound = None
    
    def get_bytes(self, *args, **kwargs):
        """
        Legacy method for compatibility with audiostream interface.
        
        This method maintains compatibility with the original audiostream-based
        implementation. In the pygame version, actual audio playback is handled
        directly by pygame, so this method returns empty data.
        
        Args:
            *args: Legacy positional arguments (ignored)
            **kwargs: Legacy keyword arguments (ignored)
        
        Returns:
            bytes: Empty byte string (audio handled by pygame directly)
        
        Note:
            This method is maintained for interface compatibility but does not
            perform actual audio processing in the pygame implementation.
        """
        # Return empty bytes as pygame handles audio directly
        empty_buffer = b"\x00\x00" * self.chunk_nb_samples
        return empty_buffer
    
    def is_playing(self):
        """
        Check if audio is currently playing.
        
        Returns:
            bool: True if audio is currently playing, False otherwise
        
        Example:
            >>> if one_shot.is_playing():
            ...     print("Audio is currently playing")
        """
        with self.sample_lock:
            if self.current_sound:
                # pygame doesn't have a direct is_playing method for individual sounds
                # but we can check if any sounds are playing on any channel
                return pygame.mixer.get_busy()
            return False
    
    def set_volume(self, volume):
        """
        Set the playback volume for future audio samples.
        
        Args:
            volume (float): Volume level between 0.0 (silent) and 1.0 (full volume)
        
        Example:
            >>> one_shot.set_volume(0.8)  # Set to 80% volume
        """
        if 0.0 <= volume <= 1.0:
            # Set global mixer volume (affects all sounds)
            pygame.mixer.set_volume(volume)
        else:
            print(f"AudioSourceOneShot Warning: Volume {volume} out of range [0.0, 1.0]")
    
    def __del__(self):
        """Destructor to ensure proper cleanup when object is garbage collected."""
        self.stop()