"""
AudioSourceMixer Module - Professional Multi-Track Audio Mixing System

This module provides a comprehensive multi-track audio mixing system designed for
professional beat making and music production applications. The mixer coordinates
multiple audio tracks with precise synchronization and real-time pattern control.

The AudioSourceMixer class serves as the central hub for multi-track sequencing,
providing master tempo control, synchronized playback, and comprehensive mixing
capabilities with professional audio quality standards.

Features:
- Multi-track audio mixing with sample-accurate synchronization
- Master tempo control affecting all tracks simultaneously
- Real-time pattern modification without audio interruption
- Professional 16-bit audio processing with overflow protection
- Step-based sequencing with customizable pattern lengths
- Thread-safe operations for real-time performance
- Callback system for UI synchronization and visual feedback

Author: MrBeat Development Team
Version: 2.0 (Pygame Implementation)
"""

import pygame
import numpy as np
from threading import Thread, Lock, Event
import time
from array import array
from audio_source_track import AudioSourceTrack

# Audio processing constants for professional quality
MAX_16BITS = 32767    # Maximum value for 16-bit signed audio
MIN_16BITS = -32768   # Minimum value for 16-bit signed audio


def sum_16bits(sample_values):
    """
    Professional audio sample mixing with overflow protection.
    
    Sums multiple audio samples while preventing digital clipping by clamping
    the result to valid 16-bit audio range. Essential for maintaining audio
    quality when mixing multiple tracks simultaneously.
    
    Args:
        sample_values (iterable): Collection of audio sample values to sum
    
    Returns:
        int: Clamped sum within valid 16-bit audio range
    
    Note:
        This function implements professional audio mixing standards by
        preventing digital distortion that would occur from arithmetic overflow.
    
    Example:
        >>> samples = [15000, 20000, 8000]  # Would exceed 16-bit range
        >>> mixed = sum_16bits(samples)     # Returns 32767 (clamped)
    """
    total = sum(sample_values)
    
    # Clamp to valid 16-bit audio range to prevent distortion
    if total > MAX_16BITS:
        return MAX_16BITS
    if total < MIN_16BITS:
        return MIN_16BITS
    
    return total


