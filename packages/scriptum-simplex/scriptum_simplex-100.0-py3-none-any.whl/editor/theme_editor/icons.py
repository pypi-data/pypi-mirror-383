"""
Material Design Icons for Theme Editor

Uses Unicode symbols that resemble Material Design icons.
"""

from typing import Dict


class MaterialIcons:
    """Material Design-style icons using Unicode symbols."""

    # File operations
    FOLDER_OPEN = "📁"  # folder_open
    SAVE = "💾"  # save
    DESCRIPTION = "📄"  # description
    REFRESH = "🔄"  # refresh
    CLOSE = "✕"  # close
    
    # Edit operations
    EDIT = "✎"  # edit
    DELETE = "🗑"  # delete
    ADD = "+"  # add
    REMOVE = "-"  # remove
    UNDO = "↶"  # undo
    REDO = "↷"  # redo
    
    # Navigation
    ARROW_BACK = "←"  # arrow_back
    ARROW_FORWARD = "→"  # arrow_forward
    ARROW_UP = "↑"  # arrow_upward
    ARROW_DOWN = "↓"  # arrow_downward
    EXPAND_MORE = "▼"  # expand_more
    EXPAND_LESS = "▲"  # expand_less
    
    # Content
    SETTINGS = "⚙"  # settings
    PALETTE = "🎨"  # palette
    VISIBILITY = "👁"  # visibility
    CODE = "{ }"  # code
    TEXT_FORMAT = "📝"  # text_format
    
    # Status
    CHECK = "✓"  # check
    ERROR = "✗"  # error
    WARNING = "⚠"  # warning
    INFO = "ℹ"  # info
    HELP = "?"  # help
    
    # UI Elements
    MENU = "☰"  # menu
    MORE_VERT = "⋮"  # more_vert
    MORE_HORIZ = "⋯"  # more_horiz
    SEARCH = "🔍"  # search
    FILTER = "▼"  # filter_list
    
    # Theme specific
    BRIGHTNESS = "☀"  # brightness_high
    CONTRAST = "◐"  # contrast
    COLOR_LENS = "🎨"  # color_lens
    FONT = "Aa"  # font_download
    
    @classmethod
    def get_all(cls) -> Dict[str, str]:
        """
        Get all icons as a dictionary.
        
        Returns:
            Dictionary mapping icon names to symbols
        """
        return {
            name: value
            for name, value in vars(cls).items()
            if not name.startswith('_') and isinstance(value, str)
        }


# Convenience access
ICONS = MaterialIcons()
