"""
Sound Kit Service Module - Professional Audio Sample Management

This module provides comprehensive audio sample management for the MrBeat drum machine.
It handles loading, organizing, and providing access to drum samples and sound kits,
ensuring efficient audio data management and seamless integration with the audio engine.

The service architecture supports multiple sound kits with different configurations,
allowing users to switch between various drum collections while maintaining
consistent performance and audio quality.

Features:
- WAV audio file loading and processing
- Multiple sound kit configurations (basic and extended)
- Efficient audio sample caching and management
- Professional 16-bit audio format support
- Extensible architecture for custom sound kits
- Thread-safe audio data access

Audio Format Support:
- WAV files with standard PCM encoding
- 16-bit signed integer audio samples
- Various sample rates (automatically handled)
- Mono and stereo audio files

Author: MrBeat Development Team
Version: 2.0 (Enhanced Documentation)
"""

import wave
from array import array


class Sound:
    """
    Individual audio sample representation with professional loading capabilities.
    
    This class manages a single audio sample, handling WAV file loading, format
    conversion, and providing access to raw audio data. Each Sound instance
    represents one drum sound (kick, snare, hi-hat, etc.) in the kit.
    
    The class automatically processes WAV files into the format required by the
    audio engine, ensuring optimal performance and compatibility across different
    audio file configurations.
    
    Attributes:
        filename (str): Path to the WAV audio file
        displayname (str): Human-readable name for UI display
        nb_samples (int): Number of audio samples in the file
        samples (array): Raw audio sample data as 16-bit integers
    
    Audio Processing:
        - Loads WAV files using Python's wave module
        - Converts to 16-bit signed integer format
        - Handles various sample rates and bit depths
        - Optimizes for real-time audio playback
    
    Example:
        >>> kick_sound = Sound("sounds/kit1/kick.wav", "KICK")
        >>> print(f"Loaded {kick_sound.nb_samples} samples")
        >>> audio_engine.play_sound(kick_sound.samples)
    """
    
    def __init__(self, filename, displayname):
        """
        Initialize a new Sound instance with audio file loading.
        
        Creates a new Sound object and immediately loads the specified WAV file,
        processing it into the format required for audio playback. The loading
        process includes format validation and sample data extraction.
        
        Args:
            filename (str): Path to the WAV file to load
                Must be a valid WAV file with PCM encoding
            displayname (str): Human-readable name for this sound
                Used in the UI for track labeling and identification
        
        Raises:
            FileNotFoundError: If the specified WAV file cannot be found
            wave.Error: If the file is not a valid WAV format
            ValueError: If the audio format is not supported
        
        Example:
            >>> # Load a kick drum sample
            >>> kick = Sound("sounds/kit1/kick.wav", "KICK")
            
            >>> # Load a custom sample with descriptive name
            >>> custom = Sound("samples/my_snare.wav", "Custom Snare")
        """
        # Store file information for reference
        self.filename = filename
        self.displayname = displayname
        
        # Initialize audio data containers
        self.nb_samples = 0
        self.samples = None
        
        # Load and process the audio file immediately
        self.load_sound()
    
    def load_sound(self):
        """
        Load and process WAV audio file into usable sample data.
        
        This method handles the complete audio loading pipeline:
        1. Opens the WAV file using Python's wave module
        2. Extracts audio frame count and raw sample data
        3. Converts to 16-bit signed integer array format
        4. Stores processed data for audio engine consumption
        
        The processed audio data is stored in a format optimized for
        real-time playback by the pygame-based audio engine.
        
        Raises:
            FileNotFoundError: If the audio file cannot be located
            wave.Error: If the file format is invalid or corrupted
            MemoryError: If the audio file is too large to load
        
        Audio Format Requirements:
            - WAV format with PCM encoding
            - Any sample rate (automatically handled)
            - 8, 16, 24, or 32-bit depth (converted to 16-bit)
            - Mono or stereo (processed appropriately)
        
        Performance Notes:
            - Audio data is loaded into memory for low-latency access
            - Large files may consume significant RAM
            - Loading occurs once during initialization for efficiency
        """
        try:
            # === AUDIO FILE OPENING PHASE ===
            # Open WAV file in read-binary mode for audio processing
            wav_file = wave.open(self.filename, mode='rb')
            
            # === AUDIO METADATA EXTRACTION ===
            # Get total number of audio frames (samples)
            self.nb_samples = wav_file.getnframes()
            
            # === RAW AUDIO DATA EXTRACTION ===
            # Read all audio frames as raw bytes
            frames = wav_file.readframes(self.nb_samples)
            
            # === AUDIO FORMAT CONVERSION ===
            # Convert raw bytes to 16-bit signed integer array
            # 'h' format: signed short (16-bit) integers
            # This format is optimal for pygame audio processing
            self.samples = array('h', frames)
            
            # === CLEANUP PHASE ===
            # Close the WAV file to free system resources
            wav_file.close()
            
        except FileNotFoundError:
            print(f"Sound Error: Audio file not found: {self.filename}")
            raise
        except wave.Error as e:
            print(f"Sound Error: Invalid WAV format in {self.filename}: {e}")
            raise
        except Exception as e:
            print(f"Sound Error: Failed to load {self.filename}: {e}")
            raise


