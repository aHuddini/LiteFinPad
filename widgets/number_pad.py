"""
NumberPad Widget for LiteFinPad.

Provides a reusable financial number pad for amount entry.
"""

import tkinter as tk
from tkinter import ttk
import config


class NumberPadWidget(ttk.LabelFrame):
    """
    Financial number pad widget for amount entry.
    
    Features:
    - 3x4 button grid (0-9, decimal point, clear)
    - Smart decimal handling (only one decimal point allowed)
    - Automatic "0." insertion when decimal pressed on empty field
    - Max length validation
    - Decimal places limit (default: 2)
    - Clean, compact styling
    
    Usage:
        amount_var = tk.StringVar()
        number_pad = NumberPadWidget(parent, amount_var)
        number_pad.pack(fill=tk.X, pady=(0, 10))
    
    Args:
        parent: Parent widget
        string_var: tk.StringVar to bind to
        max_length: Maximum characters allowed (default: 10 for 9999999.99)
        decimal_places: Maximum decimal places (default: 2)
        **kwargs: Additional arguments passed to ttk.LabelFrame
    """
    
    def __init__(self, parent, string_var, max_length=config.NumberPad.MAX_AMOUNT_LENGTH, decimal_places=2, **kwargs):
        """Initialize the NumberPad widget."""
        # Set default kwargs if not provided
        if 'text' not in kwargs:
            kwargs['text'] = ""
        if 'padding' not in kwargs:
            kwargs['padding'] = str(config.NumberPad.FRAME_PADDING)
        
        super().__init__(parent, **kwargs)
        
        self.string_var = string_var
        self.max_length = max_length
        self.decimal_places = decimal_places
        
        self._create_ui()
    
    def _create_ui(self):
        """Create the number pad UI."""
        # Configure button style
        style = ttk.Style()
        style.configure("NumPad.TButton", 
                       font=(config.Fonts.FAMILY, config.NumberPad.FONT_SIZE, config.NumberPad.FONT_WEIGHT),
                       padding=config.NumberPad.PADDING)
        
        # Button layout: 3x4 grid
        button_layout = [
            ['7', '8', '9'],
            ['4', '5', '6'],
            ['1', '2', '3'],
            ['0', '.', 'C']
        ]
        
        # Configure column weights for equal distribution
        for col in range(3):
            self.columnconfigure(col, weight=1)
        
        # Create buttons
        for row_idx, row in enumerate(button_layout):
            for col_idx, btn_text in enumerate(row):
                if btn_text == 'C':
                    # Clear button
                    btn = ttk.Button(
                        self, 
                        text=btn_text, 
                        command=self._on_clear,
                        style="NumPad.TButton",
                        width=config.NumberPad.BUTTON_WIDTH
                    )
                else:
                    # Number/decimal button
                    btn = ttk.Button(
                        self,
                        text=btn_text,
                        command=lambda t=btn_text: self._on_button_click(t),
                        style="NumPad.TButton",
                        width=config.NumberPad.BUTTON_WIDTH
                    )
                
                btn.grid(row=row_idx, column=col_idx, padx=config.NumberPad.GRID_SPACING, pady=config.NumberPad.GRID_SPACING, sticky=(tk.W, tk.E))
    
    def _on_button_click(self, value):
        """
        Handle number pad button clicks.
        
        Args:
            value: Button value ('0'-'9' or '.')
        """
        current = self.string_var.get()
        
        # Handle decimal point
        if value == '.':
            # Only allow one decimal point
            if '.' not in current:
                if not current:
                    # Auto-add "0." if field is empty
                    self.string_var.set('0.')
                else:
                    self.string_var.set(current + '.')
            return
        
        # Handle digits (0-9)
        # Check if adding this digit would exceed decimal places limit
        if '.' in current:
            integer_part, decimal_part = current.split('.')
            if len(decimal_part) >= self.decimal_places:
                return  # Already at max decimal places
        
        # Max length validation
        if len(current) >= self.max_length:
            return
        
        # Special case: Replace leading "0" with the digit (but not "0.")
        if current == '0':
            self.string_var.set(value)
        else:
            self.string_var.set(current + value)
    
    def _on_clear(self):
        """Clear the linked variable."""
        self.string_var.set('')
    
    def configure_style(self, **style_options):
        """
        Configure the button style.
        
        Allows external customization of button appearance.
        
        Args:
            **style_options: Style configuration options
                            (e.g., font=("Arial", 14), padding=(10, 12))
        """
        style = ttk.Style()
        style.configure("NumPad.TButton", **style_options)