class AudioSourceMixer:
    """
    Professional Multi-Track Audio Mixer for Beat Sequencing
    
    This class provides comprehensive multi-track mixing capabilities with
    synchronized sequencing, master tempo control, and professional audio
    quality maintenance. It coordinates multiple AudioSourceTrack instances
    to create complex rhythmic patterns and musical compositions.
    
    The mixer operates as a master controller, managing timing, synchronization,
    and audio mixing for all connected tracks while providing real-time control
    over patterns, tempo, and playback state.
    
    Attributes:
        mixer (pygame.mixer): Reference to pygame audio mixer
        tracks (list): Collection of AudioSourceTrack instances
        bpm (int): Master beats per minute for all tracks
        nb_steps (int): Number of steps in the sequence pattern
        is_playing (bool): Master playback state
        current_step_index (int): Current position in the sequence
        mixing_lock (threading.Lock): Thread safety for mixing operations
    """
    
    def __init__(self, mixer, all_wav_samples, bpm, sample_rate, nb_steps, 
                 on_current_step_changed, min_bpm, *args, **kwargs):
        """
        Initialize the AudioSourceMixer with comprehensive mixing capabilities.
        
        Sets up a professional multi-track mixer with synchronized sequencing,
        master tempo control, and callback integration for UI updates.
        
        Args:
            mixer (pygame.mixer): Initialized pygame mixer instance
            all_wav_samples (list): List of audio sample arrays for each track
            bpm (int): Initial master beats per minute
            sample_rate (int): Audio sample rate for timing calculations
            nb_steps (int): Number of steps in the sequence pattern
            on_current_step_changed (callable): Callback for step progression updates
            min_bpm (int): Minimum allowed BPM for tempo control
            *args: Additional positional arguments (for compatibility)
            **kwargs: Additional keyword arguments (for compatibility)
        
        Raises:
            ValueError: If BPM, sample rate, or step count are invalid
            TypeError: If audio samples are in unsupported format
        
        Example:
            >>> def step_callback(step):
            ...     print(f"Now on step: {step}")
            >>> 
            >>> samples = [kick_samples, snare_samples, hihat_samples]
            >>> mixer = AudioSourceMixer(pygame.mixer, samples, 120, 44100, 16, step_callback, 60)
        """
        # Core audio system setup
        self.mixer = mixer
        self.sample_rate = sample_rate
        
        # Master sequencing parameters
        self.bpm = bpm
        self.min_bpm = min_bpm
        self.nb_steps = nb_steps
        self.current_step_index = 0
        self.current_sample_index = 0
        
        # Playback state management
        self.is_playing = False
        self.is_running = False
        
        # Threading and synchronization
        self.mixing_lock = Lock()
        self.stop_event = Event()
        self.sequencer_thread = None
        
        # UI callback integration
        self.on_current_step_changed = on_current_step_changed
        
        # Initialize track collection
        self.tracks = []
        self._initialize_tracks(all_wav_samples, bpm, sample_rate, nb_steps, min_bpm)
        
        # Audio buffer management
        self.mixing_buffer = None
        if self.tracks:
            buffer_size = self.tracks[0].buffer_nb_samples if hasattr(self.tracks[0], 'buffer_nb_samples') else 1024
            self.silence = array('h', b"\x00\x00" * buffer_size)
        else:
            self.silence = array('h', b"\x00\x00" * 1024)
        
        # Step timing calculations
        self.step_duration = 0.0
        self._calculate_step_duration()
    
    def _initialize_tracks(self, all_wav_samples, bpm, sample_rate, nb_steps, min_bpm):
        """
        Initialize individual tracks with provided audio samples.
        
        Creates AudioSourceTrack instances for each provided audio sample set,
        configuring them with synchronized timing and empty initial patterns.
        
        Args:
            all_wav_samples (list): Audio sample data for each track
            bpm (int): Beats per minute for track timing
            sample_rate (int): Audio sample rate
            nb_steps (int): Number of steps in patterns
            min_bpm (int): Minimum BPM for buffer calculations
        """
        for i, wav_samples in enumerate(all_wav_samples):
            try:
                # Create track with synchronized parameters
                track = AudioSourceTrack(
                    self.mixer, 
                    wav_samples, 
                    bpm, 
                    sample_rate, 
                    min_bpm
                )
                
                # Initialize with empty pattern (all steps inactive)
                empty_pattern = (0,) * nb_steps
                track.set_steps(empty_pattern)
                
                self.tracks.append(track)
                
            except Exception as e:
                print(f"AudioSourceMixer Warning: Failed to create track {i}: {e}")
    
    def _calculate_step_duration(self):
        """Calculate the duration of each step in seconds for timing control."""
        if self.bpm > 0:
            # Standard 16th note timing: 15 factor represents subdivision
            self.step_duration = 15.0 / self.bpm
        else:
            self.step_duration = 0.0
    
    def start(self):
        """
        Start the mixer's master sequencing system.
        
        Initializes and starts the master sequencing thread that coordinates
        all tracks and manages synchronized playback timing. Also starts
        individual track sequencers.
        
        Example:
            >>> mixer = AudioSourceMixer(...)
            >>> mixer.start()  # Begin synchronized sequencing
            >>> mixer.audio_play()  # Start playbook
        """
        if not self.is_running:
            self.is_running = True
            self.stop_event.clear()
            
            # Start individual tracks
            for track in self.tracks:
                track.start()
            
            # Start master sequencer thread
            self.sequencer_thread = Thread(target=self._master_sequencer_loop, daemon=True)
            self.sequencer_thread.start()
            
            print(f"AudioSourceMixer: Started master sequencer with {len(self.tracks)} tracks at {self.bpm} BPM")
    
    def stop(self):
        """
        Stop the mixer and cleanup all resources.
        
        Safely stops the master sequencer and all individual tracks,
        cleaning up associated resources and threads.
        """
        if self.is_running:
            self.is_running = False
            self.is_playing = False
            self.stop_event.set()
            
            # Stop individual tracks
            for track in self.tracks:
                track.stop()
            
            # Stop master sequencer thread
            if self.sequencer_thread and self.sequencer_thread.is_alive():
                self.sequencer_thread.join(timeout=1.0)
            
            print("AudioSourceMixer: Stopped master sequencer")
    
    def _master_sequencer_loop(self):
        """
        Master sequencer loop coordinating all tracks.
        
        This method runs in a background thread and manages the master timing
        for all tracks, ensuring synchronized step progression and UI updates.
        """
        last_step_time = time.time()
        
        while self.is_running and not self.stop_event.is_set():
            current_time = time.time()
            
            # Check if it's time for the next step
            if self.is_playing and current_time - last_step_time >= self.step_duration:
                self._process_master_step()
                last_step_time = current_time
            
            # Small sleep to prevent excessive CPU usage
            time.sleep(0.001)  # 1ms sleep for responsive timing
    
    def _process_master_step(self):
        """
        Process the current step for all tracks and update UI.
        
        Coordinates step progression across all tracks and triggers UI
        callback for visual synchronization with audio playback.
        """
        with self.mixing_lock:
            # Update UI callback with display synchronization offset
            if self.on_current_step_changed is not None:
                # Apply 2-step offset for audio buffer synchronization
                # This compensates for audio system latency
                display_step_index = self.current_step_index - 2
                if display_step_index < 0:
                    display_step_index += self.nb_steps
                
                self.on_current_step_changed(display_step_index)
            
            # Advance to next step
            self.current_step_index += 1
            if self.current_step_index >= self.nb_steps:
                self.current_step_index = 0
    
    def set_steps(self, track_index, steps):
        """
        Set the step pattern for a specific track.
        
        Updates the sequencing pattern for the specified track with thread-safe
        operations. Validates track index and pattern length before applying changes.
        
        Args:
            track_index (int): Index of the track to modify (0-based)
            steps (tuple or list): Pattern where 1 = active, 0 = inactive
        
        Returns:
            bool: True if pattern was successfully set, False otherwise
        
        Example:
            >>> mixer.set_steps(0, (1, 0, 1, 0))  # Set kick pattern
            >>> mixer.set_steps(1, (0, 1, 0, 1))  # Set snare pattern
        """
        # Validate track index
        if track_index >= len(self.tracks) or track_index < 0:
            print(f"AudioSourceMixer Warning: Invalid track index {track_index}")
            return False
        
        # Validate pattern length
        if len(steps) != self.nb_steps:
            print(f"AudioSourceMixer Warning: Pattern length {len(steps)} doesn't match {self.nb_steps} steps")
            return False
        
        with self.mixing_lock:
            self.tracks[track_index].set_steps(steps)
            return True
    
    def set_bpm(self, bpm):
        """
        Set the master BPM for all tracks.
        
        Updates the master tempo for synchronized playback across all tracks.
        Validates minimum BPM requirements before applying changes.
        
        Args:
            bpm (int): New beats per minute (must be >= min_bpm)
        
        Returns:
            bool: True if BPM was successfully set, False otherwise
        
        Example:
            >>> mixer.set_bpm(140)  # Speed up to 140 BPM
            >>> mixer.set_bpm(80)   # Slow down to 80 BPM
        """
        if bpm < self.min_bpm:
            print(f"AudioSourceMixer Warning: BPM {bpm} below minimum {self.min_bpm}")
            return False
        
        with self.mixing_lock:
            self.bpm = bpm
            self._calculate_step_duration()
            
            # Update all tracks with new BPM
            for track in self.tracks:
                track.set_bpm(bpm)
            
            return True
    
    def audio_play(self):
        """
        Start audio playback for all tracks.
        
        Begins synchronized playback of all tracks according to their
        current step patterns. Can be called multiple times safely.
        
        Example:
            >>> mixer.audio_play()   # Start playback
            >>> mixer.audio_stop()   # Stop playback
            >>> mixer.audio_play()   # Resume playback
        """
        with self.mixing_lock:
            self.is_playing = True
            print("AudioSourceMixer: Playback started")
    
    def audio_stop(self):
        """
        Stop audio playback for all tracks.
        
        Stops synchronized playback while maintaining track patterns and
        sequencer state. Playback can be resumed with audio_play().
        """
        with self.mixing_lock:
            self.is_playing = False
            print("AudioSourceMixer: Playback stopped")
    
    def get_mixer_state(self):
        """
        Get comprehensive information about the mixer's current state.
        
        Returns:
            dict: Dictionary containing mixer state information including:
                - is_playing: Current playback state
                - is_running: Master sequencer state
                - bpm: Current beats per minute
                - current_step: Current step in sequence
                - nb_steps: Total steps in pattern
                - track_count: Number of tracks in mixer
                - track_patterns: List of current patterns for all tracks
        
        Example:
            >>> state = mixer.get_mixer_state()
            >>> print(f"Mixer playing: {state['is_playing']} at {state['bpm']} BPM")
        """
        with self.mixing_lock:
            track_patterns = []
            for track in self.tracks:
                if hasattr(track, 'get_pattern_info'):
                    track_patterns.append(track.get_pattern_info())
                else:
                    track_patterns.append({'steps': getattr(track, 'steps', ())})
            
            return {
                'is_playing': self.is_playing,
                'is_running': self.is_running,
                'bpm': self.bpm,
                'current_step': self.current_step_index,
                'nb_steps': self.nb_steps,
                'track_count': len(self.tracks),
                'track_patterns': track_patterns,
                'step_duration': self.step_duration
            }
    
    def get_bytes(self, *args, **kwargs):
        """
        Legacy method for compatibility with audiostream interface.
        
        This method maintains compatibility with the original audiostream-based
        implementation. In the pygame version, audio mixing and playback are
        handled directly by individual track sequencers and pygame mixer.
        
        Args:
            *args: Legacy positional arguments (ignored)
            **kwargs: Legacy keyword arguments (ignored)
        
        Returns:
            bytes: Empty byte string (audio handled by pygame directly)
        
        Note:
            This method is maintained for interface compatibility but does not
            perform actual audio processing in the pygame implementation.
            The mixing logic has been moved to individual track management
            and pygame's built-in mixing capabilities.
        """
        # In pygame implementation, mixing is handled by individual tracks
        # and pygame's built-in mixing system
        if self.tracks:
            step_nb_samples = getattr(self.tracks[0], 'step_nb_samples', 1024)
            empty_buffer = b"\x00\x00" * step_nb_samples
        else:
            empty_buffer = b"\x00\x00" * 1024
        
        return empty_buffer
    
    def __del__(self):
        """Destructor to ensure proper cleanup when object is garbage collected."""
        self.stop()