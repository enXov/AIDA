# Main entry point for the AIDA plugin
# This file is referenced in ida-plugin.json and serves as the entry point for IDA Pro

from src.backend.AIDA_Plugin import AIDAPlugin

def PLUGIN_ENTRY() -> AIDAPlugin:
    """
    Required function for IDA Pro plugins.
    Returns an instance of AIDAPlugin class.
    This function is called by IDA Pro when loading the plugin.
    """
    return AIDAPlugin()