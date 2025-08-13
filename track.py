"""
Track Widget Module - Individual Drum Track Interface

This module provides the track interface components for the MrBeat drum machine,
implementing individual drum track widgets with step sequencing capabilities.
Each track represents one drum sound with pattern programming functionality.

The track system enables users to create complex rhythmic patterns by combining
immediate sound triggering with step-based pattern sequencing. The visual
interface provides intuitive controls for both real-time performance and
detailed pattern programming.

Features:
- Individual sound triggering for real-time performance
- 16-step pattern sequencing with visual feedback
- Professional drum machine interface design
- Real-time pattern modification during playback
- Visual step grouping for easier pattern reading
- Seamless integration with audio engine and mixer

Architecture:
- TrackSoundButton: Immediate sound triggering
- TrackStepButton: Step-based pattern programming
- TrackWidget: Complete track with layout and logic integration

Author: MrBeat Development Team
Version: 2.0 (Enhanced Documentation)
"""

# Kivy framework imports for UI components
from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.image import Image
from kivy.uix.togglebutton import ToggleButton


class TrackStepButton(ToggleButton):
    """
    Step sequencer button for pattern programming.
    
    This class represents an individual step in the drum pattern sequence.
    Each button can be toggled on/off to create rhythmic patterns, with
    visual feedback showing the current state.
    
    The button uses toggle behavior where:
    - "down" state = step is active (drum will trigger on this step)
    - "normal" state = step is inactive (silence on this step)
    
    Visual Design:
        Uses different background images for visual distinction between
        step groups (every 4 steps) to improve pattern readability.
    
    Inheritance:
        Inherits from Kivy's ToggleButton for built-in toggle functionality
        
    Usage:
        Automatically created by TrackWidget during track initialization.
        State changes trigger pattern updates in the audio engine.
    """
    pass


class TrackSoundButton(Button):
    """
    Sound trigger button for immediate audio playback.
    
    This class provides immediate triggering of the track's drum sound,
    allowing for real-time performance and sound preview. When pressed,
    it immediately plays the associated audio sample through the audio engine.
    
    The button displays the name of the drum sound (e.g., "KICK", "SNARE")
    and provides visual feedback when pressed.
    
    Features:
        - Immediate audio sample triggering
        - Visual feedback with press states
        - Sound name display for track identification
        - Professional drum machine button styling
    
    Inheritance:
        Inherits from Kivy's Button for standard button behavior
        
    Usage:
        Created automatically by TrackWidget with sound-specific configuration.
        Connected to audio engine for immediate sound playback.
    """
    pass


