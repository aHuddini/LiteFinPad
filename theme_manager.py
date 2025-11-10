"""
Theme Manager Module for LiteFinPad

Provides centralized theme management and color scheme switching.
Supports light mode (default) and dark mode (experimental, enabled via settings.ini).

Usage:
    theme_manager = ThemeManager()
    is_dark = theme_manager.is_dark_mode()
    colors = theme_manager.get_colors()
"""

import customtkinter as ctk
from settings_manager import get_settings_manager
from error_logger import log_info, log_warning


class ThemeManager:
    """
    Manages theme switching and provides color schemes.
    
    Features:
    - Reads theme setting from settings.ini
    - Provides theme-aware color schemes
    - Applies CustomTkinter appearance mode
    - Supports both light and dark modes
    """
    
    def __init__(self):
        """Initialize theme manager and load theme setting."""
        self.settings = get_settings_manager()
        self._is_dark_mode = self._load_theme_setting()
        self._apply_customtkinter_theme()
        
        mode_str = "dark" if self._is_dark_mode else "light"
        log_info(f"Theme Manager initialized: {mode_str} mode")
    
    def _load_theme_setting(self) -> bool:
        """
        Load dark mode setting from settings.ini.
        
        Returns:
            bool: True if dark mode is enabled, False otherwise (default)
        """
        try:
            dark_mode = self.settings.get(
                'Theme',
                'dark_mode',
                default=False,
                value_type=bool
            )
            return dark_mode
        except Exception as e:
            # If Theme section doesn't exist, default to light mode
            log_warning(f"Could not load theme setting, defaulting to light mode: {e}")
            return False
    
    def _apply_customtkinter_theme(self):
        """Apply CustomTkinter appearance mode based on current theme."""
        try:
            mode = "dark" if self._is_dark_mode else "light"
            ctk.set_appearance_mode(mode)
            log_info(f"CustomTkinter appearance mode set to: {mode}")
        except Exception as e:
            log_warning(f"Could not set CustomTkinter appearance mode: {e}")
    
    def is_dark_mode(self) -> bool:
        """
        Check if dark mode is enabled.
        
        Returns:
            bool: True if dark mode is enabled, False for light mode
        """
        return self._is_dark_mode
    
    def get_colors(self):
        """
        Get current color scheme based on theme.
        
        Returns:
            Colors or DarkModeColors: Color scheme class instance
        """
        if self._is_dark_mode:
            from config import DarkModeColors
            return DarkModeColors()
        else:
            from config import Colors
            return Colors()
    
    def get_archive_tint(self):
        """
        Get archive mode tint color based on current theme.
        
        Returns:
            str: Hex color code for archive mode tint
        """
        if self._is_dark_mode:
            # Dark mode archive tint: darker purple/lavender that works on dark backgrounds
            return '#3d2d4d'  # Dark purple-lavender tint
        else:
            # Light mode archive tint: light lavender
            from config import Colors
            return Colors.BG_ARCHIVE_TINT

