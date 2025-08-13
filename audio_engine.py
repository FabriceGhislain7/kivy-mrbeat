"""
AudioEngine Module - Professional Audio Processing System

This module provides a comprehensive audio engine built on pygame for real-time 
audio playback, mixing, and beat generation. It serves as the core audio processing
component for the MrBeat drum machine application.

Features:
- High-quality audio playback with configurable parameters
- Real-time audio mixing capabilities
- Track-based beat sequencing
- One-shot audio sample triggering
- Professional audio standards compliance

Dependencies:
    - pygame: Core audio functionality
    - numpy: Audio data processing
    - Custom audio source modules for specialized audio handling

Author: MrBeat Development Team
Version: 2.0 (Pygame Implementation)
"""

import pygame
import numpy as np
from threading import Thread
import time

# Import custom audio source modules
from audio_source_mixer import AudioSourceMixer
from audio_source_one_shot import AudioSourceOneShot
from audio_source_track import AudioSourceTrack


class AudioEngine:
    """
    Professional Audio Engine for Real-time Audio Processing
    
    This class manages all audio operations including initialization of the audio
    subsystem, creation of audio sources, and coordination of audio playback.
    Built on pygame for cross-platform compatibility and reliability.
    
    Class Constants:
        NB_CHANNELS (int): Number of audio channels (1 = mono, 2 = stereo)
        SAMPLE_RATE (int): Audio sample rate in Hz (CD quality)
        BUFFER_SIZE (int): Audio buffer size for low-latency playback
    """
    
    # Audio Configuration Constants
    NB_CHANNELS = 1          # Mono audio configuration
    SAMPLE_RATE = 44100      # CD quality sample rate (44.1kHz)
    BUFFER_SIZE = 1024       # Optimized buffer size for low latency
    
    def __init__(self):
        """
        Initialize the AudioEngine with pygame audio subsystem.
        
        Sets up the audio mixer with professional-grade settings and initializes
        the one-shot audio source for immediate audio playback capabilities.
        
        Raises:
            pygame.error: If audio initialization fails
            RuntimeError: If audio sources cannot be created
        """
        # Initialize pygame mixer with professional audio settings
        pygame.mixer.pre_init(
            frequency=self.SAMPLE_RATE,
            size=-16,                    # 16-bit signed audio
            channels=self.NB_CHANNELS,
            buffer=self.BUFFER_SIZE
        )
        pygame.mixer.init()
        
        # Create and start one-shot audio source for immediate playback
        self.audio_source_one_shot = AudioSourceOneShot(pygame.mixer)
        self.audio_source_one_shot.start()
        
        # Store reference to pygame mixer for other audio sources
        self.mixer = pygame.mixer
    
    def play_sound(self, wav_samples):
        """
        Play audio samples immediately through one-shot audio source.
        
        This method triggers immediate playback of provided audio samples,
        typically used for drum hits, sound effects, or user-triggered audio.
        
        Args:
            wav_samples (numpy.ndarray or bytes): Audio sample data to play
                Can be raw audio data or numpy array of audio samples
        
        Example:
            >>> engine = AudioEngine()
            >>> engine.play_sound(kick_drum_samples)
        """
        self.audio_source_one_shot.set_wav_samples(wav_samples)
    
    def create_track(self, wav_samples, bpm):
        """
        Create a new audio track for beat sequencing.
        
        Initializes a track-based audio source that can play samples according
        to a beat pattern at the specified BPM. Each track operates independently
        and can be controlled separately.
        
        Args:
            wav_samples (numpy.ndarray): Audio samples for this track
            bpm (int): Beats per minute for track timing
        
        Returns:
            AudioSourceTrack: Configured and started track instance
        
        Example:
            >>> engine = AudioEngine()
            >>> kick_track = engine.create_track(kick_samples, 120)
            >>> kick_track.set_steps((1, 0, 1, 0))  # Play on beats 1 and 3
        """
        # Create track with pygame mixer and audio parameters
        source_track = AudioSourceTrack(
            self.mixer, 
            wav_samples, 
            bpm, 
            self.SAMPLE_RATE
        )
        
        # Start the track's audio processing thread
        source_track.start()
        
        return source_track
    
    def create_mixer(self, all_wav_samples, bpm, nb_steps, on_current_step_changed, min_bpm):
        """
        Create a comprehensive audio mixer for multi-track sequencing.
        
        Initializes the main audio mixer that handles multiple tracks simultaneously,
        provides step sequencing, and manages tempo changes. This is the core
        component for beat making and pattern sequencing.
        
        Args:
            all_wav_samples (dict): Dictionary mapping track names to sample data
            bpm (int): Initial beats per minute for the mixer
            nb_steps (int): Number of steps in the sequence pattern
            on_current_step_changed (callable): Callback function for step changes
            min_bpm (int): Minimum allowed BPM for tempo control
        
        Returns:
            AudioSourceMixer: Configured and started mixer instance
        
        Example:
            >>> def step_callback(step):
            ...     print(f"Now playing step: {step}")
            >>> 
            >>> samples = {'kick': kick_data, 'snare': snare_data}
            >>> mixer = engine.create_mixer(samples, 120, 16, step_callback, 60)
        """
        # Create comprehensive mixer with all required parameters
        source_mixer = AudioSourceMixer(
            self.mixer,
            all_wav_samples,
            bpm,
            self.SAMPLE_RATE,
            nb_steps,
            on_current_step_changed,
            min_bpm
        )
        
        # Start the mixer's processing thread
        source_mixer.start()
        
        return source_mixer
    
    def cleanup(self):
        """
        Clean up audio resources and shut down the audio engine.
        
        This method should be called when the application is closing to ensure
        proper cleanup of audio resources and prevent memory leaks.
        """
        try:
            # Stop all audio sources if they exist
            if hasattr(self, 'audio_source_one_shot'):
                self.audio_source_one_shot.stop()
            
            # Quit pygame mixer
            pygame.mixer.quit()
        except Exception as e:
            print(f"Warning: Error during audio cleanup: {e}")
    
    def __del__(self):
        """Destructor to ensure cleanup when object is garbage collected."""
        self.cleanup()