# AIDA Hooks module
# Handles UI hooks for integrating with IDA Pro's context menus

from idaapi import UI_Hooks, BWN_PSEUDOCODE, attach_action_to_popup, get_widget_type, SETMENU_APP

class ContextMenuHooks(UI_Hooks):
    """
    Hooks into IDA Pro UI events to add AIDA actions to context menus.
    Inherits from IDA Pro's UI_Hooks class.
    """
    def finish_populating_widget_popup(self, form, popup) -> None:
        """
        Called when IDA Pro finishes populating a widget's popup menu.
        Adds the AIDA action to the context menu for pseudocode windows.
        
        Args:
            form: The form/widget where the popup is being shown
            popup: The popup menu being populated
        """
        # Only add the action to pseudocode windows
        if get_widget_type(form) == BWN_PSEUDOCODE:
            action_name: str = "AIDA"
            # Attach the AIDA action to the popup menu
            attach_action_to_popup(form, popup, action_name, "AIDA", SETMENU_APP)