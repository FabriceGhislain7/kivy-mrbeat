"""
Play Indicator Module - Visual Step Sequencer Display

This module provides visual feedback for step sequencing in the MrBeat drum machine.
It displays the current playback position with illuminated indicators that move
in sync with the audio sequencer, providing real-time visual feedback to users.

The play indicator system consists of individual light widgets arranged horizontally
to represent each step in the sequence pattern. As the sequencer progresses,
the corresponding light illuminates to show the current playback position.

Features:
- Real-time step position visualization
- Configurable number of steps (typically 16)
- Synchronized with audio engine timing
- Professional indicator light graphics
- Responsive layout with proper alignment
- Thread-safe UI updates via Kivy Clock system

Author: MrBeat Development Team
Version: 2.0 (Enhanced Documentation)
"""

# Kivy framework imports for UI components
from kivy.metrics import dp
from kivy.properties import NumericProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.image import Image
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.widget import Widget


class PlayIndicatorLight(Image):
    """
    Individual indicator light widget for step visualization.
    
    This class represents a single step indicator light in the sequencer display.
    Each light can be in either an "on" (illuminated) or "off" (dark) state,
    corresponding to whether that step is currently being played.
    
    The light uses image sources to display different states, providing a
    professional visual appearance that matches the overall UI design.
    
    Inheritance:
        Inherits from Kivy's Image widget to display indicator graphics
    
    States:
        - Off: "images/indicator_light_off.png" (dark/inactive appearance)
        - On: "images/indicator_light_on.png" (bright/active appearance)
    
    Usage:
        This class is typically instantiated automatically by PlayIndicatorWidget
        and should not be created directly by user code.
    """
    pass


class PlayIndicatorWidget(BoxLayout):
    """
    Visual step sequencer indicator widget.
    
    This widget provides real-time visual feedback for step sequencing by displaying
    a horizontal row of indicator lights. Each light represents one step in the
    sequence, and the currently playing step is highlighted.
    
    The widget automatically synchronizes with the audio engine to provide accurate
    visual feedback, enhancing the user experience during beat creation and playback.
    
    Attributes:
        nb_steps (int): Current number of steps in the sequence
        lights (list): Collection of PlayIndicatorLight widgets
        left_align (NumericProperty): Left alignment offset for proper positioning
    
    Layout:
        Uses horizontal BoxLayout to arrange indicator lights in a row,
        with a spacer widget for proper alignment with track controls.
    
    Example:
        >>> indicator = PlayIndicatorWidget()
        >>> indicator.set_nb_steps(16)           # Configure for 16-step sequence
        >>> indicator.set_current_step_index(4)  # Highlight step 4
    """
    
    # Step sequencing configuration
    nb_steps = 0                              # Number of steps in current sequence
    lights = []                               # List of individual indicator lights
    left_align = NumericProperty(0)           # Alignment offset for UI positioning
    
    def set_current_step_index(self, index):
        """
        Update the visual indicator to show the current playing step.
        
        This method illuminates the indicator light for the specified step while
        turning off all other lights. It provides real-time visual feedback
        synchronized with the audio sequencer.
        
        Args:
            index (int): Zero-based index of the step to highlight (0 to nb_steps-1)
        
        Returns:
            None
        
        Note:
            If the provided index is out of range, the method returns early
            without making changes to prevent UI errors.
        
        Thread Safety:
            This method is designed to be called from Kivy's main UI thread
            via Clock.schedule_once() to ensure thread-safe GUI updates.
        
        Example:
            >>> # Highlight step 3 (4th step in 0-based indexing)
            >>> indicator.set_current_step_index(3)
            
            >>> # This will safely ignore out-of-range requests
            >>> indicator.set_current_step_index(20)  # No effect if only 16 steps
        """
        # Validate step index to prevent array bounds errors
        if index >= len(self.lights):
            return
        
        # Update all indicator lights based on current step
        for i in range(0, len(self.lights)):
            light = self.lights[i]
            
            # Illuminate current step, darken all others
            if i == index:
                light.source = "images/indicator_light_on.png"    # Active state
            else:
                light.source = "images/indicator_light_off.png"   # Inactive state
    
    def set_nb_steps(self, nb_steps):
        """
        Configure the number of steps and rebuild the indicator layout.
        
        This method dynamically creates the appropriate number of indicator lights
        for the specified step count. It rebuilds the entire widget layout when
        the step count changes, ensuring proper visual representation.
        
        Args:
            nb_steps (int): Number of steps in the sequence (typically 8, 16, or 32)
        
        Returns:
            None
        
        Process:
            1. Check if step count has actually changed
            2. Clear existing widgets and light references
            3. Add alignment spacer widget
            4. Create and add new indicator lights
            5. Update internal step count
        
        Performance Note:
            This method performs a complete widget rebuild, so it should only
            be called when the step count actually changes, not on every update.
        
        Example:
            >>> # Configure for standard 16-step sequencing
            >>> indicator.set_nb_steps(16)
            
            >>> # Change to 8-step pattern
            >>> indicator.set_nb_steps(8)
            
            >>> # Calling with same value is efficiently ignored
            >>> indicator.set_nb_steps(8)  # No rebuild occurs
        """
        # Only rebuild if step count has actually changed
        if not nb_steps == self.nb_steps:
            
            # === WIDGET CLEANUP PHASE ===
            # Clear existing light references and remove all widgets
            self.lights = []
            self.clear_widgets()
            
            # === LAYOUT ALIGNMENT PHASE ===
            # Add spacer widget for proper alignment with track controls
            # This ensures indicator lights align with step buttons in tracks
            dummy_widget = Widget()
            dummy_widget.size_hint_x = None           # Fixed width, no stretching
            dummy_widget.width = self.left_align      # Use configured alignment offset
            self.add_widget(dummy_widget)
            
            # === INDICATOR LIGHTS CREATION PHASE ===
            # Create individual indicator light for each step
            for i in range(0, nb_steps):
                # Create new indicator light widget
                light = PlayIndicatorLight()
                light.source = "images/indicator_light_off.png"  # Initialize as inactive
                
                # Add to internal collection for state management
                self.lights.append(light)
                
                # Add to widget layout for visual display
                self.add_widget(light)
            
            # === FINALIZATION PHASE ===
            # Update internal step count to reflect new configuration
            self.nb_steps = nb_steps