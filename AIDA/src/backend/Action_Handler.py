# AIDA Action Handler module
# Handles actions triggered by the user in IDA Pro interface

from ida_kernwin import get_current_widget, get_custom_viewer_curline, read_selection, get_viewer_user_data, get_widget_title
from idaapi import plugin_t, action_handler_t, get_func_name, get_func, BADADDR
from ida_hexrays import decompile, get_widget_vdui
from ida_name import get_name_ea
from ida_lines import tag_remove
from re import findall, search
from ida_funcs import get_func

class ActionHandler(action_handler_t):
    """
    Handler for AIDA actions triggered in IDA Pro.
    Inherits from IDA Pro's action_handler_t class.
    Processes pseudocode and related functions for summarization.
    """
    def __init__(self, plugin: plugin_t) -> None:
        """
        Initialize the action handler.
        
        Args:
            plugin: Reference to the parent plugin instance
        """
        action_handler_t.__init__(self)
        self.plugin: plugin_t = plugin

    def __get_clean_pseudocode(self, vu) -> str:
        """
        Extract clean pseudocode from the decompiler view.
        Removes IDA's internal tags and empty lines.
        
        Args:
            vu: The vdui object from IDA Pro
            
        Returns:
            Cleaned pseudocode as a string
        """
        try:
            cfunc = vu.cfunc

            sv = cfunc.get_pseudocode()
            if sv:
                text: list = []
                for sline in sv:
                    clean_line = tag_remove(sline.line)
                    if clean_line.strip():
                        text.append(clean_line)
                return '\n'.join(text)
            return ""
        except Exception as e:
            print(f"[AIDA][ERROR] Error in get_clean_pseudocode: {str(e)}")
            return ""
            
    def __extract_sub_functions(self, pseudocode: str) -> set:
        """
        Extract references to sub_XXX functions in the pseudocode.
        
        Args:
            pseudocode: The pseudocode text to analyze
            
        Returns:
            Set of sub_XXX function names found in the pseudocode
        """
        pattern = r'sub_[0-9A-Fa-f]+'
        sub_funcs: set = set(findall(pattern, pseudocode))
        return sub_funcs
        
    def __get_function_pseudocode(self, func_name: str) -> str:
        """
        Get the pseudocode for a specific function by name.
        
        Args:
            func_name: Name of the function to decompile
            
        Returns:
            Cleaned pseudocode of the specified function as a string
        """
        try:
            # Get the address for the function
            func_addr = get_name_ea(0, func_name)
            if func_addr == BADADDR:
                return ""
                
            # Get the function object
            func = get_func(func_addr)
            if not func:
                return ""
                
            # Decompile the function
            cfunc = decompile(func)
            if not cfunc:
                return ""
                
            # Extract and clean the pseudocode
            sv = cfunc.get_pseudocode()
            if sv:
                text: list = []
                for sline in sv:
                    clean_line = tag_remove(sline.line)
                    if clean_line.strip():
                        text.append(clean_line)
                return '\n'.join(text)
            return ""
        except Exception as e:
            print(f"[AIDA][ERROR] Error getting pseudocode for {func_name}: {str(e)}")
            return ""
            
    def __get_all_related_pseudocode(self, primary_pseudocode: str) -> str:
        """
        Get pseudocode for all related functions referenced in the primary pseudocode.
        Builds a comprehensive view of the function and its called functions.
        
        Args:
            primary_pseudocode: The main pseudocode to analyze
            
        Returns:
            Combined pseudocode of the main function and all related functions
        """
        result: str = primary_pseudocode
        collected_funcs: set = set()

        # Extract all sub_XXX function references
        sub_funcs: set = self.__extract_sub_functions(primary_pseudocode)
        
        funcs_to_process: set = sub_funcs.copy()
        
        # Try to identify the main function name
        main_func_match = search(r'(sub_[0-9A-Fa-f]+)\s*\(', primary_pseudocode)
        main_func_name = main_func_match.group(1) if main_func_match else None
        
        if main_func_name:
            collected_funcs.add(main_func_name)
        
        # Process all referenced functions
        while funcs_to_process:
            current_func = funcs_to_process.pop()
            
            # Skip already processed functions
            if current_func in collected_funcs:
                continue
                
            collected_funcs.add(current_func)
            func_code = self.__get_function_pseudocode(current_func)
            
            # Add the function's pseudocode to the result
            if func_code:
                result += f"\n\n// Function: {current_func}\n{func_code}"
        
        return result

    def activate(self, ctx) -> int:
        """
        Activate method called when the action is triggered.
        Gets the current pseudocode and opens a summarize widget.
        
        Args:
            ctx: The action context
            
        Returns:
            1 to indicate successful handling
        """
        widget = get_current_widget()
        vu = get_widget_vdui(widget)
        if vu:
            try:
                # Get the title of the source window for identification
                source_window_title = get_widget_title(widget)

                identifier = ""
                if source_window_title:
                    match = search(r'Pseudocode-([A-Za-z0-9]+)', source_window_title)
                    if match:
                        identifier = match.group(1)
                
                # Get pseudocode and related functions
                primary_pseudocode: str = self.__get_clean_pseudocode(vu)
                if primary_pseudocode:
                    complete_pseudocode = self.__get_all_related_pseudocode(primary_pseudocode)
                    self.plugin.open_summarize_widget(complete_pseudocode, identifier)
            except Exception as e:
                print(f"[AIDA][ERROR] Error getting pseudocode: {str(e)}")
        return 1

    def update(self, ctx) -> int:
        """
        Update method to determine if the action should be available.
        Always returns 1 to make the action always available.
        
        Args:
            ctx: The action context
            
        Returns:
            1 to indicate the action is enabled
        """
        return 1