class TrackWidget(BoxLayout):
    """
    Complete drum track widget with sound triggering and pattern sequencing.
    
    This class represents a complete drum track in the MrBeat interface,
    combining immediate sound triggering with step-based pattern programming.
    Each track manages one drum sound and provides comprehensive control
    over its playback behavior.
    
    The widget layout consists of:
    1. Sound trigger button with drum name
    2. Visual separator for clean layout organization  
    3. Series of step buttons for pattern programming (typically 16 steps)
    
    The track integrates with the audio engine to provide both immediate
    sound triggering and automated pattern playback through the sequencer.
    
    Attributes:
        audio_engine (AudioEngine): Reference to main audio processing system
        sound (Sound): Audio sample data and metadata for this track
        track_source (AudioSourceTrack): Audio sequencer for this track
        step_buttons (list): Collection of step programming buttons
        nb_steps (int): Number of steps in the sequence pattern
    
    Example:
        >>> # Create track for kick drum with 16 steps
        >>> kick_track = TrackWidget(
        ...     kick_sound, audio_engine, 16, mixer_track, dp(120)
        ... )
    """
    
    def __init__(self, sound, audio_engine, nb_steps, track_source, steps_left_align, **kwargs):
        """
        Initialize a complete drum track widget with all controls.
        
        Creates a comprehensive track interface including sound triggering,
        pattern programming, and visual layout. The track is immediately
        ready for user interaction and audio processing.
        
        Args:
            sound (Sound): Audio sample and metadata for this track
                Contains the drum sound samples and display name
            audio_engine (AudioEngine): Main audio processing system
                Used for immediate sound triggering
            nb_steps (int): Number of steps in the pattern sequence
                Typically 16 for standard drum machine operation
            track_source (AudioSourceTrack): Audio sequencer for this track
                Handles automated pattern playback
            steps_left_align (float): Left alignment offset for step buttons
                Ensures step buttons align with play indicator
            **kwargs: Additional arguments passed to parent BoxLayout
        
        Layout Structure:
            [Sound Button][Separator][Step 1][Step 2]...[Step N]
            
        Visual Design:
            - Sound button shows drum name (e.g., "KICK", "SNARE")
            - Separator provides clean visual division
            - Step buttons use alternating backgrounds for readability
            - Professional drum machine appearance throughout
        """
        # Initialize parent BoxLayout with horizontal orientation
        super(TrackWidget, self).__init__(**kwargs)
        
        # === CORE SYSTEM REFERENCES ===
        # Store references to audio and sound systems
        self.audio_engine = audio_engine       # For immediate sound triggering
        self.sound = sound                     # Audio sample and metadata
        self.track_source = track_source       # Audio sequencer for patterns
        
        # === SOUND TRIGGER SECTION SETUP ===
        # Create container for sound button and separator
        sound_and_separator_layout = BoxLayout()
        sound_and_separator_layout.size_hint_x = None        # Fixed width
        sound_and_separator_layout.width = steps_left_align  # Match indicator alignment
        self.add_widget(sound_and_separator_layout)
        
        # === SOUND TRIGGER BUTTON CREATION ===
        # Create main sound trigger button
        sound_button = TrackSoundButton()
        sound_button.text = sound.displayname              # Display drum name (e.g., "KICK")
        sound_button.on_press = self.on_sound_button_press  # Connect to trigger method
        sound_and_separator_layout.add_widget(sound_button)
        
        # === VISUAL SEPARATOR ELEMENT ===
        # Add separator image for clean visual division
        separator_image = Image(source="images/track_separator.png")
        separator_image.size_hint_x = None      # Fixed width separator
        separator_image.width = dp(15)          # 15dp width for subtle division
        sound_and_separator_layout.add_widget(separator_image)
        
        # === STEP SEQUENCER SETUP ===
        # Initialize step button collection and configuration
        self.step_buttons = []
        self.nb_steps = nb_steps
        
        # === STEP BUTTON CREATION LOOP ===
        # Create individual step buttons for pattern programming
        for i in range(0, nb_steps):
            # Create step button with toggle behavior
            step_button = TrackStepButton()
            
            # === VISUAL GROUPING SYSTEM ===
            # Alternate background images every 4 steps for readability
            # This creates visual groups: [1-4] [5-8] [9-12] [13-16]
            if int(i/4) % 2 == 0:
                # Steps 1-4, 9-12: First background style
                step_button.background_normal = "images/step_normal1.png"
            else:
                # Steps 5-8, 13-16: Second background style  
                step_button.background_normal = "images/step_normal2.png"
            
            # === EVENT BINDING ===
            # Connect button state changes to pattern update method
            step_button.bind(state=self.on_step_button_state)
            
            # === BUTTON REGISTRATION AND LAYOUT ===
            # Add to internal collection and widget layout
            self.step_buttons.append(step_button)
            self.add_widget(step_button)
    
    def on_sound_button_press(self):
        """
        Handle sound trigger button press for immediate audio playback.
        
        This method is called when the user presses the main sound button,
        providing immediate audio feedback and allowing real-time performance.
        The sound plays instantly without affecting the current pattern sequence.
        
        Audio Processing:
            - Triggers immediate playback through audio engine
            - Uses one-shot audio system for minimal latency
            - Does not interfere with automated pattern playback
            - Provides instant audio feedback for user interaction
        
        Use Cases:
            - Real-time performance and jamming
            - Sound preview during pattern creation
            - Manual triggering during playback
            - Audio feedback for user interface interaction
        
        Example:
            User clicks "KICK" button → kick drum sound plays immediately
        """
        # Trigger immediate playback of this track's audio sample
        self.audio_engine.play_sound(self.sound.samples)
    
    def on_step_button_state(self, widget, value):
        """
        Handle step button state changes and update pattern sequence.
        
        This method is called whenever any step button changes state (on/off),
        automatically updating the audio sequencer with the new pattern.
        The update happens in real-time, allowing pattern modification during playback.
        
        Args:
            widget (TrackStepButton): The step button that changed state
            value (str): New state value ("down" = active, "normal" = inactive)
        
        Pattern Processing:
            1. Scan all step buttons to determine current pattern
            2. Convert button states to binary pattern (1 = active, 0 = inactive)
            3. Send updated pattern to audio sequencer
            4. Changes take effect immediately, even during playback
        
        Pattern Format:
            List of integers where:
            - 1 = step is active (drum triggers on this step)
            - 0 = step is inactive (silence on this step)
            
        Example Pattern:
            [1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0]
            = Kick drum on beats 1, 5, 9, 13 (four-on-the-floor pattern)
        
        Real-time Updates:
            - Pattern changes apply immediately during playback
            - No audio glitches or interruptions
            - Smooth transitions between different patterns
            - Professional drum machine behavior
        """
        # === PATTERN EXTRACTION PHASE ===
        # Scan all step buttons to build current pattern
        steps = []
        for i in range(0, self.nb_steps):
            # Check each step button state and convert to binary
            if self.step_buttons[i].state == "down":
                steps.append(1)  # Active step - drum will trigger
            else:
                steps.append(0)  # Inactive step - silence
        
        # === AUDIO SEQUENCER UPDATE ===
        # Send updated pattern to audio sequencer for immediate use
        # This updates the pattern in real-time, even during playback
        self.track_source.set_steps(steps)
        
        # Note: Commented debug output - uncomment for pattern debugging
        # print(str(steps))