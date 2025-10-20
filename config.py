"""
LiteFinPad Configuration Constants
===================================

Centralized configuration for all visual and behavioral constants.
This makes the codebase easier to maintain and customize.

Version: 1.0
Created: October 19, 2025
"""

# ============================================================================
# WINDOW DIMENSIONS
# ============================================================================

class Window:
    """Main window dimensions"""
    WIDTH = 700
    HEIGHT = 1000  # Increased from 850 for inline Quick Add section
    COMPACT_HEIGHT = 850  # Legacy compact height
    
class Dialog:
    """Dialog window dimensions"""
    # Add Expense Dialog (with number pad)
    ADD_EXPENSE_WIDTH = 400
    ADD_EXPENSE_HEIGHT = 670
    ADD_EXPENSE_WITH_NUMPAD_HEIGHT = 725  # Quick Add variant
    
    # Edit Expense Dialog
    EDIT_EXPENSE_WIDTH = 350
    EDIT_EXPENSE_HEIGHT = 250
    
    # About Dialog
    ABOUT_WIDTH = 450
    ABOUT_HEIGHT = 480

# ============================================================================
# COLORS
# ============================================================================

class Colors:
    """Color palette for the application"""
    
    # === Backgrounds ===
    BG_WHITE = '#ffffff'
    BG_LIGHT_GRAY = '#f0f0f0'
    BG_MEDIUM_GRAY = '#e0e0e0'
    BG_DARK_GRAY = '#d0d0d0'
    BG_BUTTON_DISABLED = '#D0D0D0'  # Gray when button is ON/disabled
    BG_DIALOG = '#f8f9fa'
    BG_TOTAL_ROW = '#E7E6E6'  # Export Excel total row
    
    # === Date Field (Dark Blue) ===
    DATE_BG = '#2E5C8A'
    DATE_FG = 'white'
    
    # === Text Colors ===
    TEXT_BLACK = '#1a1a1a'
    TEXT_GRAY_DARK = '#323130'
    TEXT_GRAY_MEDIUM = '#605e5c'
    TEXT_GRAY_LIGHT = '#888888'  # Future expenses
    TEXT_BROWN = '#8B4513'  # Recent expenses
    
    # === Accent Colors ===
    # Success/Green
    GREEN_PRIMARY = '#107c10'  # Total amount, Add button
    GREEN_HOVER = '#0e6b0e'
    GREEN_PRESSED = '#0c5a0c'
    
    # Info/Blue
    BLUE_PRIMARY = '#0078D4'  # Headers, links, progress labels
    BLUE_LINK = '#0078D4'  # Clickable links (About dialog, etc.)
    BLUE_NAVY = '#4A8FCE'  # Day/Week progress labels
    BLUE_SELECTED = '#0078d4'  # Treeview selection
    
    # Warning/Red
    RED_PRIMARY = '#8B0000'  # Daily average, largest expense
    
    # Alert/Orange
    ORANGE_PRIMARY = '#E67E00'  # Weekly pace
    
    # Trend/Purple
    PURPLE_PRIMARY = '#4A4A8A'  # Previous month, trend analysis
    
    # === Button States ===
    BUTTON_ACTIVE_BG = '#e0e0e0'
    BUTTON_PRESSED_BG = '#d0d0d0'

# ============================================================================
# FONTS
# ============================================================================

class Fonts:
    """Font configuration"""
    
    FAMILY = 'Segoe UI'
    
    # === Font Sizes ===
    SIZE_TINY = 9       # Small labels, tooltips, About dialog
    SIZE_SMALL = 10     # Standard labels, status
    SIZE_NORMAL = 11    # Entries, analytics
    SIZE_MEDIUM = 12    # Buttons, standard text
    SIZE_LARGE = 13     # Count labels
    SIZE_XLARGE = 14    # Bold headers
    SIZE_TITLE = 18     # Month label
    SIZE_HERO = 20      # About dialog title
    SIZE_HUGE = 22      # Main title (LiteFinPad)
    SIZE_MASSIVE = 38   # Total amount
    
    # === Common Font Tuples ===
    # Format: (family, size, style)
    TITLE = (FAMILY, SIZE_HUGE, 'bold')
    SUBTITLE = (FAMILY, SIZE_TITLE, 'bold')
    HERO_TOTAL = (FAMILY, SIZE_MASSIVE, 'bold')
    HEADER = (FAMILY, SIZE_XLARGE, 'bold')
    BUTTON = (FAMILY, SIZE_MEDIUM, 'bold')
    LABEL = (FAMILY, SIZE_SMALL)
    LABEL_SMALL = (FAMILY, SIZE_TINY)  # Size 9 for small labels
    ENTRY = (FAMILY, SIZE_NORMAL)
    TOOLTIP = (FAMILY, SIZE_TINY)
    LINK = (FAMILY, SIZE_TINY, 'underline')
    ABOUT_TITLE = (FAMILY, SIZE_HERO, 'bold')  # About dialog title (20pt bold)

