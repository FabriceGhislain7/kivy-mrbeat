"""
MrBeat - Professional Drum Machine Application

This is the main application module for MrBeat, a professional drum machine
and beat sequencer built with Kivy framework and pygame audio engine.
The application provides an intuitive interface for creating rhythmic patterns
and musical compositions with high-quality audio processing.

Features:
- Multi-track drum sequencing with 16-step patterns
- Real-time BPM control (80-160 BPM range)
- Professional audio engine with low-latency playback
- Intuitive graphical user interface with visual step indicators
- Sound kit management with multiple drum samples
- Thread-safe audio processing for stable performance

Technical Architecture:
- UI Framework: Kivy for cross-platform GUI
- Audio Engine: Pygame-based professional audio system
- Pattern Sequencing: Step-based beat programming
- Real-time Processing: Multi-threaded audio architecture

Author: MrBeat Development Team
Version: 2.0 (Pygame Implementation)
License: Professional Use
"""

# Kivy configuration - Set application window properties
from kivy import Config
Config.set('graphics', 'width', '780')     # Default window width
Config.set('graphics', 'height', '360')    # Default window height  
Config.set('graphics', 'minimum_width', '650')   # Minimum resizable width
Config.set('graphics', 'minimum_height', '300')  # Minimum resizable height

# Core Kivy framework imports
from kivy.app import App
from kivy.lang import Builder
from kivy.metrics import dp
from kivy.properties import ObjectProperty, NumericProperty, Clock
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.widget import Widget

# MrBeat application modules
from audio_engine import AudioEngine
from sound_kit_service import SoundKitService
from track import TrackWidget

# Load Kivy UI definition files
Builder.load_file("track.kv")
Builder.load_file("play_indicator.kv")

# Application constants for beat sequencing
TRACK_NB_STEPS = 16    # Number of steps per track pattern
MIN_BPM = 80           # Minimum beats per minute
MAX_BPM = 160          # Maximum beats per minute


class VerticalSpacingWidget(Widget):
    """
    Simple spacing widget for vertical layout organization.
    
    This widget provides consistent vertical spacing between track elements
    in the main interface layout, ensuring proper visual separation and
    alignment of UI components.
    """
    pass