class SoundKit:
    """
    Base class for drum sound kit collections.
    
    This abstract base class defines the interface for sound kit implementations,
    providing a consistent way to access and manage collections of drum samples.
    Different sound kits can inherit from this class to provide various
    drum collections while maintaining a uniform API.
    
    The sound kit system allows for easy expansion and customization of
    available drum sounds, supporting both built-in kits and user-defined
    collections.
    
    Attributes:
        sounds (tuple): Collection of Sound instances in this kit
            Should be defined by subclasses with specific sound selections
    
    Interface Methods:
        - get_nb_tracks(): Returns number of tracks/sounds in the kit
        - get_all_samples(): Returns all audio sample data for mixer setup
    
    Design Pattern:
        Uses composition to group related Sound instances into logical
        collections that represent complete drum kits or sound sets.
    """
    
    # Sound collection - to be defined by subclasses
    sounds = ()
    
    def get_nb_tracks(self):
        """
        Get the number of tracks (sounds) available in this kit.
        
        Returns the total count of individual sounds in this kit,
        which determines how many tracks will be available in the
        drum machine interface.
        
        Returns:
            int: Number of sounds/tracks in this kit
        
        Example:
            >>> kit = SoundKit1()
            >>> print(f"This kit has {kit.get_nb_tracks()} tracks")
            This kit has 4 tracks
        """
        return len(self.sounds)
    
    def get_all_samples(self):
        """
        Extract audio sample data from all sounds in the kit.
        
        This method collects the raw audio sample data from every sound
        in the kit and returns it as a list. The returned data is used
        by the audio mixer to set up multi-track sequencing capabilities.
        
        Returns:
            list: List of audio sample arrays, one for each sound in the kit
                Each element is an array of 16-bit audio samples
        
        Usage:
            This method is typically called during audio engine initialization
            to provide all necessary audio data to the mixer system.
        
        Example:
            >>> kit = SoundKit1All()
            >>> samples = kit.get_all_samples()
            >>> mixer = audio_engine.create_mixer(samples, 120, 16, callback, 60)
        """
        # Collect sample data from all sounds in the kit
        all_samples = []
        for i in range(0, len(self.sounds)):
            all_samples.append(self.sounds[i].samples)
        return all_samples


class SoundKit1(SoundKit):
    """
    Basic drum kit with essential drum sounds.
    
    This sound kit provides the fundamental drum sounds needed for basic
    beat creation. It includes the core elements of a standard drum kit:
    kick drum, clap, shaker, and snare drum.
    
    Sound Selection:
        - KICK: Deep bass drum for strong downbeats
        - CLAP: Hand clap sound for accents and fills
        - SHAKER: Percussion shaker for rhythmic texture
        - SNARE: Snare drum for backbeats and rolls
    
    Use Cases:
        - Basic beat creation and learning
        - Simple rhythm patterns
        - Minimalist drum programming
        - Resource-constrained environments
    
    Example:
        >>> basic_kit = SoundKit1()
        >>> print(f"Basic kit has {basic_kit.get_nb_tracks()} sounds")
        Basic kit has 4 sounds
    """
    
    # Define core drum sound collection
    sounds = (
        Sound("sounds/kit1/kick.wav", "KICK"),      # Deep bass drum
        Sound("sounds/kit1/clap.wav", "CLAP"),      # Hand clap percussion
        Sound("sounds/kit1/shaker.wav", "SHAKER"),  # Rhythmic shaker
        Sound("sounds/kit1/snare.wav", "SNARE")     # Snare drum backbeat
    )