# ============================================================================
# ANIMATION
# ============================================================================

class Animation:
    """Window animation parameters"""
    
    # Slide-out animation
    SLIDE_OUT_DURATION_MS = 200
    EASE_OUT_POWER = 1.3  # Custom ease-out curve (was 2.0 standard)
    FADE_START_PROGRESS = 0.6  # Start fading at 60% progress
    FADE_END_OPACITY = 0.3  # Fade to 30% opacity
    
    # Window positioning
    SCREEN_MARGIN = 20  # Pixels from screen edge

# ============================================================================
# UI COMPONENTS
# ============================================================================

class NumberPad:
    """Number pad widget configuration"""
    
    BUTTON_WIDTH = 2
    FONT_SIZE = 12
    FONT_WEIGHT = 'bold'
    PADDING = (8, 10)  # (horizontal, vertical)
    GRID_SPACING = 5  # Pixels between buttons
    FRAME_PADDING = 10  # Frame internal padding
    MAX_AMOUNT_LENGTH = 10  # 9999999.99 format

class TreeView:
    """Treeview/Table configuration"""
    
    # Row heights
    ROW_HEIGHT = 28
    
    # Font sizes
    HEADER_FONT_SIZE = 10
    BODY_FONT_SIZE = 10
    
    # Column widths (used in expense_table.py)
    COL_DATE_WIDTH = 120
    COL_DESCRIPTION_WIDTH = 350
    COL_AMOUNT_WIDTH = 120

class Export:
    """Export dialog and file configuration"""
    
    DIALOG_WIDTH = 400
    DIALOG_HEIGHT = 300
    
    # Excel export colors
    EXCEL_HEADER_BG = '#0078D4'
    EXCEL_HEADER_FG = 'white'
    EXCEL_TOTAL_BG = '#E7E6E6'

# ============================================================================
# VALIDATION
# ============================================================================

class Validation:
    """Input validation parameters"""
    
    MAX_AMOUNT_VALUE = 9999999.99
    MAX_AMOUNT_DECIMALS = 2
    MAX_DESCRIPTION_LENGTH = 200
    MIN_DESCRIPTION_LENGTH = 1

# ============================================================================
# APPLICATION INFO
# ============================================================================

class App:
    """Application metadata"""
    
    NAME = "LiteFinPad"
    TAGLINE = "Monthly Expense Tracker"
    DESCRIPTION = "A simple, offline expense tracker for Windows."
    LICENSE = "MIT License"
    BUILT_WITH = "Built with AI assistance (Cursor + Claude Sonnet 4)"
    GITHUB_URL = "https://github.com/aHuddini/LiteFinPad"
    OFFLINE_NOTICE = "100% offline - no internet connection required"

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def get_font(size, weight=None):
    """
    Get a font tuple with standard family.
    
    Args:
        size: Font size (use Fonts.SIZE_* constants)
        weight: Optional weight ('bold', 'italic', etc.)
    
    Returns:
        Tuple: (family, size) or (family, size, weight)
    """
    if weight:
        return (Fonts.FAMILY, size, weight)
    return (Fonts.FAMILY, size)

def get_window_geometry(width, height, x, y):
    """
    Format a geometry string for Tkinter.
    
    Args:
        width: Window width in pixels
        height: Window height in pixels
        x: X position
        y: Y position
    
    Returns:
        str: Formatted geometry string "WIDTHxHEIGHT+X+Y"
    """
    return f"{width}x{height}+{x}+{y}"

