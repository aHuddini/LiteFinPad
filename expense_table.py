"""
Expense Table Management Module for LiteFinPad

This module handles all expense table functionality including:
- Display and management of expense data
- Add/Edit/Delete expense operations
- Data validation and error handling
- Modern UI components for expense management
"""

import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
from datetime import datetime
from typing import List, Dict, Optional, Callable
from validation import InputValidation, ValidationPresets, ValidationResult
import config
from dialog_helpers import DialogHelper
from widgets import CollapsibleDateCombobox, AutoCompleteEntry
from date_utils import DateUtils
from settings_manager import get_settings_manager


class ExpenseData:
    """Data model for expense entries"""
    
    def __init__(self, date: str, amount: float, description: str):
        self.date = date
        self.amount = amount
        self.description = description
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization"""
        return {
            'date': self.date,
            'amount': self.amount,
            'description': self.description
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'ExpenseData':
        """Create from dictionary"""
        return cls(data['date'], data['amount'], data['description'])
    
    def __str__(self) -> str:
        return f"{self.date}: ${self.amount:.2f} - {self.description}"


class ExpenseTableManager:
    """Manages the expense table display and operations"""
    
    def __init__(self, parent_frame: ttk.Frame, on_expense_change: Optional[Callable] = None, theme_manager=None):
        self.parent_frame = parent_frame
        self.on_expense_change = on_expense_change
        self.theme_manager = theme_manager
        self.expenses: List[ExpenseData] = []
        
        # Get theme-aware colors
        self.colors = theme_manager.get_colors() if theme_manager else config.Colors
        
        # Sort state tracking
        self.sort_column = config.TreeView.DEFAULT_SORT_COLUMN  # Default: 'Date'
        self.sort_order = config.TreeView.DEFAULT_SORT_ORDER    # Default: 'desc'
        self._load_sort_preferences()
        
        # Pagination state tracking
        self.current_page = 1
        self.items_per_page = 15
        
        # Create the table frame
        self.setup_table()
        
    def setup_table(self):
        """Setup the expense table with modern styling"""
        # Configure LabelFrame style to match parent background (expense_list_frame)
        is_dark = self.theme_manager.is_dark_mode() if self.theme_manager else False
        frame_bg = self.colors.BG_SECONDARY if is_dark else self.colors.BG_LIGHT_GRAY
        
        # Create style for table frame to match parent background
        style = ttk.Style()
        style.configure("TableContainer.TLabelframe", 
                       background=frame_bg,
                       bordercolor=self.colors.BG_DARK_GRAY,
                       borderwidth=1)  # 1px border
        style.configure("TableContainer.TLabelframe.Label", 
                       background=frame_bg)
        
        # Create main container frame with custom style
        self.table_frame = ttk.LabelFrame(self.parent_frame, text="", padding="10", style="TableContainer.TLabelframe")
        self.table_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))  # Reduced bottom padding
        
        # Configure grid weights
        self.parent_frame.columnconfigure(0, weight=1)
        self.parent_frame.rowconfigure(0, weight=1)
        self.table_frame.columnconfigure(0, weight=1)
        self.table_frame.rowconfigure(0, weight=1)
        
        # Create treeview with modern styling
        columns = ("Date", "Amount", "Description")
        self.tree = ttk.Treeview(
            self.table_frame, 
            columns=columns, 
            show="headings", 
            height=11,  # Increased from 8 to show more entries
            style="Modern.Treeview"
        )
        
        # Configure columns with click handlers for sorting
        self.tree.heading("Date", text="Date", anchor="center", command=lambda: self._on_column_click("Date"))
        self.tree.heading("Amount", text="Amount", anchor="e", command=lambda: self._on_column_click("Amount"))
        self.tree.heading("Description", text="Description", anchor="w", command=lambda: self._on_column_click("Description"))
        
        # Update headers to show current sort indicator
        self._update_column_headers()
        
        # Set column widths and properties (wider date column for "(Future)" text)
        self.tree.column("Date", width=180, minwidth=160, anchor="center")
        self.tree.column("Amount", width=120, minwidth=100, anchor="e")  # Wider for 5-digit amounts
        self.tree.column("Description", width=230, minwidth=140, anchor="w")  # Reduced to balance with Date/Amount
        
        # Configure modern styling with theme-aware colors
        # Use grayish navy blue for table background in dark mode only (subtle but noticeable)
        # Keep original white/light gray in light mode
        is_dark = self.theme_manager.is_dark_mode() if self.theme_manager else False
        if is_dark and hasattr(self.colors, 'BG_TABLE'):
            table_bg = self.colors.BG_TABLE  # Grayish navy blue in dark mode
        else:
            table_bg = self.colors.BG_WHITE if not is_dark else self.colors.BG_SECONDARY  # Original colors
        table_fg = self.colors.TEXT_BLACK  # Theme-aware: TEXT_BLACK in light, TEXT_PRIMARY in dark
        
        style = ttk.Style()
        style.configure("Modern.Treeview", 
                       font=config.get_font(config.Fonts.SIZE_SMALL),
                       rowheight=config.TreeView.ROW_HEIGHT,
                       background=table_bg,
                       foreground=table_fg,
                       fieldbackground=table_bg)
        style.configure("Modern.Treeview.Heading",
                       font=config.get_font(config.TreeView.HEADER_FONT_SIZE, 'bold'),
                       background=self.colors.BG_LIGHT_GRAY,
                       foreground=table_fg)
        style.map("Modern.Treeview", 
                 background=[('selected', self.colors.BLUE_SELECTED)],
                 foreground=[('selected', 'white')])
        
        # Add treeview directly to table frame
        self.tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(self.table_frame, orient="vertical", command=self.tree.yview)
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        # Configure tags for future expenses with theme-aware color
        self.tree.tag_configure('future', foreground=self.colors.TEXT_GRAY_LIGHT, font=config.get_font(config.Fonts.SIZE_SMALL, 'italic'))
        
        # Bind events
        self.tree.bind("<Button-3>", self.show_context_menu)  # Right-click
        self.tree.bind("<Double-1>", self.edit_selected_expense)  # Double-click
        self.tree.bind("<Delete>", self.delete_selected_expense)  # Delete key
        
        # Add status bar
        # Configure frame background to match parent (expense_list_frame) - BG_SECONDARY in dark, BG_LIGHT_GRAY in light
        status_frame_bg = self.colors.BG_SECONDARY if is_dark else self.colors.BG_LIGHT_GRAY
        status_style = ttk.Style()
        status_style.configure("TableStatus.TFrame", background=status_frame_bg)
        
        self.status_frame = ttk.Frame(self.table_frame, style="TableStatus.TFrame")
        self.status_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(5, 0))
        
        # Configure ttk.Style for status and pagination labels (ttk.Label requires style configuration)
        status_text_color = self.colors.TEXT_BLACK  # Theme-aware: TEXT_BLACK in light, TEXT_PRIMARY in dark
        status_style.configure("TableStatus.TLabel", 
                             foreground=status_text_color,
                             background=status_frame_bg,  # Match frame background
                             font=config.Fonts.LABEL)
        
        self.status_label = ttk.Label(self.status_frame, text="No expenses", style="TableStatus.TLabel")
        self.status_label.pack(side=tk.LEFT)
        
        # Add pagination controls (right side)
        # Pagination frame should also match the background
        self.pagination_frame = ttk.Frame(self.status_frame, style="TableStatus.TFrame")
        self.pagination_frame.pack(side=tk.RIGHT)
        
        self.first_page_btn = ttk.Button(self.pagination_frame, text="◄◄", width=3, command=self.first_page)
        self.first_page_btn.pack(side=tk.LEFT, padx=(0, 2))
        
        self.prev_page_btn = ttk.Button(self.pagination_frame, text="◄", width=3, command=self.prev_page)
        self.prev_page_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        self.page_label = ttk.Label(self.pagination_frame, text="1/1", style="TableStatus.TLabel")
        self.page_label.pack(side=tk.LEFT, padx=(0, 5))
        
        self.next_page_btn = ttk.Button(self.pagination_frame, text="►", width=3, command=self.next_page)
        self.next_page_btn.pack(side=tk.LEFT, padx=(0, 2))
        
        self.last_page_btn = ttk.Button(self.pagination_frame, text="►►", width=3, command=self.last_page)
        self.last_page_btn.pack(side=tk.LEFT)
    
    def _load_sort_preferences(self):
        """Load sort preferences from settings"""
        settings = get_settings_manager()
        self.sort_column = settings.get('Table', 'sort_column', 
                                        default=config.TreeView.DEFAULT_SORT_COLUMN)
        self.sort_order = settings.get('Table', 'sort_order', 
                                       default=config.TreeView.DEFAULT_SORT_ORDER)
    
    def _save_sort_preferences(self):
        """Save sort preferences to settings"""
        settings = get_settings_manager()
        settings.set('Table', 'sort_column', self.sort_column)
        settings.set('Table', 'sort_order', self.sort_order)
    
    def _on_column_click(self, column: str):
        """Handle column header click for sorting"""
        # Toggle sort order if clicking the same column, otherwise reset to descending
        if self.sort_column == column:
            self.sort_order = 'asc' if self.sort_order == 'desc' else 'desc'
        else:
            self.sort_column = column
            self.sort_order = 'desc'  # Default to descending for new column
        
        # Save preferences
        self._save_sort_preferences()
        
        # Update UI
        self._update_column_headers()
        self.refresh_display()
    
    def _update_column_headers(self):
        """Update column headers to show sort indicators"""
        for col in ["Date", "Amount", "Description"]:
            if col == self.sort_column:
                # Add sort indicator to active column
                icon = config.TreeView.SORT_DESCENDING_ICON if self.sort_order == 'desc' else config.TreeView.SORT_ASCENDING_ICON
                header_text = f"{col} {icon}"
            else:
                header_text = col
            
            # Preserve anchor alignment when updating text
            if col == "Date":
                self.tree.heading(col, text=header_text, anchor="center")
            elif col == "Amount":
                self.tree.heading(col, text=header_text, anchor="e")
            else:  # Description
                self.tree.heading(col, text=header_text, anchor="w")
    
    def _sort_expenses(self, expenses: List[ExpenseData]) -> List[ExpenseData]:
        """Sort expenses based on current sort column and order"""
        reverse = (self.sort_order == 'desc')
        
        if self.sort_column == "Date":
            # Sort by date (datetime object)
            return sorted(expenses, key=lambda x: DateUtils.parse_date(x.date) or datetime.min, reverse=reverse)
        elif self.sort_column == "Amount":
            # Sort by amount (float)
            return sorted(expenses, key=lambda x: x.amount, reverse=reverse)
        elif self.sort_column == "Description":
            # Sort by description (case-insensitive alphabetical)
            return sorted(expenses, key=lambda x: x.description.lower(), reverse=reverse)
        else:
            # Fallback to date descending
            return sorted(expenses, key=lambda x: DateUtils.parse_date(x.date) or datetime.min, reverse=True)
    
    def _update_pagination_controls(self, total_pages: int):
        """Update pagination control visibility and state"""
        # Update page label with theme-aware colors
        is_dark = self.theme_manager.is_dark_mode() if self.theme_manager else False
        status_text_color = self.colors.TEXT_BLACK  # Theme-aware: TEXT_BLACK in light, TEXT_PRIMARY in dark
        
        # Update ttk.Style for page label
        status_style = ttk.Style()
        status_style.configure("TableStatus.TLabel", 
                             foreground=status_text_color,
                             background=self.colors.BG_LIGHT_GRAY,
                             font=config.Fonts.LABEL)
        
        self.page_label.config(text=f"{self.current_page}/{total_pages}", style="TableStatus.TLabel")
        
        # Enable/disable buttons based on current page
        if total_pages <= 1:
            # Hide pagination when only 1 page
            self.pagination_frame.pack_forget()
        else:
            # Show pagination
            self.pagination_frame.pack(side=tk.RIGHT)
            
            # First page and previous buttons
            if self.current_page <= 1:
                self.first_page_btn.config(state=tk.DISABLED)
                self.prev_page_btn.config(state=tk.DISABLED)
            else:
                self.first_page_btn.config(state=tk.NORMAL)
                self.prev_page_btn.config(state=tk.NORMAL)
            
            # Last page and next buttons
            if self.current_page >= total_pages:
                self.next_page_btn.config(state=tk.DISABLED)
                self.last_page_btn.config(state=tk.DISABLED)
            else:
                self.next_page_btn.config(state=tk.NORMAL)
                self.last_page_btn.config(state=tk.NORMAL)
    
    def first_page(self):
        """Go to first page"""
        self.current_page = 1
        self.refresh_display()
    
    def prev_page(self):
        """Go to previous page"""
        if self.current_page > 1:
            self.current_page -= 1
            self.refresh_display()
    
    def next_page(self):
        """Go to next page"""
        total_pages = max(1, (len(self.expenses) + self.items_per_page - 1) // self.items_per_page)
        if self.current_page < total_pages:
            self.current_page += 1
            self.refresh_display()
    
    def last_page(self):
        """Go to last page"""
        total_pages = max(1, (len(self.expenses) + self.items_per_page - 1) // self.items_per_page)
        self.current_page = total_pages
        self.refresh_display()
        
    def load_expenses(self, expenses_data: List[Dict]):
        """Load expenses from data"""
        self.expenses = [ExpenseData.from_dict(exp) for exp in expenses_data]
        self.refresh_display()
        
    def add_expense(self, expense: ExpenseData):
        """Add a new expense"""
        self.expenses.append(expense)
        self.refresh_display()
        if self.on_expense_change:
            self.on_expense_change()
            
    def update_expense(self, index: int, expense: ExpenseData):
        """Update an existing expense"""
        if 0 <= index < len(self.expenses):
            self.expenses[index] = expense
            self.refresh_display()
            if self.on_expense_change:
                self.on_expense_change()
                
    def delete_expense(self, index: int):
        """Delete an expense by index"""
        if 0 <= index < len(self.expenses):
            del self.expenses[index]
            self.refresh_display()
            if self.on_expense_change:
                self.on_expense_change()
                
    def get_expenses(self) -> List[ExpenseData]:
        """Get all expenses"""
        return self.expenses.copy()
        
    def get_total_amount(self) -> float:
        """Get total amount of all expenses"""
        return sum(expense.amount for expense in self.expenses)
        
    def refresh_display(self):
        """Refresh the table display efficiently"""
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        # Add expenses with pagination
        if self.expenses:
            # Apply user's sort preference
            sorted_expenses = self._sort_expenses(self.expenses)
            
            # Calculate pagination
            total_expenses = len(sorted_expenses)
            total_pages = max(1, (total_expenses + self.items_per_page - 1) // self.items_per_page)
            
            # Ensure current page is valid
            if self.current_page > total_pages:
                self.current_page = total_pages
            if self.current_page < 1:
                self.current_page = 1
            
            # Get expenses for current page
            start_idx = (self.current_page - 1) * self.items_per_page
            end_idx = start_idx + self.items_per_page
            page_expenses = sorted_expenses[start_idx:end_idx]
            
            today = datetime.now().date()
            
            for expense in page_expenses:
                # Format date for display
                date_obj = DateUtils.parse_date(expense.date)
                if date_obj:
                    formatted_date = date_obj.strftime("%m/%d/%Y")
                    
                    # Check if this is a future expense
                    is_future = date_obj.date() > today
                    if is_future:
                        formatted_date = formatted_date + " (Future)"
                else:
                    formatted_date = expense.date
                    is_future = False
                
                # Insert with 'future' tag if applicable
                if is_future:
                    self.tree.insert("", "end", values=(
                        formatted_date,
                        f"${expense.amount:.2f}",
                        expense.description
                    ), tags=('future',))
                else:
                    self.tree.insert("", "end", values=(
                        formatted_date,
                        f"${expense.amount:.2f}",
                        expense.description
                    ))
            
            # Update status - only count expenses up to today
            total = sum(e.amount for e in self.expenses 
                       if (dt := DateUtils.parse_date(e.date)) and dt.date() <= today)
            count = len(self.expenses)
            future_count = sum(1 for e in self.expenses 
                             if (dt := DateUtils.parse_date(e.date)) and dt.date() > today)
            
            # Update status label with theme-aware colors
            is_dark = self.theme_manager.is_dark_mode() if self.theme_manager else False
            status_text_color = self.colors.TEXT_BLACK  # Theme-aware: TEXT_BLACK in light, TEXT_PRIMARY in dark
            
            # Update ttk.Style for status label
            status_style = ttk.Style()
            status_style.configure("TableStatus.TLabel", 
                                 foreground=status_text_color,
                                 background=self.colors.BG_LIGHT_GRAY,
                                 font=config.Fonts.LABEL)
            
            if future_count > 0:
                self.status_label.config(text=f"{count} expenses ({future_count} future)", style="TableStatus.TLabel")
            else:
                self.status_label.config(text=f"{count} expenses", style="TableStatus.TLabel")
            
            # Update pagination controls
            self._update_pagination_controls(total_pages)
        else:
            # Show placeholder
            self.tree.insert("", "end", values=(
                "No expenses",
                "$0.00",
                "Add your first expense!"
            ))
            # Update status label with theme-aware colors
            is_dark = self.theme_manager.is_dark_mode() if self.theme_manager else False
            status_text_color = self.colors.TEXT_BLACK  # Theme-aware: TEXT_BLACK in light, TEXT_PRIMARY in dark
            
            # Update ttk.Style for status label
            status_style = ttk.Style()
            status_style.configure("TableStatus.TLabel", 
                                 foreground=status_text_color,
                                 background=self.colors.BG_LIGHT_GRAY,
                                 font=config.Fonts.LABEL)
            
            self.status_label.config(text="No expenses", style="TableStatus.TLabel")
            
            # Hide pagination when no expenses
            self._update_pagination_controls(1)
            
    def show_context_menu(self, event):
        """Show context menu for expense management"""
        # Select the item under the cursor
        item = self.tree.identify_row(event.y)
        if item:
            self.tree.selection_set(item)
            
            # Create context menu
            context_menu = tk.Menu(self.parent_frame.winfo_toplevel(), tearoff=0)
            
            # Primary action at top
            context_menu.add_command(label="Edit Expense", command=self.edit_selected_expense)
            
            # Visual separator
            context_menu.add_separator()
            
            # Utility actions in middle
            context_menu.add_command(label="Copy Amount", command=self.copy_amount)
            context_menu.add_command(label="Copy Description", command=self.copy_description)
            
            # Visual separator before dangerous action
            context_menu.add_separator()
            
            # Dangerous action at bottom with visual warning
            context_menu.add_command(
                label="Delete Expense",
                command=self.delete_selected_expense,
                foreground="red",
                font=("Segoe UI", 9, "bold")
            )
            
            # Show context menu
            try:
                context_menu.tk_popup(event.x_root, event.y_root)
            finally:
                context_menu.grab_release()
                
    def edit_selected_expense(self, event=None):
        """Edit the selected expense"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning(config.Messages.TITLE_NO_SELECTION, config.Messages.NO_SELECTION_EDIT)
            return
            
        # Get the selected item
        item = selection[0]
        values = self.tree.item(item, 'values')
        
        if not values or values[0] == "No expenses":
            return
            
        # Find the expense index
        expense_index = self.find_expense_index(values)
        if expense_index is None:
            messagebox.showerror(config.Messages.TITLE_ERROR, "Could not find expense to edit.")
            return
            
        # Open edit dialog with theme_manager
        expense = self.expenses[expense_index]
        dialog = ExpenseEditDialog(
            self.parent_frame.winfo_toplevel(), 
            expense, 
            lambda new_expense: self.update_expense(expense_index, new_expense),
            theme_manager=self.theme_manager
        )
        
    def delete_selected_expense(self, event=None):
        """Delete the selected expense"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning(config.Messages.TITLE_NO_SELECTION, config.Messages.NO_SELECTION_DELETE)
            return
            
        # Get the selected item
        item = selection[0]
        values = self.tree.item(item, 'values')
        
        if not values or values[0] == "No expenses":
            return
            
        # Find the expense index
        expense_index = self.find_expense_index(values)
        if expense_index is None:
            messagebox.showerror(config.Messages.TITLE_ERROR, "Could not find expense to delete.")
            return
            
        # Confirm deletion
        expense = self.expenses[expense_index]
        result = messagebox.askyesno(
            config.Messages.TITLE_DELETE_CONFIRM, 
            f"Are you sure you want to delete this expense?\n\n{expense}"
        )
        if result:
            self.delete_expense(expense_index)
            
    def find_expense_index(self, values) -> Optional[int]:
        """Find expense index from tree values"""
        if not values or values[0] == "No expenses":
            return None
            
        # Convert display date back to storage format
        display_date = values[0]
        amount_str = values[1].replace('$', '')
        description = values[2]
        
        # Try to convert display date (10/12/2025) back to storage format (YYYY-MM-DD)
        try:
            if '/' in display_date and len(display_date.split('/')) == 3:
                # Format: MM/DD/YYYY -> YYYY-MM-DD
                month, day, year = display_date.split('/')
                storage_date = f"{year}-{month.zfill(2)}-{day.zfill(2)}"
            elif ',' in display_date:
                # Format: Oct 12, 2025 -> YYYY-MM-DD (backward compatibility)
                date_obj = datetime.strptime(display_date, "%b %d, %Y")
                storage_date = date_obj.strftime("%Y-%m-%d")
            else:
                storage_date = display_date
        except:
            storage_date = display_date
        
        for i, expense in enumerate(self.expenses):
            if (expense.date == storage_date and 
                f"{expense.amount:.2f}" == amount_str and 
                expense.description == description):
                return i
        return None
        
    def copy_amount(self):
        """Copy selected expense amount to clipboard"""
        selection = self.tree.selection()
        if selection:
            values = self.tree.item(selection[0], 'values')
            if values and values[0] != "No expenses":
                self.parent_frame.winfo_toplevel().clipboard_clear()
                self.parent_frame.winfo_toplevel().clipboard_append(values[1])
                
    def copy_description(self):
        """Copy selected expense description to clipboard"""
        selection = self.tree.selection()
        if selection:
            values = self.tree.item(selection[0], 'values')
            if values and values[0] != "No expenses":
                self.parent_frame.winfo_toplevel().clipboard_clear()
                self.parent_frame.winfo_toplevel().clipboard_append(values[2])


class ExpenseAddDialog:
    """Modern add expense dialog with improved UX"""
    
    def __init__(self, parent, on_add: Callable[[ExpenseData], None], description_history=None, theme_manager=None):
        self.on_add = on_add
        self.description_history = description_history
        self.theme_manager = theme_manager
        
        # Get theme-aware colors
        self.colors = theme_manager.get_colors() if theme_manager else config.Colors
        
        # Create dialog using DialogHelper with theme-aware colors
        self.dialog = DialogHelper.create_dialog(
            parent,
            "Add New Expense",
            config.Dialog.ADD_EXPENSE_WIDTH,
            config.Dialog.ADD_EXPENSE_HEIGHT,
            colors=self.colors
        )
        
        # Setup GUI first (while hidden)
        self.setup_dialog()
        
        # Position the dialog at lower right corner
        DialogHelper.position_lower_right(
            self.dialog,
            parent,
            config.Dialog.ADD_EXPENSE_WIDTH,
            config.Dialog.ADD_EXPENSE_HEIGHT
        )
        
        # Show the dialog
        DialogHelper.show_dialog(self.dialog)
        
        # Auto-focus amount field after dialog is fully rendered
        # Using after() ensures the widget is ready to receive focus
        self.dialog.after(100, lambda: self.amount_entry.focus_set())
        
        # Bind keyboard shortcuts for sequential field navigation
        def handle_amount_enter(event):
            """Enter in amount field moves to description"""
            self.description_entry.focus_set()
            return "break"  # Prevent default behavior
        
        def handle_description_enter(event):
            """Enter in description field submits the form"""
            # Widget's KeyPress handler returns "break" if dropdown is visible
            # Otherwise, submit form
            self.add_expense()
            return "break"
            
        DialogHelper.bind_escape_to_close(self.dialog)
        
        # Bind Enter to move between fields (amount → description → submit)
        self.amount_entry.bind('<Return>', handle_amount_enter)
        # CRITICAL: Bind with add='+' so widget's handler can run first
        # Widget's handler returns "break" if dropdown is visible, preventing this handler
        self.description_entry.entry.bind('<Return>', handle_description_enter, add='+')
    
    def setup_number_pad(self, parent_frame):
        """Setup calculator-style number pad for amount entry"""
        # Get theme-aware background color for numpad frame
        is_dark = self.theme_manager.is_dark_mode() if self.theme_manager else False
        dialog_bg = self.colors.BG_SECONDARY if is_dark else self.colors.BG_LIGHT_GRAY
        
        # Configure style for numpad LabelFrame to match dialog background
        style = ttk.Style()
        style.configure('NumPad.TLabelframe', 
                       background=dialog_bg,
                       bordercolor=self.colors.BG_DARK_GRAY,
                       borderwidth=0)
        style.configure('NumPad.TLabelframe.Label', 
                       background=dialog_bg)
        
        # Number pad container (no label text) - use theme-aware style
        pad_frame = ttk.LabelFrame(parent_frame, text="", padding="10", style='NumPad.TLabelframe')
        pad_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(0, 12))
        
        # Configure style for number pad buttons (taller, narrower)
        style = ttk.Style()
        style.configure("NumPad.TButton", 
                       font=("Segoe UI", 12, "bold"),
                       padding=(8, 10))
        
        # Button layout: 3x4 grid
        # Row 1: 7, 8, 9
        # Row 2: 4, 5, 6
        # Row 3: 1, 2, 3
        # Row 4: 0, ., C (Clear)
        buttons = [
            ['7', '8', '9'],
            ['4', '5', '6'],
            ['1', '2', '3'],
            ['0', '.', 'C']
        ]
        
        # Create buttons
        for row_idx, row in enumerate(buttons):
            # Center the buttons in the frame
            pad_frame.columnconfigure(0, weight=1)
            pad_frame.columnconfigure(1, weight=1)
            pad_frame.columnconfigure(2, weight=1)
            
            for col_idx, btn_text in enumerate(row):
                # Determine button style and command
                if btn_text == 'C':
                    # Clear button - different color
                    btn = ttk.Button(pad_frame, text=btn_text, 
                                   command=self.on_clear_click,
                                   style="NumPad.TButton",
                                   width=2)
                else:
                    # Number or decimal button
                    btn = ttk.Button(pad_frame, text=btn_text,
                                   command=lambda t=btn_text: self.on_number_click(t),
                                   style="NumPad.TButton",
                                   width=2)
                
                btn.grid(row=row_idx, column=col_idx, padx=5, pady=5, sticky=(tk.W, tk.E))
    
    def on_number_click(self, value):
        """Handle number pad button clicks"""
        current = self.amount_var.get()
        
        # Handle decimal point
        if value == '.':
            # Only allow one decimal point
            if '.' not in current:
                # If empty, start with "0."
                if not current:
                    self.amount_var.set('0.')
                else:
                    self.amount_var.set(current + '.')
            return
        
        # Handle digits (0-9)
        # Check if adding this digit would exceed 2 decimal places
        if '.' in current:
            integer_part, decimal_part = current.split('.')
            if len(decimal_part) >= 2:
                return  # Already have 2 decimal places
        
        # Max length validation (prevent excessive digits)
        if len(current) >= 10:  # Max 10 characters (e.g., 9999999.99)
            return
        
        # If current value is "0", replace it (except after decimal)
        if current == '0':
            self.amount_var.set(value)
        else:
            self.amount_var.set(current + value)
    
    def on_clear_click(self):
        """Clear the amount field"""
        self.amount_var.set('')
    
    def setup_dialog(self):
        """Setup dialog components with clean, simple design"""
        # Configure style
        style = ttk.Style()
        style.theme_use('clam')
        
        # Ensure dialog background matches main_frame for consistency
        is_dark = self.theme_manager.is_dark_mode() if self.theme_manager else False
        dialog_bg = self.colors.BG_SECONDARY if is_dark else self.colors.BG_LIGHT_GRAY
        self.dialog.configure(bg=dialog_bg)
        
        # Configure main_frame background to match dialog (use specific style to avoid global conflicts)
        style.configure('AddDialog.TFrame', background=dialog_bg)
        
        # Configure ttk.Style for Add Expense dialog entry fields (slightly lighter gray, matching Quick Add inline)
        entry_bg = self.colors.BG_MEDIUM_GRAY if is_dark else self.colors.BG_WHITE
        entry_fg = self.colors.TEXT_BLACK  # Theme-aware: TEXT_BLACK in light, TEXT_PRIMARY in dark
        style.configure('AddDialog.TEntry',
                       fieldbackground=entry_bg,
                       foreground=entry_fg,
                       borderwidth=1,
                       relief='solid')
        # Also configure style for Combobox (used by AutoCompleteEntry)
        style.configure('AddDialog.TCombobox',
                       fieldbackground=entry_bg,
                       foreground=entry_fg,
                       borderwidth=1)
        
        # Main container with padding
        main_frame = ttk.Frame(self.dialog, padding="20", style='AddDialog.TFrame')
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid
        self.dialog.columnconfigure(0, weight=1)
        self.dialog.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        
        # Amount field
        ttk.Label(main_frame, text="Amount ($):", 
                 font=config.Fonts.LABEL,
                 foreground=self.colors.TEXT_BLACK,
                 background=dialog_bg).grid(row=0, column=0, sticky=tk.W, pady=(0, 5))
        self.amount_var = tk.StringVar()
        
        # Register validation function
        vcmd = (self.dialog.register(InputValidation.validate_amount), '%P')
        
        self.amount_entry = ttk.Entry(main_frame, textvariable=self.amount_var,
                                     font=config.Fonts.ENTRY,
                                     validate='key', validatecommand=vcmd,
                                     style='AddDialog.TEntry')  # Apply theme-aware styling
        self.amount_entry.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 12))
        
        # Number pad frame
        self.setup_number_pad(main_frame)
        
        # Description field with auto-complete
        ttk.Label(main_frame, text="Description:", 
                 font=config.Fonts.LABEL,
                 foreground=self.colors.TEXT_BLACK,
                 background=dialog_bg).grid(row=3, column=0, sticky=tk.W, pady=(0, 5))
        self.description_var = tk.StringVar()
        
        if self.description_history:
            # Auto-complete entry
            def get_suggestions(partial_text, limit=None):
                """Get suggestions, accepting optional limit parameter"""
                if limit is not None:
                    return self.description_history.get_suggestions(partial_text, limit=limit)
                else:
                    return self.description_history.get_suggestions(partial_text)
            
            desc_frame = ttk.Frame(main_frame)
            desc_frame.grid(row=4, column=0, sticky=(tk.W, tk.E), pady=(0, 12))
            desc_frame.columnconfigure(0, weight=1)
            
            self.description_entry = AutoCompleteEntry(
                desc_frame,
                get_suggestions_callback=get_suggestions,
                show_on_focus=self.description_history.should_show_on_focus(),
                min_chars=self.description_history.get_min_chars(),
                font=config.Fonts.ENTRY,
                style='AddDialog.TCombobox'  # Apply theme-aware styling
            )
            self.description_entry.grid(row=0, column=0, sticky=(tk.W, tk.E))
            # CRITICAL: Replace entry_var and rebind trace callback
            # This ensures text changes trigger dropdown updates
            old_var = self.description_entry.entry_var
            self.description_entry.entry_var = self.description_var
            # Rebind trace callback to new StringVar (required for dropdown to work)
            self.description_entry.entry_var.trace('w', self.description_entry._on_text_change)
            # Update the entry widget to use our StringVar
            self.description_entry.entry.config(textvariable=self.description_var)
        else:
            # Plain entry (fallback if no description_history)
            self.description_entry = ttk.Entry(main_frame, textvariable=self.description_var, 
                                              font=config.Fonts.ENTRY,
                                              style='AddDialog.TEntry')  # Apply theme-aware styling
            self.description_entry.grid(row=4, column=0, sticky=(tk.W, tk.E), pady=(0, 12))
        
        # Date field with collapsible month combobox
        ttk.Label(main_frame, text="Date:", 
                 font=config.Fonts.LABEL,
                 foreground=self.colors.TEXT_BLACK,
                 background=dialog_bg).grid(row=5, column=0, sticky=tk.W, pady=(0, 5))
        
        # Create collapsible date combobox (all 12 months with accordion behavior)
        self.date_combo = CollapsibleDateCombobox(main_frame)
        self.date_combo.grid(row=6, column=0, sticky=(tk.W, tk.E), pady=(0, 15))
        
        # Buttons frame
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=7, column=0, pady=(5, 0))
        
        # OK button (primary action)
        ok_button = ttk.Button(button_frame, text="OK", 
                              command=self.add_expense, width=12)
        ok_button.pack(side=tk.LEFT, padx=(0, 8))
        
        # Cancel button
        cancel_button = ttk.Button(button_frame, text="Cancel", 
                                 command=self.dialog.destroy, width=12)
        cancel_button.pack(side=tk.LEFT)
        
            
    def add_expense(self):
        """Add the expense with validation"""
        try:
            # Get date from widget (returns YYYY-MM-DD format)
            date_str = self.date_combo.get_selected_date()
            
            if not date_str:
                messagebox.showerror(config.Messages.TITLE_VALIDATION, config.Messages.DATE_REQUIRED)
                self.date_combo.combo.focus()
                return
            
            # Validate all fields using preset validator
            # Get description value - AutoCompleteEntry has get() method, Entry uses StringVar
            desc_value = self.description_entry.get() if hasattr(self.description_entry, 'get') else self.description_var.get()
            
            result = ValidationPresets.manual_add_expense(
                self.amount_var.get(),
                desc_value,
                date_str
            )
            
            # If validation failed, show error and focus appropriate field
            if not result:
                messagebox.showerror(config.Messages.TITLE_VALIDATION, result.error_message)
                
                # Auto-focus the field that failed validation
                if result.error_field == "amount":
                    self.amount_entry.focus()
                elif result.error_field == "description":
                    # Handle both AutoCompleteEntry and regular Entry
                    if hasattr(self.description_entry, 'focus_set'):
                        self.description_entry.focus_set()
                    else:
                        self.description_entry.focus()
                elif result.error_field == "date":
                    self.date_combo.combo.focus()
                return
            
            # Get sanitized values from validation result
            sanitized = result.sanitized_value
            
            # Create expense with pre-validated, cleaned data
            expense = ExpenseData(
                date=sanitized['date'],
                amount=sanitized['amount'],
                description=sanitized['description']
            )
            
            # Track description for auto-complete (if history manager available)
            if self.description_history:
                self.description_history.add_or_update(
                    sanitized['description'],
                    sanitized['amount']
            )
            
            # Add expense
            self.on_add(expense)
            self.dialog.destroy()
            
        except Exception as e:
            messagebox.showerror(config.Messages.TITLE_ERROR, f"Unexpected error: {e}")
            self.amount_entry.focus()


class ExpenseEditDialog:
    """Modern edit expense dialog"""
    
    def __init__(self, parent, expense: ExpenseData, on_update: Callable[[ExpenseData], None], theme_manager=None):
        self.expense = expense
        self.on_update = on_update
        self.theme_manager = theme_manager
        
        # Get theme-aware colors
        self.colors = theme_manager.get_colors() if theme_manager else config.Colors
        
        # Create dialog using DialogHelper with theme-aware colors
        self.dialog = DialogHelper.create_dialog(
            parent,
            "Edit Expense",
            config.Dialog.EDIT_EXPENSE_WIDTH,
            config.Dialog.EDIT_EXPENSE_HEIGHT,
            colors=self.colors
        )
        
        # Setup GUI
        self.setup_dialog()
        
        # Center the dialog on parent
        DialogHelper.center_on_parent(
            self.dialog,
            parent,
            config.Dialog.EDIT_EXPENSE_WIDTH,
            config.Dialog.EDIT_EXPENSE_HEIGHT
        )
        
        # Show the dialog
        DialogHelper.show_dialog(self.dialog)
        
        # Focus on amount field and select all
        self.amount_entry.focus()
        self.amount_entry.select_range(0, tk.END)
        
        # Bind keyboard shortcuts - more robust approach
        def handle_enter(event):
            self.update_expense()
            return "break"  # Prevent default behavior
            
        self.dialog.bind('<Return>', handle_enter)
        DialogHelper.bind_escape_to_close(self.dialog)
        
        # Also bind to the entry fields
        self.amount_entry.bind('<Return>', handle_enter)
        self.description_entry.bind('<Return>', handle_enter)
        self.date_combo.combo.bind('<Return>', handle_enter)
    
    def setup_dialog(self):
        """Setup dialog components"""
        # Configure style first
        style = ttk.Style()
        style.theme_use('clam')
        
        # Ensure dialog background matches main_frame for consistency
        is_dark = self.theme_manager.is_dark_mode() if self.theme_manager else False
        dialog_bg = self.colors.BG_SECONDARY if is_dark else self.colors.BG_LIGHT_GRAY
        self.dialog.configure(bg=dialog_bg)
        
        # Configure main_frame background to match dialog (use specific style to avoid global conflicts)
        style.configure('EditDialog.TFrame', background=dialog_bg)
        
        # Main container (use specific style to avoid global conflicts)
        main_frame = ttk.Frame(self.dialog, padding="20", style='EditDialog.TFrame')
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid
        self.dialog.columnconfigure(0, weight=1)
        self.dialog.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        
        # Configure ttk.Style for Edit Expense dialog labels (theme-aware backgrounds)
        style.configure('EditDialog.TLabel', 
                       font=config.Fonts.LABEL,
                       foreground=self.colors.TEXT_BLACK,
                       background=dialog_bg)
        style.configure('EditDialog.Header.TLabel', 
                       font=config.Fonts.HEADER,
                       foreground=self.colors.TEXT_BLACK,
                       background=dialog_bg)
        
        # Configure ttk.Style for Edit Expense dialog entry fields (theme-aware)
        entry_bg = self.colors.BG_TERTIARY if is_dark else self.colors.BG_WHITE
        entry_fg = self.colors.TEXT_BLACK  # Theme-aware: TEXT_BLACK in light, TEXT_PRIMARY in dark
        style.configure('EditDialog.TEntry',
                       fieldbackground=entry_bg,
                       foreground=entry_fg,
                       borderwidth=1,
                       relief='solid')
        
        # Title
        title_label = ttk.Label(main_frame, text="Edit Expense", 
                               style='EditDialog.Header.TLabel')
        title_label.grid(row=0, column=0, pady=(0, 20))
        
        # Amount field
        ttk.Label(main_frame, text="Amount:", 
                 style='EditDialog.TLabel').grid(row=1, column=0, sticky=tk.W, pady=(0, 5))
        self.amount_var = tk.StringVar(value=InputValidation.format_amount(self.expense.amount))
        self.amount_entry = ttk.Entry(main_frame, textvariable=self.amount_var, 
                                     width=25, font=config.Fonts.ENTRY,
                                     style='EditDialog.TEntry')
        self.amount_entry.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(0, 15))
        
        # Description field
        ttk.Label(main_frame, text="Description:", 
                 style='EditDialog.TLabel').grid(row=3, column=0, sticky=tk.W, pady=(0, 5))
        self.description_var = tk.StringVar(value=self.expense.description)
        self.description_entry = ttk.Entry(main_frame, textvariable=self.description_var, 
                                          width=25, font=config.Fonts.ENTRY,
                                          style='EditDialog.TEntry')
        self.description_entry.grid(row=4, column=0, sticky=(tk.W, tk.E), pady=(0, 15))
        
        # Date field with collapsible month combobox
        ttk.Label(main_frame, text="Date:", 
                 style='EditDialog.TLabel').grid(row=5, column=0, sticky=tk.W, pady=(0, 5))
        
        # Create collapsible date combobox (all 12 months with accordion behavior)
        self.date_combo = CollapsibleDateCombobox(main_frame)
        
        # Set to the existing expense's date
        self.date_combo.set_date(self.expense.date)
        
        self.date_combo.grid(row=6, column=0, sticky=(tk.W, tk.E), pady=(0, 20))
        
        # Buttons frame
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=7, column=0, pady=(10, 0))
        
        # Update button
        update_button = ttk.Button(button_frame, text="Update", 
                                 command=self.update_expense)
        update_button.pack(side=tk.LEFT, padx=(0, 10))
        
        cancel_button = ttk.Button(button_frame, text="Cancel", 
                                 command=self.dialog.destroy)
        cancel_button.pack(side=tk.LEFT)
        
        
    def update_expense(self):
        """Update the expense with validation"""
        try:
            # Get date from widget (returns YYYY-MM-DD format)
            date_str = self.date_combo.get_selected_date()
            
            if not date_str:
                messagebox.showerror(config.Messages.TITLE_VALIDATION, config.Messages.DATE_REQUIRED)
                self.date_combo.combo.focus()
                return
            
            # Validate all fields using preset validator
            result = ValidationPresets.edit_expense(
                self.amount_var.get(),
                self.description_var.get(),
                date_str
            )
            
            # If validation failed, show error and focus appropriate field
            if not result:
                messagebox.showerror(config.Messages.TITLE_VALIDATION, result.error_message)
                
                # Auto-focus the field that failed validation
                if result.error_field == "amount":
                    self.amount_entry.focus()
                elif result.error_field == "description":
                    # Handle both AutoCompleteEntry and regular Entry
                    if hasattr(self.description_entry, 'focus_set'):
                        self.description_entry.focus_set()
                    else:
                        self.description_entry.focus()
                elif result.error_field == "date":
                    self.date_combo.combo.focus()
                return
            
            # Get sanitized values from validation result
            sanitized = result.sanitized_value
            
            # Create updated expense with pre-validated, cleaned data
            updated_expense = ExpenseData(
                date=sanitized['date'],
                amount=sanitized['amount'],
                description=sanitized['description']
            )
            
            # Update expense
            self.on_update(updated_expense)
            self.dialog.destroy()
            
        except Exception as e:
            messagebox.showerror(config.Messages.TITLE_ERROR, f"Unexpected error: {e}")
            self.amount_entry.focus()