class MainWidget(RelativeLayout):
    """
    Main application widget managing the drum machine interface.
    
    This class serves as the primary container for the drum machine interface,
    coordinating between the audio engine, track widgets, playback controls,
    and visual indicators. It manages the overall application state and
    user interactions.
    
    The widget handles real-time audio processing, pattern sequencing,
    tempo control, and visual feedback for an intuitive beat-making experience.
    
    Attributes:
        tracks_layout (ObjectProperty): Container for individual track widgets
        play_indicator_widget (ObjectProperty): Visual step progression indicator
        TRACK_STEPS_LEFT_ALIGN (NumericProperty): Alignment constant for track steps
        step_index (int): Current step position in the sequence
        bpm (NumericProperty): Current beats per minute for tempo control
        nb_tracks (NumericProperty): Total number of available tracks
        
    Properties:
        sound_kit_service (SoundKitService): Service for managing drum samples
        audio_engine (AudioEngine): Core audio processing system
        mixer (AudioSourceMixer): Multi-track audio mixer instance
    """
    
    # Kivy property bindings for UI elements
    tracks_layout = ObjectProperty()
    play_indicator_widget = ObjectProperty()
    TRACK_STEPS_LEFT_ALIGN = NumericProperty(dp(120))
    
    # Sequencing state variables
    step_index = 0
    bpm = NumericProperty(115)          # Default BPM
    nb_tracks = NumericProperty(0)
    
    def __init__(self, **kwargs):
        """
        Initialize the main drum machine interface.
        
        Sets up the audio engine, sound kit service, and creates the master
        mixer for coordinated multi-track playback. Initializes all core
        systems required for beat sequencing and audio processing.
        
        Args:
            **kwargs: Additional keyword arguments passed to parent RelativeLayout
        
        Raises:
            RuntimeError: If audio engine initialization fails
            FileNotFoundError: If sound kit files are not found
        """
        super(MainWidget, self).__init__(**kwargs)
        
        # Initialize sound kit service for drum sample management
        self.sound_kit_service = SoundKitService()
        self.nb_tracks = self.sound_kit_service.get_nb_tracks()
        
        # Initialize professional audio engine
        self.audio_engine = AudioEngine()
        
        # Create master mixer with synchronized multi-track sequencing
        self.mixer = self.audio_engine.create_mixer(
            self.sound_kit_service.soundkit.get_all_samples(),
            self.bpm,
            TRACK_NB_STEPS,
            self.on_mixer_current_step_changed,
            MIN_BPM
        )
    
    def on_parent(self, widget, parent):
        """
        Configure UI elements when widget is added to parent container.
        
        This method is called automatically by Kivy when the widget is added
        to a parent container. It sets up the play indicator, creates individual
        track widgets, and establishes the complete UI layout.
        
        Args:
            widget: Reference to this widget instance
            parent: Parent container widget
        
        Note:
            This method creates the dynamic UI elements that depend on the
            sound kit configuration and number of available tracks.
        """
        # Configure play indicator for visual step progression
        self.play_indicator_widget.set_nb_steps(TRACK_NB_STEPS)
        
        # Create individual track widgets for each drum sound
        for i in range(0, self.sound_kit_service.get_nb_tracks()):
            sound = self.sound_kit_service.get_sound_at(i)
            
            # Add vertical spacing for clean layout
            self.tracks_layout.add_widget(VerticalSpacingWidget())
            
            # Create and add track widget with audio integration
            track_widget = TrackWidget(
                sound,
                self.audio_engine,
                TRACK_NB_STEPS,
                self.mixer.tracks[i],
                self.TRACK_STEPS_LEFT_ALIGN
            )
            self.tracks_layout.add_widget(track_widget)
        
        # Add final spacing element
        self.tracks_layout.add_widget(VerticalSpacingWidget())
    
    def on_mixer_current_step_changed(self, step_index):
        """
        Handle step progression updates from the audio mixer.
        
        This callback method is invoked by the audio mixer when the current
        step changes during playback. It schedules UI updates to maintain
        visual synchronization with audio playback.
        
        Args:
            step_index (int): New current step index (0-based)
        
        Note:
            Uses Kivy's Clock.schedule_once to ensure UI updates occur on
            the main thread for thread-safe GUI operations.
        """
        self.step_index = step_index
        Clock.schedule_once(self.update_play_indicator_cbk, 0)
    
    def update_play_indicator_cbk(self, dt):
        """
        Update the visual play indicator widget.
        
        This method updates the play indicator to show the current step
        position during playback, providing visual feedback synchronized
        with the audio sequencer.
        
        Args:
            dt (float): Delta time from Kivy Clock (unused but required)
        
        Note:
            This method runs on the main UI thread to ensure safe GUI updates.
        """
        if self.play_indicator_widget is not None:
            self.play_indicator_widget.set_current_step_index(self.step_index)
    
    def on_play_button_pressed(self):
        """
        Handle play button press events.
        
        Starts audio playback for all tracks according to their current
        step patterns. Begins synchronized sequencing across all configured
        tracks with immediate audio response.
        
        Example:
            >>> main_widget.on_play_button_pressed()  # Starts playback
        """
        self.mixer.audio_play()
    
    def on_stop_button_pressed(self):
        """
        Handle stop button press events.
        
        Stops audio playback while maintaining current patterns and sequencer
        state. Playback can be resumed with on_play_button_pressed() without
        losing pattern configurations.
        
        Example:
            >>> main_widget.on_stop_button_pressed()  # Stops playbook
        """
        self.mixer.audio_stop()
    
    def on_bpm(self, widget, value):
        """
        Handle BPM (tempo) changes from UI controls.
        
        Updates the master tempo for all tracks while enforcing minimum and
        maximum BPM limits. Provides real-time tempo adjustment during playbook
        without interrupting audio flow.
        
        Args:
            widget: UI widget that triggered the BPM change
            value (int): New BPM value requested
        
        Note:
            BPM is automatically clamped to the valid range (MIN_BPM to MAX_BPM)
            to prevent audio timing issues and maintain stable playback.
        
        Example:
            >>> main_widget.on_bpm(slider_widget, 140)  # Set tempo to 140 BPM
        """
        print("BPM: " + str(value))
        
        # Enforce minimum BPM limit
        if value < MIN_BPM:
            self.bpm = MIN_BPM
            return
        
        # Enforce maximum BPM limit  
        if value > MAX_BPM:
            self.bpm = MAX_BPM
            return
        
        # Apply validated BPM to audio mixer
        self.mixer.set_bpm(self.bpm)


class MrBeatApp(App):
    """
    Main application class for the MrBeat drum machine.
    
    This class serves as the entry point for the MrBeat application,
    inheriting from Kivy's App class to provide the application framework.
    It automatically loads the main widget and manages the application lifecycle.
    
    The app class handles application-level events, configuration loading,
    and provides the foundation for the complete drum machine experience.
    
    Features:
        - Automatic main widget loading
        - Application lifecycle management
        - Cross-platform compatibility through Kivy framework
        - Professional audio integration
    
    Usage:
        >>> app = MrBeatApp()
        >>> app.run()  # Start the drum machine application
    """
    pass


# Application entry point
if __name__ == '__main__':
    """
    Application startup sequence.
    
    Creates and runs the MrBeat drum machine application with all
    configured audio systems, UI components, and beat sequencing
    capabilities activated.
    """
    MrBeatApp().run()