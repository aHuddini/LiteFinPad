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


def validate_amount_input(new_value):
    """
    Validate amount field input in real-time
    - Only allows digits, one decimal point
    - Maximum 2 decimal places
    - No upper limit on value
    - Returns True if valid, False otherwise
    """
    if new_value == "":
        return True  # Allow empty field
    
    # Check if it only contains digits and at most one decimal point
    if not all(c.isdigit() or c == '.' for c in new_value):
        return False
    
    # Check for only one decimal point
    if new_value.count('.') > 1:
        return False
    
    # Check decimal places (max 2)
    if '.' in new_value:
        integer_part, decimal_part = new_value.split('.')
        if len(decimal_part) > 2:
            return False
    
    # Check if it's a valid number format
    try:
        if new_value != '.':
            float(new_value)
    except ValueError:
        return False
    
    return True


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
    
    def __init__(self, parent_frame: ttk.Frame, on_expense_change: Optional[Callable] = None):
        self.parent_frame = parent_frame
        self.on_expense_change = on_expense_change
        self.expenses: List[ExpenseData] = []
        
        # Create the table frame
        self.setup_table()
        
    def setup_table(self):
        """Setup the expense table with modern styling"""
        # Create main container frame
        self.table_frame = ttk.LabelFrame(self.parent_frame, text="", padding="10")
        self.table_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 15))
        
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
            height=8,
            style="Modern.Treeview"
        )
        
        # Configure columns
        self.tree.heading("Date", text="Date", anchor="center")
        self.tree.heading("Amount", text="Amount", anchor="e")
        self.tree.heading("Description", text="Description", anchor="w")
        
        # Set column widths and properties (wider date column for "(Future)" text)
        self.tree.column("Date", width=180, minwidth=160, anchor="center")
        self.tree.column("Amount", width=120, minwidth=100, anchor="e")  # Wider for 5-digit amounts
        self.tree.column("Description", width=230, minwidth=140, anchor="w")  # Reduced to balance with Date/Amount
        
        # Configure modern styling
        style = ttk.Style()
        style.configure("Modern.Treeview", 
                       font=('Segoe UI', 10),
                       rowheight=28,
                       background='white',
                       foreground='black',
                       fieldbackground='white')
        style.configure("Modern.Treeview.Heading", 
                       font=('Segoe UI', 10, 'bold'),
                       background='#f0f0f0',
                       foreground='black')
        style.map("Modern.Treeview", 
                 background=[('selected', '#0078d4')],
                 foreground=[('selected', 'white')])
        
        # Add treeview directly to table frame
        self.tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(self.table_frame, orient="vertical", command=self.tree.yview)
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        # Configure tags for future expenses
        self.tree.tag_configure('future', foreground='#888888', font=('Segoe UI', 10, 'italic'))
        
        # Bind events
        self.tree.bind("<Button-3>", self.show_context_menu)  # Right-click
        self.tree.bind("<Double-1>", self.edit_selected_expense)  # Double-click
        self.tree.bind("<Delete>", self.delete_selected_expense)  # Delete key
        
        # Add status bar
        self.status_frame = ttk.Frame(self.table_frame)
        self.status_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(5, 0))
        
        self.status_label = ttk.Label(self.status_frame, text="No expenses", font=('Segoe UI', 10))
        self.status_label.pack(side=tk.LEFT)
        
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
            
        # Add expenses (show last 15 for better performance)
        if self.expenses:
            # Sort by date descending (most recent first)
            recent_expenses = sorted(self.expenses, key=lambda x: x.date, reverse=True)[:15]
            today = datetime.now().date()
            
            for expense in recent_expenses:
                # Format date for display
                try:
                    date_obj = datetime.strptime(expense.date, "%Y-%m-%d")
                    formatted_date = date_obj.strftime("%m/%d/%Y")
                    
                    # Check if this is a future expense
                    is_future = date_obj.date() > today
                    if is_future:
                        formatted_date = formatted_date + " (Future)"
                except ValueError:
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
                       if datetime.strptime(e.date, "%Y-%m-%d").date() <= today)
            count = len(self.expenses)
            future_count = sum(1 for e in self.expenses 
                             if datetime.strptime(e.date, "%Y-%m-%d").date() > today)
            
            if future_count > 0:
                self.status_label.config(text=f"{count} expenses ({future_count} future)")
            else:
                self.status_label.config(text=f"{count} expenses")
        else:
            # Show placeholder
            self.tree.insert("", "end", values=(
                "No expenses",
                "$0.00",
                "Add your first expense above"
            ))
            self.status_label.config(text="No expenses")
            
    def show_context_menu(self, event):
        """Show context menu for expense management"""
        # Select the item under the cursor
        item = self.tree.identify_row(event.y)
        if item:
            self.tree.selection_set(item)
            
            # Create context menu
            context_menu = tk.Menu(self.parent_frame.winfo_toplevel(), tearoff=0)
            context_menu.add_command(label="Edit Expense", command=self.edit_selected_expense)
            context_menu.add_command(label="Delete Expense", command=self.delete_selected_expense)
            context_menu.add_separator()
            context_menu.add_command(label="Copy Amount", command=self.copy_amount)
            context_menu.add_command(label="Copy Description", command=self.copy_description)
            
            # Show context menu
            try:
                context_menu.tk_popup(event.x_root, event.y_root)
            finally:
                context_menu.grab_release()
                
    def edit_selected_expense(self, event=None):
        """Edit the selected expense"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select an expense to edit.")
            return
            
        # Get the selected item
        item = selection[0]
        values = self.tree.item(item, 'values')
        
        if not values or values[0] == "No expenses":
            return
            
        # Find the expense index
        expense_index = self.find_expense_index(values)
        if expense_index is None:
            messagebox.showerror("Error", "Could not find expense to edit.")
            return
            
        # Open edit dialog
        expense = self.expenses[expense_index]
        dialog = ExpenseEditDialog(
            self.parent_frame.winfo_toplevel(), 
            expense, 
            lambda new_expense: self.update_expense(expense_index, new_expense)
        )
        
    def delete_selected_expense(self, event=None):
        """Delete the selected expense"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select an expense to delete.")
            return
            
        # Get the selected item
        item = selection[0]
        values = self.tree.item(item, 'values')
        
        if not values or values[0] == "No expenses":
            return
            
        # Find the expense index
        expense_index = self.find_expense_index(values)
        if expense_index is None:
            messagebox.showerror("Error", "Could not find expense to delete.")
            return
            
        # Confirm deletion
        expense = self.expenses[expense_index]
        result = messagebox.askyesno(
            "Confirm Delete", 
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
    
    def __init__(self, parent, on_add: Callable[[ExpenseData], None]):
        self.on_add = on_add
        
        # Create dialog window
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Add New Expense")
        self.dialog.resizable(False, False)
        self.dialog.transient(parent)
        self.dialog.configure(bg='#f8f9fa')
        
        # IMPORTANT: Withdraw immediately to prevent flash at top-left corner
        self.dialog.withdraw()
        
        # Setup GUI first (while hidden)
        self.setup_dialog()
        
        # Position the dialog at lower right corner
        self.center_dialog(parent)
        
        # Show the dialog now that it's fully configured and positioned
        self.dialog.deiconify()
        
        # Ensure dialog is on top and focused
        self.dialog.lift()
        self.dialog.focus_force()
        self.dialog.grab_set()  # Make dialog modal
        
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
            self.add_expense()
            return "break"  # Prevent default behavior
            
        def handle_escape(event):
            self.dialog.destroy()
            return "break"
            
        self.dialog.bind('<Escape>', handle_escape)
        
        # Bind Enter to move between fields (amount → description → submit)
        self.amount_entry.bind('<Return>', handle_amount_enter)
        self.description_entry.bind('<Return>', handle_description_enter)
    
    def setup_number_pad(self, parent_frame):
        """Setup calculator-style number pad for amount entry"""
        # Number pad container (no label text)
        pad_frame = ttk.LabelFrame(parent_frame, text="", padding="10")
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
    
    def generate_date_options(self):
        """Generate date options for the current month (including future dates)"""
        today = datetime.now()
        current_day = today.day
        current_month = today.strftime("%B")  # e.g., "October"
        
        # Get the last day of current month
        if today.month == 12:
            last_day = 31
        else:
            from calendar import monthrange
            last_day = monthrange(today.year, today.month)[1]
        
        options = []
        for day in range(1, last_day + 1):
            # Format: "1 - October 1", "2 - October 2", etc. (no suffix)
            # Add (Today) or (Future) indicator
            if day == current_day:
                display = f"{day} - {current_month} {day} (Today)"
            elif day > current_day:
                display = f"{day} - {current_month} {day} (Future)"
            else:
                display = f"{day} - {current_month} {day}"
            
            options.append(display)
        
        return options
        
    def center_dialog(self, parent):
        """Position dialog at lower right corner of parent window"""
        parent.update_idletasks()
        # Position at lower right corner - perfectly snapped to corner
        x = parent.winfo_x() + parent.winfo_width() - 400  # No padding - touch right edge
        y = parent.winfo_y() + parent.winfo_height() - 670  # No padding - touch bottom edge
        # Adjust Y if dialog would go off-screen
        screen_height = parent.winfo_screenheight()
        if y < 0:
            y = 20  # Small margin from top
        self.dialog.geometry(f"400x670+{x}+{y}")
        
    def setup_dialog(self):
        """Setup dialog components with clean, simple design"""
        # Configure style
        style = ttk.Style()
        style.theme_use('clam')
        
        # Main container with padding
        main_frame = ttk.Frame(self.dialog, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid
        self.dialog.columnconfigure(0, weight=1)
        self.dialog.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        
        # Amount field
        ttk.Label(main_frame, text="Amount ($):", font=("Segoe UI", 10)).grid(row=0, column=0, sticky=tk.W, pady=(0, 5))
        self.amount_var = tk.StringVar()
        
        # Register validation function
        vcmd = (self.dialog.register(validate_amount_input), '%P')
        
        self.amount_entry = ttk.Entry(main_frame, textvariable=self.amount_var, 
                                     font=("Segoe UI", 11),
                                     validate='key', validatecommand=vcmd)
        self.amount_entry.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 12))
        
        # Number pad frame
        self.setup_number_pad(main_frame)
        
        # Description field
        ttk.Label(main_frame, text="Description:", font=("Segoe UI", 10)).grid(row=3, column=0, sticky=tk.W, pady=(0, 5))
        self.description_var = tk.StringVar()
        self.description_entry = ttk.Entry(main_frame, textvariable=self.description_var, 
                                          font=("Segoe UI", 11))
        self.description_entry.grid(row=4, column=0, sticky=(tk.W, tk.E), pady=(0, 12))
        
        # Date field with smart dropdown
        ttk.Label(main_frame, text="Date:", font=("Segoe UI", 10)).grid(row=5, column=0, sticky=tk.W, pady=(0, 5))
        
        # Generate date options for current month
        self.date_var = tk.StringVar()
        date_options = self.generate_date_options()
        
        # Set default to today's day (index is day - 1)
        current_day = datetime.now().day
        self.date_var.set(date_options[current_day - 1])  # e.g., if today is 12th, use index 11
        
        # Configure custom style for date combobox with darker blue highlight and white text
        style = ttk.Style()
        style.map('DateCombo.TCombobox',
                  fieldbackground=[('readonly', '#2E5C8A')],
                  foreground=[('readonly', 'white')],
                  selectbackground=[('readonly', '#2E5C8A')],
                  selectforeground=[('readonly', 'white')])
        style.configure('DateCombo.TCombobox',
                       foreground='white',
                       fieldbackground='#2E5C8A')
        
        self.date_combo = ttk.Combobox(main_frame, textvariable=self.date_var, 
                                      values=date_options, state="readonly", 
                                      font=("Segoe UI", 10), style='DateCombo.TCombobox')
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
            amount_str = self.amount_var.get().strip()
            description = self.description_var.get().strip()
            date_selection = self.date_var.get().strip()
            
            # Validation
            if not amount_str:
                messagebox.showerror("Error", "Please enter an amount")
                self.amount_entry.focus()
                return
                
            if not description:
                messagebox.showerror("Error", "Please enter a description")
                self.description_entry.focus()
                return
                
            if not date_selection:
                messagebox.showerror("Error", "Please select a date")
                self.date_combo.focus()
                return
                
            amount = float(amount_str)
            if amount <= 0:
                messagebox.showerror("Error", "Amount must be greater than 0")
                self.amount_entry.focus()
                return
                
            if amount > 100000:  # Reasonable upper limit
                messagebox.showerror("Error", "Amount seems too large. Please verify.")
                self.amount_entry.focus()
                return
                
            # Parse date from selection (e.g., "12 - October 12th" -> 2025-10-12)
            try:
                # Extract the day number from the beginning of the selection
                # Format: "12 - October 12th" -> day = 12
                day_num = int(date_selection.split(' - ')[0])
                
                # Get current month and year
                current_date = datetime.now()
                current_year = current_date.year
                current_month = current_date.month
                
                # Create date string in YYYY-MM-DD format
                date_str = f"{current_year}-{current_month:02d}-{day_num:02d}"
                
                # Validate the date
                datetime.strptime(date_str, "%Y-%m-%d")
            except (ValueError, IndexError):
                messagebox.showerror("Error", "Invalid date selection")
                return
                
            # Create expense
            expense = ExpenseData(
                date=date_str,
                amount=amount,
                description=description
            )
            
            # Add expense
            self.on_add(expense)
            self.dialog.destroy()
            
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid amount")
            self.amount_entry.focus()


