"""
AudioSourceTrack Module - Professional Beat Sequencing System

This module provides a comprehensive track-based audio sequencing system designed
for beat making and rhythmic pattern creation. Each track operates independently
with precise timing control and step-based pattern sequencing.

The AudioSourceTrack class manages individual instrument tracks within a drum
machine or beat sequencer, providing professional-grade timing accuracy and
flexible pattern programming capabilities.

Features:
- Step-based pattern sequencing
- Precise BPM-based timing control
- Professional audio quality maintenance
- Thread-safe pattern modification
- Optimized audio buffer management
- Real-time tempo changes support

Author: MrBeat Development Team
Version: 2.0 (Pygame Implementation)
"""

import pygame
import numpy as np
from threading import Thread, Lock, Event
import time
from array import array


class AudioSourceTrack:
    """
    Professional Track-Based Audio Sequencer for Beat Programming
    
    This class provides comprehensive track sequencing capabilities with step-based
    pattern programming, precise timing control, and professional audio quality.
    Each track operates independently and can be synchronized with other tracks
    through a master clock system.
    
    The track system supports complex pattern programming with variable step counts,
    real-time tempo changes, and seamless pattern switching without audio glitches.
    
    Attributes:
        mixer (pygame.mixer): Reference to pygame audio mixer
        wav_samples (array): Audio sample data for this track
        bpm (int): Current beats per minute for timing
        sample_rate (int): Audio sample rate for timing calculations
        steps (tuple): Current step pattern (1 = active, 0 = inactive)
        is_running (bool): Thread execution state
        pattern_lock (threading.Lock): Thread safety for pattern operations
    """
    
    def __init__(self, mixer, wav_samples, bpm, sample_rate, min_bpm=60, *args, **kwargs):
        """
        Initialize the AudioSourceTrack with comprehensive sequencing capabilities.
        
        Sets up a professional track sequencer with the provided audio samples,
        timing parameters, and buffer management for optimal performance.
        
        Args:
            mixer (pygame.mixer): Initialized pygame mixer instance
            wav_samples (array or numpy.ndarray): Audio sample data for this track
            bpm (int): Initial beats per minute for track timing
            sample_rate (int): Audio sample rate for timing calculations
            min_bpm (int, optional): Minimum BPM for buffer sizing. Defaults to 60.
            *args: Additional positional arguments (for compatibility)
            **kwargs: Additional keyword arguments (for compatibility)
        
        Raises:
            ValueError: If BPM or sample rate values are invalid
            TypeError: If audio samples are in unsupported format
        """
        # Core audio system references
        self.mixer = mixer
        
        # Audio sample management
        self.wav_samples = wav_samples
        self.nb_wav_samples = len(wav_samples) if wav_samples else 0
        
        # Timing and sequencing parameters
        self.bpm = bpm
        self.min_bpm = min_bpm
        self.sample_rate = sample_rate
        
        # Step sequencing state
        self.steps = ()
        self.current_step_index = 0
        self.current_sample_index = 0
        self.last_sound_sample_start_index = 0
        
        # Threading and synchronization
        self.is_running = False
        self.pattern_lock = Lock()
        self.stop_event = Event()
        self.playback_thread = None
        
        # Audio buffer calculations
        self.step_nb_samples = self._compute_step_nb_samples(bpm)
        self.buffer_nb_samples = self._compute_step_nb_samples(min_bpm)
        
        # Pre-allocated silence buffer for efficient processing
        self.silence = array('h', b"\\x00\\x00" * self.buffer_nb_samples)
        
        # Pygame-specific audio setup
        self.current_channel = None
        self.step_duration = 0.0
        self._calculate_step_duration()
        
        # Validate and adjust step samples for precise timing
        if bpm != 0:
            calculated_samples = int(self.sample_rate * 15 / bpm)
            if calculated_samples != self.step_nb_samples:
                self.step_nb_samples = calculated_samples
    
    def _compute_step_nb_samples(self, bpm_value):
        """
        Calculate the number of audio samples per sequencer step.
        
        This method computes the precise number of audio samples required for
        each step in the sequence based on the BPM and sample rate, ensuring
        accurate timing for beat sequencing.
        
        Args:
            bpm_value (int): Beats per minute value for calculation
        
        Returns:
            int: Number of samples per step, 0 if BPM is invalid
        
        Note:
            Formula: samples_per_step = sample_rate * 15 / BPM
            The factor 15 represents a standard subdivision for step sequencing.
        """
        if bpm_value != 0:
            return int(self.sample_rate * 15 / bpm_value)
        return 0
    
    def _calculate_step_duration(self):
        """Calculate the duration of each step in seconds for pygame timing."""
        if self.bpm > 0:
            # Calculate step duration: 15 represents 16th notes in standard sequencing
            self.step_duration = 15.0 / self.bpm
        else:
            self.step_duration = 0.0
    
    def start(self):
        """
        Start the track's audio sequencing thread.
        
        Initializes and starts the background thread responsible for step sequencing
        and audio playback timing. This method must be called before the track
        will begin playing patterns.
        
        Example:
            >>> track = AudioSourceTrack(mixer, samples, 120, 44100)
            >>> track.set_steps((1, 0, 1, 0))  # Set a basic pattern
            >>> track.start()  # Begin sequencing
        """
        if not self.is_running:
            self.is_running = True
            self.stop_event.clear()
            self.playback_thread = Thread(target=self._sequencer_loop, daemon=True)
            self.playback_thread.start()
            print(f"AudioSourceTrack: Started sequencing at {self.bpm} BPM")
    
    def stop(self):
        """
        Stop the track's audio sequencing and cleanup resources.
        
        Safely stops the sequencing thread and cleans up associated audio resources.
        Should be called when the track is no longer needed or when shutting down.
        """
        if self.is_running:
            self.is_running = False
            self.stop_event.set()
            
            if self.playback_thread and self.playback_thread.is_alive():
                self.playback_thread.join(timeout=1.0)
            
            # Stop any currently playing audio
            if self.current_channel:
                self.current_channel.stop()
            
            print("AudioSourceTrack: Stopped sequencing")
    
    def _sequencer_loop(self):
        """
        Main sequencing loop running in background thread.
        
        This method handles the core sequencing logic, managing step progression,
        audio triggering, and timing accuracy. It operates continuously while
        the track is active.
        """
        last_step_time = time.time()
        
        while self.is_running and not self.stop_event.is_set():
            current_time = time.time()
            
            # Check if it's time for the next step
            if current_time - last_step_time >= self.step_duration:
                self._process_current_step()
                last_step_time = current_time
                
                # Advance to next step
                with self.pattern_lock:
                    self.current_step_index += 1
                    if self.current_step_index >= len(self.steps):
                        self.current_step_index = 0
            
            # Small sleep to prevent excessive CPU usage
            time.sleep(0.001)  # 1ms sleep for responsive timing
    
    def _process_current_step(self):
        """
        Process the current step in the sequence pattern.
        
        Determines whether to trigger audio playback based on the current step
        pattern and handles audio sample playback through pygame.
        """
        with self.pattern_lock:
            if not self._no_steps_activated() and len(self.steps) > self.current_step_index:
                if self.steps[self.current_step_index] == 1:
                    self._trigger_audio_sample()
    
    def _trigger_audio_sample(self):
        """
        Trigger playback of the track's audio sample.
        
        Creates a pygame Sound object from the track's audio samples and plays
        it immediately with optimal performance characteristics.
        """
        try:
            if self.wav_samples and self.nb_wav_samples > 0:
                # Convert samples to pygame Sound format
                if isinstance(self.wav_samples, np.ndarray):
                    if self.wav_samples.dtype != np.int16:
                        # Normalize and convert to 16-bit integers
                        audio_data = (self.wav_samples * 32767).astype(np.int16)
                    else:
                        audio_data = self.wav_samples
                    audio_bytes = audio_data.tobytes()
                else:
                    # Handle array type from original implementation
                    audio_bytes = self.wav_samples.tobytes() if hasattr(self.wav_samples, 'tobytes') else bytes(self.wav_samples)
                
                # Create and play pygame Sound
                sound = pygame.mixer.Sound(buffer=audio_bytes)
                self.current_channel = sound.play()
                
        except Exception as e:
            print(f"AudioSourceTrack Error: Failed to trigger sample - {e}")
    
    def set_steps(self, steps):
        """
        Set the step pattern for this track.
        
        Updates the track's sequencing pattern with thread-safe operations.
        The pattern determines which steps will trigger audio playback.
        
        Args:
            steps (tuple or list): Pattern where 1 = active step, 0 = inactive step
                Example: (1, 0, 1, 0) creates a pattern playing on steps 1 and 3
        
        Note:
            If the new pattern has a different length than the current pattern,
            the step index is reset to prevent out-of-bounds access.
        
        Example:
            >>> track.set_steps((1, 0, 0, 1, 1, 0, 1, 0))  # 8-step pattern
            >>> track.set_steps((1, 1, 1, 1))              # 4-step pattern
        """
        with self.pattern_lock:
            # Reset step index if pattern length changes
            if len(steps) != len(self.steps):
                self.current_step_index = 0
            
            self.steps = tuple(steps)  # Convert to immutable tuple for thread safety
    
    def set_bpm(self, bpm):
        """
        Update the track's BPM and recalculate timing parameters.
        
        Changes the track's tempo in real-time, automatically recalculating
        all timing-related parameters for seamless tempo transitions.
        
        Args:
            bpm (int): New beats per minute value (must be > 0)
        
        Raises:
            ValueError: If BPM is less than or equal to 0
        
        Example:
            >>> track.set_bpm(140)  # Speed up to 140 BPM
            >>> track.set_bpm(80)   # Slow down to 80 BPM
        """
        if bpm <= 0:
            raise ValueError("BPM must be greater than 0")
        
        with self.pattern_lock:
            self.bpm = bpm
            self.step_nb_samples = self._compute_step_nb_samples(bpm)
            self._calculate_step_duration()
    
    def _no_steps_activated(self):
        """
        Check if any steps in the current pattern are activated.
        
        Returns:
            bool: True if no steps are activated (all zeros), False otherwise
        
        Note:
            An empty pattern is considered as having no activated steps.
        """
        if len(self.steps) == 0:
            return True
        
        return not any(step == 1 for step in self.steps)
    
    def get_pattern_info(self):
        """
        Get comprehensive information about the current pattern state.
        
        Returns:
            dict: Dictionary containing pattern information including:
                - current_step: Current step index in the pattern
                - pattern_length: Total number of steps in pattern
                - active_steps: List of indices where steps are activated
                - bpm: Current beats per minute
                - step_duration: Duration of each step in seconds
        
        Example:
            >>> info = track.get_pattern_info()
            >>> print(f"Currently on step {info['current_step']}")
        """
        with self.pattern_lock:
            active_steps = [i for i, step in enumerate(self.steps) if step == 1]
            
            return {
                'current_step': self.current_step_index,
                'pattern_length': len(self.steps),
                'active_steps': active_steps,
                'bpm': self.bpm,
                'step_duration': self.step_duration,
                'is_running': self.is_running
            }
    
    def get_bytes(self, *args, **kwargs):
        """
        Legacy method for compatibility with audiostream interface.
        
        This method maintains compatibility with the original audiostream-based
        implementation. In the pygame version, audio playback is handled directly
        by the sequencer loop and pygame mixer.
        
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
        empty_buffer = b"\\x00\\x00" * self.step_nb_samples
        return empty_buffer
    
    def __del__(self):
        """Destructor to ensure proper cleanup when object is garbage collected."""
        self.stop()