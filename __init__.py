"""
Quick Presets - Main Module
This file ensures the extension is properly loaded by ForgeUI/Automatic1111
"""

import os
import sys

# Add the scripts directory to the path if needed
scripts_dir = os.path.dirname(os.path.abspath(__file__))
if scripts_dir not in sys.path:
    sys.path.insert(0, scripts_dir)

# Import the main script
try:
    from scripts.preset_manager import QuickPresetsExtension, on_ui_tabs
except ImportError:
    # Fallback for different directory structures
    pass