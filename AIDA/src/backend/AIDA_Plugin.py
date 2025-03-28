# AIDA Plugin for IDA Pro
# This file contains the main plugin class that integrates with IDA Pro's plugin system

from idaapi import plugin_t, PLUGIN_FIX, PLUGIN_KEEP, register_action, action_handler_t, action_desc_t
from src.frontend.Summarize_Widget import SummarizeWidget
from src.backend.Action_Handler import ActionHandler
from src.frontend.Main_Widget import MainWidget
from src.backend.Hooks import ContextMenuHooks

class AIDAPlugin(plugin_t):
    """
    Main plugin class for AIDA.
    Inherits from IDA Pro's plugin_t class to integrate with the IDA Pro plugin system.
    Manages the main widget and summarize windows.
    """
    flags: int = PLUGIN_FIX  # Plugin should be fixed in memory
    comment: str = "AIDA"  # Plugin comment shown in IDA Pro
    help: str = "Provides an AI assistant for pseudocode summaries"  # Help message
    wanted_name: str = "AIDA"  # Name of the plugin
    wanted_hotkey: str = "Alt-T"  # Hotkey to activate the plugin

    def __init__(self) -> None: 
        """
        Initialize the plugin instance.
        Creates empty lists for holding windows and sets up initial state.
        """
        super(AIDAPlugin, self).__init__()
        self.summarize_windows: list = []  # List to hold multiple summarize windows
        self.main_widget = None  # Main widget reference
        self.menu = None  # Context menu reference

    def init(self) -> int:
        """
        Plugin initialization method called by IDA Pro.
        Registers the action handler and sets up the context menu hooks.
        
        Returns:
            PLUGIN_KEEP to keep the plugin loaded, PLUGIN_FIX otherwise.
        """
        action_desc = action_desc_t(
            'AIDA',  # Action name
            'Summarize',  # Action text displayed in menus
            ActionHandler(self),  # Handler instance
            '',  # Shortcut
            'Summarize with AI',  # Tooltip
            -1  # Icon
        )
        if register_action(action_desc):
            self.menu = ContextMenuHooks()
            self.menu.hook()
            return PLUGIN_KEEP
        return PLUGIN_FIX

    def open_summarize_widget(self, pseudocode: str = "", source_identifier: str = "") -> None:
        """
        Opens a new summarize widget window.
        
        Args:
            pseudocode: Initial pseudocode to display in the window
            source_identifier: Identifier for the widget name
        """
        new_window: SummarizeWidget = SummarizeWidget(self.main_widget)
        self.summarize_windows.append(new_window)
        
        # Set window title based on source identifier or assign a letter
        if source_identifier:
            window_title: str = f"Summarize-{source_identifier}"
        else:
            window_letter: str = chr(65 + len(self.summarize_windows) - 1)
            window_title: str = f"Summarize-{window_letter}"
            
        new_window.Show(window_title)
        if pseudocode:
            new_window.set_pseudocode(pseudocode)

    def __open_main_widget(self) -> None:
        """
        Private method to open the main widget window.
        Creates the widget if it doesn't exist yet.
        """
        if not self.main_widget:
            self.main_widget = MainWidget()
        self.main_widget.Show("AIDA")

    def run(self, arg: int) -> None:
        """
        Run method called when the plugin is activated by hotkey or menu.
        Opens the main widget.
        
        Args:
            arg: Argument passed by IDA Pro (not used)
        """
        self.__open_main_widget()

    def term(self) -> None:
        """
        Termination method called when IDA Pro is closing or plugin is unloaded.
        Cleans up resources by unhooking the menu and clearing window references.
        """
        if self.menu:
            self.menu.unhook()
        self.summarize_windows.clear()
        return