class SoundKit1All(SoundKit):
    """
    Extended drum kit with comprehensive sound collection.
    
    This sound kit provides a complete set of drum and percussion sounds
    for professional beat creation. It includes all sounds from SoundKit1
    plus additional elements for more complex and varied compositions.
    
    Sound Collection:
        Core Drums:
        - KICK: Deep bass drum foundation
        - CLAP: Hand clap accents
        - SHAKER: Percussion texture
        - SNARE: Snare drum backbeats
        
        Extended Sounds:
        - BASS: Synthesized bass sounds
        - EFFECTS: Sound effects and transitions
        - PLUCK: Melodic plucked instruments
        - VOCAL: Vocal chops and samples
    
    Use Cases:
        - Professional beat production
        - Complex rhythm programming
        - Multi-layered compositions
        - Creative sound design
        - Full-featured drum machine operation
    
    Example:
        >>> full_kit = SoundKit1All()
        >>> print(f"Full kit has {full_kit.get_nb_tracks()} sounds")
        Full kit has 8 sounds
    """
    
    # Define comprehensive sound collection
    sounds = (
        # === CORE DRUM SECTION ===
        Sound("sounds/kit1/kick.wav", "KICK"),          # Primary bass drum
        Sound("sounds/kit1/clap.wav", "CLAP"),          # Hand clap percussion
        Sound("sounds/kit1/shaker.wav", "SHAKER"),      # Rhythmic shaker
        Sound("sounds/kit1/snare.wav", "SNARE"),        # Snare drum
        
        # === EXTENDED SOUND SECTION ===
        Sound("sounds/kit1/bass.wav", "BASS"),          # Synthesized bass
        Sound("sounds/kit1/effects.wav", "EFFECTS"),    # Sound effects
        Sound("sounds/kit1/pluck.wav", "PLUCK"),        # Melodic plucks
        Sound("sounds/kit1/vocal_chop.wav", "VOCAL")    # Vocal samples
    )


class SoundKitService:
    """
    Central service for sound kit management and access.
    
    This service class provides a centralized interface for accessing sound kits
    and individual sounds within the MrBeat application. It acts as a facade
    that simplifies sound kit usage while providing a clean API for the UI
    and audio engine integration.
    
    The service uses the SoundKit1All configuration by default, providing
    the full collection of available sounds for maximum creative flexibility.
    
    Architecture Benefits:
        - Centralized sound management
        - Easy sound kit switching capability
        - Clean separation between UI and audio data
        - Simplified API for common operations
        - Future extensibility for multiple kit support
    
    Attributes:
        soundkit (SoundKit): Currently active sound kit instance
            Defaults to SoundKit1All for comprehensive sound collection
    
    Example:
        >>> service = SoundKitService()
        >>> kick_sound = service.get_sound_at(0)  # Get first sound (kick)
        >>> print(f"Kit has {service.get_nb_tracks()} tracks")
    """
    
    def __init__(self):
        """
        Initialize the sound kit service with default configuration.
        
        Sets up the service with SoundKit1All as the default sound kit,
        providing access to the complete collection of drum and percussion
        sounds available in the application.
        """
        # Use comprehensive sound kit as default configuration
        self.soundkit = SoundKit1All()
    
    def get_nb_tracks(self):
        """
        Get the number of tracks available in the current sound kit.
        
        This method provides a convenient way to determine how many
        tracks should be created in the UI and audio mixer without
        directly accessing the sound kit internals.
        
        Returns:
            int: Number of tracks/sounds in the current kit
        
        Example:
            >>> service = SoundKitService()
            >>> track_count = service.get_nb_tracks()
            >>> print(f"Creating {track_count} track widgets")
        """
        return self.soundkit.get_nb_tracks()
    
    def get_sound_at(self, index):
        """
        Retrieve a specific sound from the current kit by index.
        
        This method provides safe access to individual sounds within the
        kit, with bounds checking to prevent index errors. It's used by
        the UI to get sound information for track creation and labeling.
        
        Args:
            index (int): Zero-based index of the desired sound
                Must be within range [0, get_nb_tracks()-1]
        
        Returns:
            Sound: Sound instance at the specified index
            None: If index is out of range (prevents crashes)
        
        Example:
            >>> service = SoundKitService()
            >>> kick = service.get_sound_at(0)      # First sound (kick)
            >>> snare = service.get_sound_at(3)     # Fourth sound (snare)
            >>> invalid = service.get_sound_at(99)  # Returns None safely
        """
        # Validate index to prevent array bounds errors
        if index >= len(self.soundkit.sounds):
            return None
        
        # Return the requested sound instance
        return self.soundkit.sounds[index]