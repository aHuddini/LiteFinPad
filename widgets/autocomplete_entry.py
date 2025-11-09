"""
Auto-Complete Entry Widget
Tkinter Entry with dropdown suggestions for expense descriptions

Uses ttk.Combobox - simple and reliable, no auto-opening.
"""

import tkinter as tk
from tkinter import ttk
from typing import Callable, List, Dict, Optional
import config


class AutoCompleteEntry(ttk.Frame):
    """
    Entry widget with auto-complete dropdown suggestions.
    
    Uses ttk.Combobox - suggestions update as you type, but dropdown
    only opens when you press Down arrow or click the dropdown button.
    """
    
    def __init__(self, parent, get_suggestions_callback: Callable[[str], List[Dict]],
                 show_on_focus: bool = True, min_chars: int = 2, **kwargs):
        """
        Initialize auto-complete entry widget.
        
        Args:
            parent: Parent tkinter widget
            get_suggestions_callback: Function that returns suggestions for partial text
            show_on_focus: Whether to show top suggestions when field receives focus
            min_chars: Minimum characters before showing suggestions
            **kwargs: Additional arguments passed to underlying Combobox widget
        """
        super().__init__(parent)
        
        self.get_suggestions = get_suggestions_callback
        self.show_on_focus = show_on_focus
        self.min_chars = min_chars
        
        # Use ttk.Combobox
        self.entry_var = tk.StringVar()
        entry_font = kwargs.pop('font', config.Fonts.ENTRY)
        
        self.combo = ttk.Combobox(
            self,
            textvariable=self.entry_var,
            font=entry_font,
            state='normal',
            **kwargs
        )
        self.combo.pack(fill=tk.X)
        
        # State tracking
        self._updating = False
        
        # Bind events
        self.entry_var.trace('w', self._on_text_change)
        self.combo.bind('<<ComboboxSelected>>', self._on_selection)
        self.combo.bind('<KeyPress>', self._on_key_press)
        self.combo.bind('<Button-1>', self._on_button_click)
        self.combo.bind('<FocusIn>', self._on_focus_in)
        
        # Access to underlying entry for compatibility
        self.entry = self.combo
    
    def get(self):
        """Get the current entry value"""
        return self.entry_var.get()
    
    def focus_set(self):
        """Focus the entry widget"""
        return self.combo.focus_set()
    
    def _on_text_change(self, *args):
        """Handle text change - update suggestions (manual dropdown open only)"""
        if self._updating:
            return
        
        text = self.entry_var.get()
        text_stripped = text.strip()
        
        # If text is too short, clear suggestions
        if len(text_stripped) < self.min_chars:
            self.combo['values'] = []
            return
        
        # Get suggestions
        try:
            suggestions = self.get_suggestions(text_stripped)
        except TypeError:
            suggestions = self.get_suggestions(text_stripped)
        except Exception:
            suggestions = []
        
        # Update combobox values (user opens dropdown manually with Down arrow or click)
        if suggestions:
            suggestion_texts = [s['text'] for s in suggestions]
            self.combo['values'] = suggestion_texts
        else:
            self.combo['values'] = []
    
    
    def _on_selection(self, event):
        """Handle selection from dropdown"""
        # User selected - prevent text change from retriggering
        self._updating = True
        self.combo.after(100, lambda: setattr(self, '_updating', False))
    
    def _on_focus_in(self, event):
        """Load top suggestions when field receives focus (if empty)"""
        if not self.show_on_focus:
            return
        
        text = self.entry_var.get().strip()
        if not text:
            # Load top suggestions if empty
            self._load_top_suggestions()
    
    def _load_top_suggestions(self):
        """Load top suggestions for empty field"""
        if self.combo['values']:
            return  # Already loaded
        
        try:
            suggestions = self.get_suggestions("", limit=5)
        except TypeError:
            suggestions = self.get_suggestions("")
            suggestions = suggestions[:5] if suggestions else []
        
        if suggestions:
            suggestion_texts = [s['text'] for s in suggestions]
            self.combo['values'] = suggestion_texts
    
    def _on_button_click(self, event):
        """Handle click on combobox - ensure values are loaded before dropdown opens"""
        # Get click position to detect if clicking dropdown arrow
        widget_width = self.combo.winfo_width()
        click_x = event.x
        
        # If clicking on dropdown arrow (right side), ensure values are loaded
        if click_x > widget_width - 20:
            text = self.entry_var.get().strip()
            if not self.combo['values']:
                # No values loaded - load suggestions based on current text
                if len(text) >= self.min_chars:
                    # Trigger text change to load filtered suggestions
                    self._on_text_change()
                else:
                    # Load top suggestions for empty/short text
                    self._load_top_suggestions()
    
    def _on_key_press(self, event):
        """Handle key press - ensure suggestions are loaded before dropdown opens"""
        keysym = event.keysym
        if keysym == 'Down':
            # Ensure dropdown has suggestions before opening
            text = self.entry_var.get().strip()
            if not self.combo['values']:
                # No values loaded - load suggestions
                if len(text) >= self.min_chars:
                    # Trigger text change to load filtered suggestions
                    self._on_text_change()
                else:
                    # Load top suggestions for empty/short text
                    self._load_top_suggestions()
    
    @property
    def dropdown_visible(self):
        """Check if dropdown is visible - always return False for simplicity"""
        # Since we don't auto-open, we don't need to track this
        # The dialog's Return handler will just work normally
        return False
    
    def bind(self, event, handler, add=None):
        """Bind event to underlying combobox widget"""
        if add:
            return self.combo.bind(event, handler, add=add)
        return self.combo.bind(event, handler)
    
    def config(self, **kwargs):
        """Configure underlying combobox widget"""
        return self.combo.config(**kwargs)
    
    def set(self, value):
        """Set entry value"""
        self._updating = True
        self.entry_var.set(value)
        self._updating = False
    
    def grid(self, **kwargs):
        """Forward grid() to frame"""
        super().grid(**kwargs)
    
    def pack(self, **kwargs):
        """Forward pack() to frame"""
        super().pack(**kwargs)