class ExpenseEditDialog:
    """Modern edit expense dialog"""
    
    def __init__(self, parent, expense: ExpenseData, on_update: Callable[[ExpenseData], None]):
        self.expense = expense
        self.on_update = on_update
        
        # Create dialog window
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Edit Expense")
        self.dialog.geometry("350x250")
        self.dialog.resizable(False, False)
        self.dialog.transient(parent)
        self.dialog.grab_set()
        self.dialog.configure(bg='#f8f9fa')
        
        # Position the dialog at lower right corner
        self.center_dialog(parent)
        
        # Setup GUI
        self.setup_dialog()
        
        # Focus on amount field and select all
        self.amount_entry.focus()
        self.amount_entry.select_range(0, tk.END)
        
        # Ensure dialog is on top and focused
        self.dialog.lift()
        self.dialog.focus_force()
        self.dialog.grab_set()  # Make dialog modal
        
        # Bind keyboard shortcuts - more robust approach
        def handle_enter(event):
            self.update_expense()
            return "break"  # Prevent default behavior
            
        def handle_escape(event):
            self.dialog.destroy()
            return "break"
            
        self.dialog.bind('<Return>', handle_enter)
        self.dialog.bind('<Escape>', handle_escape)
        
        # Also bind to the entry fields
        self.amount_entry.bind('<Return>', handle_enter)
        self.description_entry.bind('<Return>', handle_enter)
        self.month_combo.bind('<Return>', handle_enter)
        
    def center_dialog(self, parent):
        """Center dialog on parent window"""
        parent.update_idletasks()
        x = parent.winfo_x() + (parent.winfo_width() // 2) - 175
        y = parent.winfo_y() + (parent.winfo_height() // 2) - 100
        self.dialog.geometry(f"350x250+{x}+{y}")
        
    def setup_dialog(self):
        """Setup dialog components"""
        # Configure style
        style = ttk.Style()
        style.theme_use('clam')
        
        # Main container
        main_frame = ttk.Frame(self.dialog, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid
        self.dialog.columnconfigure(0, weight=1)
        self.dialog.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        
        # Title
        title_label = ttk.Label(main_frame, text="Edit Expense", 
                               font=("Segoe UI", 14, "bold"))
        title_label.grid(row=0, column=0, pady=(0, 20))
        
        # Amount field
        ttk.Label(main_frame, text="Amount:", font=("Segoe UI", 10)).grid(row=1, column=0, sticky=tk.W, pady=(0, 5))
        self.amount_var = tk.StringVar(value=str(self.expense.amount))
        self.amount_entry = ttk.Entry(main_frame, textvariable=self.amount_var, 
                                     width=25, font=("Segoe UI", 11))
        self.amount_entry.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(0, 15))
        
        # Description field
        ttk.Label(main_frame, text="Description:", font=("Segoe UI", 10)).grid(row=3, column=0, sticky=tk.W, pady=(0, 5))
        self.description_var = tk.StringVar(value=self.expense.description)
        self.description_entry = ttk.Entry(main_frame, textvariable=self.description_var, 
                                          width=25, font=("Segoe UI", 11))
        self.description_entry.grid(row=4, column=0, sticky=(tk.W, tk.E), pady=(0, 15))
        
        # Date field - Month dropdown
        ttk.Label(main_frame, text="Month:", font=("Segoe UI", 10)).grid(row=5, column=0, sticky=tk.W, pady=(0, 5))
        
        # Create month dropdown
        self.month_var = tk.StringVar()
        month_options = [
            "1 - January", "2 - February", "3 - March", "4 - April",
            "5 - May", "6 - June", "7 - July", "8 - August",
            "9 - September", "10 - October", "11 - November", "12 - December"
        ]
        
        # Set to the month from the existing expense
        try:
            expense_date = datetime.strptime(self.expense.date, "%Y-%m-%d")
            month_num = expense_date.month
            month_name = expense_date.strftime('%B')
            self.month_var.set(f"{month_num} - {month_name}")
        except ValueError:
            # Fallback to current month if date parsing fails
            current_month = datetime.now().month
            self.month_var.set(f"{current_month} - {datetime.now().strftime('%B')}")
        
        self.month_combo = ttk.Combobox(main_frame, textvariable=self.month_var, 
                                       values=month_options, state="readonly", 
                                       width=22, font=("Segoe UI", 11))
        self.month_combo.grid(row=6, column=0, sticky=(tk.W, tk.E), pady=(0, 20))
        
        # Buttons frame
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=7, column=0, pady=(10, 0))
        
        # Update button
        update_button = ttk.Button(button_frame, text="Update Expense", 
                                 command=self.update_expense)
        update_button.pack(side=tk.LEFT, padx=(0, 10))
        
        cancel_button = ttk.Button(button_frame, text="Cancel", 
                                 command=self.dialog.destroy)
        cancel_button.pack(side=tk.LEFT)
        
        
    def update_expense(self):
        """Update the expense with validation"""
        try:
            amount_str = self.amount_var.get().strip()
            description = self.description_var.get().strip()
            month_str = self.month_var.get().strip()
            
            # Validation
            if not amount_str:
                messagebox.showerror("Error", "Please enter an amount")
                self.amount_entry.focus()
                return
                
            if not description:
                messagebox.showerror("Error", "Please enter a description")
                self.description_entry.focus()
                return
                
            if not month_str:
                messagebox.showerror("Error", "Please select a month")
                self.month_combo.focus()
                return
                
            amount = float(amount_str)
            if amount <= 0:
                messagebox.showerror("Error", "Amount must be greater than 0")
                self.amount_entry.focus()
                return
                
            if amount > 100000:
                messagebox.showerror("Error", "Amount seems too large. Please verify.")
                self.amount_entry.focus()
                return
                
            # Convert month selection to date format
            try:
                # Extract month number from selection (e.g., "1 - January" -> 1)
                month_num = int(month_str.split(' - ')[0])
                current_year = datetime.now().year
                current_day = datetime.now().day
                
                # Create date string in YYYY-MM-DD format
                date_str = f"{current_year}-{month_num:02d}-{current_day:02d}"
                
                # Validate the date
                datetime.strptime(date_str, "%Y-%m-%d")
            except (ValueError, IndexError):
                messagebox.showerror("Error", "Invalid month selection")
                self.month_combo.focus()
                return
                
            # Create updated expense
            updated_expense = ExpenseData(
                date=date_str,
                amount=amount,
                description=description
            )
            
            # Update expense
            self.on_update(updated_expense)
            self.dialog.destroy()
            
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid amount")
            self.amount_entry.focus()
