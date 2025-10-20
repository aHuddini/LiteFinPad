"""
Dialog Helper Module
Provides reusable dialog creation and positioning utilities
"""

import tkinter as tk
from tkinter import ttk
import config


class DialogHelper:
    """Static helper methods for creating and managing dialogs"""
    
    @staticmethod
    def create_dialog(parent, title, width, height):
        """
        Creates a standard Toplevel dialog with common settings.
        
        Args:
            parent: Parent window
            title: Dialog title
            width: Dialog width in pixels
            height: Dialog height in pixels
            
        Returns:
            tk.Toplevel: Configured dialog window
        """
        dialog = tk.Toplevel(parent)
        dialog.title(title)
        dialog.resizable(False, False)
        dialog.transient(parent)
        dialog.configure(bg=config.Colors.BG_DIALOG)
        dialog.geometry(f"{width}x{height}")
        dialog.withdraw()  # Hide until fully configured
        return dialog
    
    @staticmethod
    def create_content_frame(dialog, padding="15"):
        """
        Creates a standard content frame for dialogs.
        
        Args:
            dialog: Parent dialog window
            padding: Padding around content (default: "15")
            
        Returns:
            ttk.Frame: Content frame
        """
        content_frame = ttk.Frame(dialog, padding=padding)
        content_frame.pack(fill=tk.BOTH, expand=True)
        return content_frame
    
    @staticmethod
    def center_on_parent(dialog, parent, dialog_width, dialog_height):
        """
        Centers the dialog over its parent window.
        
        Args:
            dialog: Dialog to position
            parent: Parent window
            dialog_width: Width of dialog
            dialog_height: Height of dialog
        """
        dialog.update_idletasks()
        parent_x = parent.winfo_x()
        parent_y = parent.winfo_y()
        parent_width = parent.winfo_width()
        parent_height = parent.winfo_height()
        
        x = parent_x + (parent_width // 2) - (dialog_width // 2)
        y = parent_y + (parent_height // 2) - (dialog_height // 2)
        
        dialog.geometry(f"+{x}+{y}")
    
    @staticmethod
    def position_lower_right(dialog, parent, dialog_width, dialog_height):
        """
        Positions the dialog in the lower-right corner relative to the parent, with screen boundary checks.
        
        Args:
            dialog: Dialog to position
            parent: Parent window
            dialog_width: Width of dialog
            dialog_height: Height of dialog
        """
        dialog.update_idletasks()
        screen_width = dialog.winfo_screenwidth()
        screen_height = dialog.winfo_screenheight()
        
        # Calculate position relative to parent's lower-right
        parent_x = parent.winfo_x()
        parent_y = parent.winfo_y()
        parent_width = parent.winfo_width()
        parent_height = parent.winfo_height()
        
        # Default position: perfectly snapped to lower-right of parent (no margins)
        x = parent_x + parent_width - dialog_width
        y = parent_y + parent_height - dialog_height
        
        # Adjust if dialog goes off screen (only then apply margins for safety)
        if x + dialog_width > screen_width:
            x = screen_width - dialog_width - config.Window.MARGIN_RIGHT
        if y + dialog_height > screen_height:
            y = screen_height - dialog_height - config.Window.MARGIN_BOTTOM
        if x < config.Window.MARGIN_LEFT:
            x = config.Window.MARGIN_LEFT
        if y < config.Window.MARGIN_TOP:
            y = config.Window.MARGIN_TOP
        
        dialog.geometry(f"+{x}+{y}")
    
    @staticmethod
    def position_right_of_parent(dialog, parent, dialog_width, dialog_height, gap=10):
        """
        Positions the dialog to the right of the parent window with intelligent fallbacks.
        
        Positioning logic:
        1. Try to position to the right of parent with gap
        2. If off-screen, try left of parent
        3. If still off-screen, center on screen
        
        Args:
            dialog: Dialog to position
            parent: Parent window
            dialog_width: Width of dialog
            dialog_height: Height of dialog
            gap: Gap between dialog and parent (default: 10)
        """
        dialog.update_idletasks()
        
        # Get parent position and size
        parent_x = parent.winfo_x()
        parent_y = parent.winfo_y()
        parent_width = parent.winfo_width()
        
        # Get screen dimensions
        screen_width = dialog.winfo_screenwidth()
        screen_height = dialog.winfo_screenheight()
        
        # Try to position to the right of main window
        x = parent_x + parent_width + gap
        y = parent_y  # Align with top of parent
        
        # Check if dialog would go off-screen to the right
        if x + dialog_width > screen_width:
            # Try positioning to the left of parent
            x = parent_x - dialog_width - gap
            
            # If still off-screen, center on screen
            if x < 0:
                x = (screen_width - dialog_width) // 2
                y = (screen_height - dialog_height) // 2
        
        dialog.geometry(f"+{x}+{y}")
    
    @staticmethod
    def bind_escape_to_close(dialog):
        """
        Binds the Escape key to close the dialog.
        
        Args:
            dialog: Dialog to bind
        """
        dialog.bind('<Escape>', lambda e: dialog.destroy())
    
    @staticmethod
    def bind_escape_with_cleanup(dialog, cleanup_callback):
        """
        Binds the Escape key to close the dialog with custom cleanup logic.
        
        This is useful for dialogs that need to perform cleanup before closing
        (e.g., resetting flags, canceling operations).
        
        Args:
            dialog: Dialog to bind
            cleanup_callback: Function to call when Escape is pressed (should handle dialog.destroy())
        """
        dialog.bind('<Escape>', lambda e: cleanup_callback())
    
    @staticmethod
    def show_dialog(dialog, grab_set=True, focus_set=True):
        """
        Shows the dialog and optionally grabs focus.
        
        Args:
            dialog: Dialog to show
            grab_set: Whether to grab modal focus (default: True)
            focus_set: Whether to set keyboard focus (default: True)
        """
        dialog.deiconify()
        if grab_set:
            dialog.grab_set()
        if focus_set:
            dialog.focus_set()

