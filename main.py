import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
from datetime import datetime, timedelta
import calendar
import threading
import sys
import time
# PIL removed - icon.ico is bundled directly by PyInstaller
import ctypes
from expense_table import ExpenseTableManager, ExpenseAddDialog, ExpenseData
from gui import LiteFinPadGUI
from tray_icon import create_simple_tray_icon
from error_logger import log_error, log_info, log_warning, log_debug, error_logger, log_data_load
from export_data import export_expenses
from import_data import import_expense_backup
from window_animation import create_window_animator

# Set DPI awareness for Windows 11 crisp text rendering
try:
    # Set process DPI awareness to prevent blurry text
    ctypes.windll.shcore.SetProcessDpiAwareness(1)
except AttributeError:
    # Fallback for older Windows versions
    try:
        ctypes.windll.user32.SetProcessDPIAware()
    except AttributeError:
        pass

# Setup debug logger



class ExpenseTracker:
    def __init__(self):
        # Initialize error logging
        error_logger.log_application_start()
        
        self.current_month = datetime.now().strftime("%Y-%m")
        self.data_folder = f"data_{self.current_month}"
        self.expenses_file = os.path.join(self.data_folder, "expenses.json")
        self.calculations_file = os.path.join(self.data_folder, "calculations.json")
        self.expenses = []
        self.monthly_total = 0.0
        self.current_page = "main"  # Track current page
        self.open_dialogs = []  # Track open dialogs for proper cleanup
        self.is_hidden = True  # Track if window is intentionally hidden (starts hidden)
        self.load_data()
        
        # Create main window
        self.root = tk.Tk()
        
        # Remove taskbar icon - make this a pure system tray application
        self.root.attributes('-toolwindow', True)
        
        # Anti-flicker optimizations
        self.root.configure(bg='white')  # Set consistent background
        self.root.attributes('-alpha', 1.0)  # Ensure full opacity initially
        
        # Configure window close behavior - X button should quit the app
        self.root.protocol("WM_DELETE_WINDOW", self.quit_app)
        
        # Add window state change handler to distinguish between minimize and close
        self.root.bind("<Unmap>", self.on_window_unmap)
        self.root.bind("<Map>", self.on_window_map)
        
        # Add additional close detection
        self.root.bind("<Destroy>", self.on_window_destroy)
        
        # Configure DPI scaling for crisp text rendering
        self.configure_dpi_scaling()
        
        # Initialize GUI using separated GUI class
        self.gui = LiteFinPadGUI(self.root, self)
        
        # Create window animator
        self.animator = create_window_animator(self.root)
        
        # Create and start tray icon
        self.create_tray_icon()
        
        # Hide window initially - use tray icon to access
        self.root.withdraw()
        
    def configure_dpi_scaling(self):
        """Configure DPI scaling for crisp text rendering on Windows 11"""
        try:
            # Get the current DPI scaling factor
            dpi = ctypes.windll.user32.GetDpiForWindow(self.root.winfo_id())
            if dpi > 0:
                # Calculate scaling factor (96 is standard DPI)
                scaling_factor = dpi / 96.0
                
                # Set tkinter scaling to match system DPI
                self.root.tk.call('tk', 'scaling', scaling_factor)
                
                print(f"DPI scaling configured: {scaling_factor:.2f}x (DPI: {dpi})")
            else:
                # Fallback: use a reasonable default
                self.root.tk.call('tk', 'scaling', 1.0)
                print("Using default DPI scaling")
        except Exception as e:
            print(f"DPI scaling configuration failed: {e}")
            # Fallback to default scaling
            self.root.tk.call('tk', 'scaling', 1.0)
        
    def get_icon_path(self):
        """Get the correct icon path for both development and PyInstaller builds"""
        try:
            # Check if we're running as a PyInstaller bundle
            if hasattr(sys, '_MEIPASS'):
                # Running as PyInstaller executable
                icon_path = os.path.join(sys._MEIPASS, 'icon.ico')
                print(f"PyInstaller mode: Looking for icon at {icon_path}")
                if os.path.exists(icon_path):
                    print(f"Found icon in PyInstaller bundle: {icon_path}")
                    return icon_path
                else:
                    print("Icon not found in PyInstaller bundle, trying alternative locations")
                    # Try alternative locations
                    alt_paths = [
                        os.path.join(sys._MEIPASS, 'dist', 'icon.ico'),
                        os.path.join(os.path.dirname(sys.executable), 'icon.ico'),
                        os.path.join(os.path.dirname(sys.executable), 'dist', 'icon.ico')
                    ]
                    for alt_path in alt_paths:
                        if os.path.exists(alt_path):
                            print(f"Found icon at alternative location: {alt_path}")
                            return alt_path
                    print("Icon not found in any location, creating default")
                    return self.create_default_icon()
            else:
                # Running as Python script
                icon_path = "icon.ico"
                print(f"Development mode: Looking for icon at {icon_path}")
                if os.path.exists(icon_path):
                    print(f"Found icon in development: {icon_path}")
                    return icon_path
                else:
                    print("Icon not found in development, creating default")
                    return self.create_default_icon()
        except Exception as e:
            print(f"Error resolving icon path: {e}")
            return self.create_default_icon()
    
    def create_default_icon(self):
        """Fallback - icon.ico should always be bundled by PyInstaller"""
        try:
            print("Warning: icon.ico not found - using tkinter default")
            # PIL removed for size optimization
            # icon.ico is bundled by PyInstaller via --icon and --add-data flags
            # If we reach this point, something went wrong with the build
            return None
            
        except Exception as e:
            print(f"Error in create_default_icon: {e}")
            import traceback
            traceback.print_exc()
            return None
        
    def create_tray_icon(self):
        """Create and start the system tray icon"""
        try:
            log_info("Creating tray icon...")
            
            def toggle_app():
                """Toggle app visibility - simple toggle based on hidden state"""
                try:
                    if self.is_hidden:
                        self.show_window()
                    else:
                        self.hide_window()
                except Exception as e:
                    log_error("Error in toggle_app", e)
            
            # Generate tooltip with monthly total
            tooltip = self.get_tray_tooltip()
            
            # Create and start tray icon using the new system
            self.tray_icon = create_simple_tray_icon(
                toggle_callback=toggle_app,
                quick_add_callback=self.show_quick_add_dialog,
                quit_callback=self.quit_app,
                tooltip=tooltip
            )
            
            # Start the tray icon
            if self.tray_icon.start():
                log_info("Tray icon created and started successfully")
            else:
                log_error("Failed to start tray icon")
            
        except Exception as e:
            log_error("Error creating tray icon", e)
    
    def get_tray_tooltip(self):
        """Generate tooltip text for tray icon with monthly total"""
        try:
            # Get month name and year
            month_name = datetime.strptime(self.current_month, "%Y-%m").strftime("%B %Y")
            
            # Calculate monthly total
            monthly_total = sum(expense['amount'] for expense in self.expenses)
            
            # Format tooltip with line break: "LiteFinPad\nOctober 2025: $5,176.00"
            tooltip = f"LiteFinPad\n{month_name}: ${monthly_total:,.2f}"
            return tooltip
        except Exception as e:
            log_error(f"Error generating tray tooltip: {e}")
            return "LiteFinPad\nExpense Tracker"
    
    def update_tray_tooltip(self):
        """Update the tray icon tooltip with current monthly total"""
        try:
            if hasattr(self, 'tray_icon') and self.tray_icon:
                tooltip = self.get_tray_tooltip()
                self.tray_icon.update_tooltip(tooltip)
        except Exception as e:
            log_error(f"Error updating tray tooltip: {e}")
        
    def show_window(self):
        """Show the main window positioned near taskbar with slide animation"""
        try:
            log_info(f"[WINDOW] === show_window() called at {time.time():.3f} ===")
            log_info(f"[WINDOW] Current hidden state: {self.is_hidden}")
            
            # Refresh display to update date-based filtering (e.g., future expenses becoming current)
            log_info("[WINDOW] Updating recent expenses and display")
            self.gui.update_recent_expenses()
            self.gui.update_display()
            log_info("[WINDOW] Display updated")
            
            # Get screen dimensions
            screen_width = self.root.winfo_screenwidth()
            screen_height = self.root.winfo_screenheight()
            
            # Position window near bottom-right corner (near taskbar)
            window_width = 650
            window_height = 850  # Compact height with reduced Recent Expenses
            x = screen_width - window_width - 20
            y = screen_height - window_height - 450  # Clear space for 3 rows of hidden system tray icons
            
            # Use the animator for smooth slide-in
            self.animator.slide_in(x, y, window_width, window_height)
            log_info("[WINDOW] Setting hidden state to False")
            self.is_hidden = False
            
            # Bring to front
            log_info("[WINDOW] Bringing window to front with lift() and focus_force()")
            self.root.lift()
            self.root.focus_force()
            
            # Set topmost attribute based on stay_on_top setting
            if hasattr(self.gui, 'stay_on_top_var') and self.gui.stay_on_top_var.get():
                # Stay on top is enabled - keep window on top permanently
                log_info("[WINDOW] Stay on top enabled, setting topmost=True")
                self.root.attributes('-topmost', True)
            else:
                # Stay on top is disabled - use temporary topmost to bring to front, then remove
                log_info("[WINDOW] Stay on top disabled, using temporary topmost")
                self.root.attributes('-topmost', True)
                self.root.update()  # Force update to apply topmost
                self.root.attributes('-topmost', False)
            
            log_info("[WINDOW] === show_window() completed successfully ===")
                
        except Exception as e:
            log_error(f"[WINDOW] ERROR in show_window: {e}", e)
            print(f"Error showing window: {e}")
            # Fallback: just show the window
            self.root.deiconify()
    
    def hide_window(self):
        """Hide window to system tray with slide animation"""
        try:
            log_info(f"[WINDOW] === hide_window() called at {time.time():.3f} ===")
            log_info(f"[WINDOW] Current hidden state: {self.is_hidden}")
            log_info(f"[WINDOW] Quick Add dialog open flag: {getattr(self, '_quick_add_dialog_open', False)}")
            
            log_info("[WINDOW] Setting hidden state to True")
            self.is_hidden = True
            
            # Close all open dialogs first to prevent focus issues
            log_info("[WINDOW] Closing all open dialogs")
            self.close_all_dialogs()
            log_info("[WINDOW] All dialogs closed")
            
            # Get current position
            current_geometry = self.root.geometry()
            if 'x' in current_geometry and '+' in current_geometry:
                # Extract current position
                parts = current_geometry.split('+')
                if len(parts) >= 3:
                    current_x = int(parts[1])
                    current_y = int(parts[2])
                    
                    # Use the animator for smooth slide-out
                    self.animator.slide_out(current_x, current_y)
                    return
            
            # Fallback: just hide
            log_info("[WINDOW] Using fallback withdraw()")
            self.root.withdraw()
            
            log_info("[WINDOW] === hide_window() completed successfully ===")
            
        except Exception as e:
            log_error(f"[WINDOW] ERROR in hide_window: {e}", e)
            print(f"Error in hide animation: {e}")
            # Fallback: just hide
            self.root.withdraw()
    
    def force_hide_window(self):
        """Force hide window without animation (for testing)"""
        # Close all open dialogs first
        self.close_all_dialogs()
        self.root.withdraw()
    
    def on_window_unmap(self, event):
        """Handle window unmapping (minimize or close)"""
        # Don't do anything here - let the protocol handle close, toggle handle minimize
        
    def on_window_map(self, event):
        """Handle window mapping (restore from minimize)"""
        # Don't do anything here - just for debugging
        
    def on_window_destroy(self, event):
        """Handle window destroy event"""
        # This should only be called when the window is actually being destroyed
        # If we get here, it means the window is closing for real
        if event.widget == self.root:
            self.quit_app()
    
        
    def quit_app(self):
        """Quit the application"""
        try:
            # Destroy the root window first
            self.root.quit()
            self.root.destroy()
        except Exception as e:
            log_error(f"Error destroying window: {e}")
        
        try:
            # Stop tray icon after window is destroyed
            if hasattr(self, 'tray_icon') and self.tray_icon:
                self.tray_icon.stop()
        except Exception as e:
            log_error(f"Error stopping tray icon: {e}")
        
        # Force exit
        import sys
        sys.exit(0)
        
    def toggle_stay_on_top(self):
        """Toggle stay on top functionality"""
        if hasattr(self.gui, 'stay_on_top_var'):
            if self.gui.stay_on_top_var.get():
                self.root.attributes('-topmost', True)
            else:
                self.root.attributes('-topmost', False)
                
    def load_data(self):
        """Load expense data from JSON file"""
        log_info(f"Loading data from: {self.expenses_file}")
        log_info(f"Data folder: {self.data_folder}")
        log_info(f"Current month: {self.current_month}")
        
        if os.path.exists(self.expenses_file):
            try:
                with open(self.expenses_file, 'r') as f:
                    data = json.load(f)
                    self.expenses = data.get('expenses', [])
                    # Calculate monthly_total from expenses (excluding future dates)
                    today = datetime.now().date()
                    self.monthly_total = sum(
                        expense['amount'] for expense in self.expenses
                        if datetime.strptime(expense['date'], '%Y-%m-%d').date() <= today
                    )
                    log_data_load("expenses", len(self.expenses), self.expenses_file)
                    log_info(f"Monthly total calculated: ${self.monthly_total:.2f}")
            except Exception as e:
                log_error(f"Error loading data from {self.expenses_file}", e)
                print(f"Error loading data: {e}")
                self.expenses = []
                self.monthly_total = 0.0
        else:
            log_warning(f"Expenses file not found: {self.expenses_file}")
            log_info(f"Current working directory: {os.getcwd()}")
            log_info(f"Files in current directory: {os.listdir('.')[:10]}")
            self.expenses = []
            self.monthly_total = 0.0
            
    def save_data(self):
        """Save expense data to JSON file"""
        os.makedirs(self.data_folder, exist_ok=True)
        data = {
            'expenses': self.expenses,
            'monthly_total': self.monthly_total
        }
        try:
            with open(self.expenses_file, 'w') as f:
                json.dump(data, f, indent=2)
            log_info(f"Data saved: {len(self.expenses)} expenses to {self.expenses_file}")
        except Exception as e:
            log_error(f"Error saving data to {self.expenses_file}", e)
            print(f"Error saving data: {e}")
            
    def add_expense(self):
        """Add a new expense"""
        def on_add_expense(expense_data):
            # Convert ExpenseData to dict format
            expense_dict = expense_data.to_dict()
            self.expenses.append(expense_dict)
            self.monthly_total += expense_dict['amount']
            self.save_data()
            self.gui.update_display()
            # Update tray icon tooltip with new total
            self.update_tray_tooltip()
        
        dialog = ExpenseAddDialog(self.root, on_add_expense)
        self.open_dialogs.append(dialog)  # Track the dialog
        
        # Set up cleanup when dialog is destroyed
        def on_dialog_destroy():
            if dialog in self.open_dialogs:
                self.open_dialogs.remove(dialog)
        
        dialog.dialog.bind('<Destroy>', lambda e: on_dialog_destroy())
    
    def show_quick_add_dialog(self):
        """Show quick add expense dialog without opening main window"""
        try:
            log_info(f"[DIALOG] === Quick Add Dialog Creation Started at {time.time():.3f} ===")
            
            # Prevent multiple dialogs from opening
            if hasattr(self, '_quick_add_dialog_open') and self._quick_add_dialog_open:
                log_info("[DIALOG] Dialog already open, ignoring request")
                return
            
            log_info("[DIALOG] Setting dialog flag to True")
            self._quick_add_dialog_open = True
            
            from datetime import datetime
            import tkinter as tk
            from tkinter import ttk, messagebox
            
            # Create dialog
            dialog = tk.Toplevel(self.root)
            dialog.title("Quick Add Expense")
            dialog.resizable(False, False)
            
            # IMPORTANT: Withdraw immediately to prevent flash at top-left corner
            dialog.withdraw()
            
            # Position dialog in same location as main window (lower-right corner)
            dialog.update_idletasks()
            screen_width = dialog.winfo_screenwidth()
            screen_height = dialog.winfo_screenheight()
            
            # Position to match main window: align with main window's left edge
            # Main window is 650px wide at (screen_width - 650 - 20)
            x = screen_width - 650 - 20  # Align with main window's left edge
            y = screen_height - 725 - 450  # Same 450px offset as main window
            
            # Adjust if dialog goes off screen
            if y < 0:
                y = 20
            if x < 0:
                x = 20
                
            dialog.geometry(f"400x725+{x}+{y}")
            
            # Content frame
            content_frame = ttk.Frame(dialog, padding="15")
            content_frame.pack(fill=tk.BOTH, expand=True)
            
            # Title
            title_label = ttk.Label(
                content_frame,
                text="Quick Add Expense",
                font=('Segoe UI', 14, 'bold')
            )
            title_label.pack(pady=(0, 15))
            
            # Current month and total info
            current_month = datetime.now().strftime("%B %Y")
            info_frame = ttk.Frame(content_frame)
            info_frame.pack(fill=tk.X, pady=(0, 20))
            
            month_label = ttk.Label(
                info_frame,
                text=current_month,
                font=('Segoe UI', 10),
                foreground='#1a1a1a'
            )
            month_label.pack(anchor=tk.CENTER)
            
            total_label = ttk.Label(
                info_frame,
                text=f"Current Total: ${self.monthly_total:.2f}",
                font=('Segoe UI', 10, 'bold'),
                foreground='#107c10'
            )
            total_label.pack(anchor=tk.CENTER, pady=(5, 0))
            
            # Amount field
            amount_frame = ttk.Frame(content_frame)
            amount_frame.pack(fill=tk.X, pady=(0, 10))
            
            amount_label = ttk.Label(amount_frame, text="Amount ($):")
            amount_label.pack(anchor=tk.W)
            
            amount_var = tk.StringVar()
            
            # Validation function for amount field (numeric only, max 2 decimals)
            def validate_quick_add_amount(new_value):
                """
                Validate amount input in real-time
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
                    parts = new_value.split('.')
                    if len(parts[1]) > 2:
                        return False
                
                # Check if it's a valid number format
                try:
                    if new_value != '.':
                        float(new_value)
                except ValueError:
                    return False
                
                return True
            
            # Register validation command
            vcmd = (dialog.register(validate_quick_add_amount), '%P')
            
            amount_entry = ttk.Entry(amount_frame, textvariable=amount_var, font=('Segoe UI', 10),
                                    validate='key', validatecommand=vcmd)
            amount_entry.pack(fill=tk.X, pady=(5, 0))
            amount_entry.focus_set()
            
            # Number pad
            pad_frame = ttk.LabelFrame(content_frame, text="", padding="10")
            pad_frame.pack(fill=tk.X, pady=(0, 10))
            
            # Configure style for number pad buttons
            style = ttk.Style()
            style.configure("NumPad.TButton", 
                           font=("Segoe UI", 12, "bold"),
                           padding=(8, 10))
            
            # Button layout: 3x4 grid
            buttons = [
                ['7', '8', '9'],
                ['4', '5', '6'],
                ['1', '2', '3'],
                ['0', '.', 'C']
            ]
            
            # Helper functions for number pad
            def on_number_click(value):
                """Handle number pad button clicks"""
                current = amount_var.get()
                
                # Handle decimal point
                if value == '.':
                    if '.' not in current:
                        if not current:
                            amount_var.set('0.')
                        else:
                            amount_var.set(current + '.')
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
                
                # If current value is "0", replace it
                if current == '0':
                    amount_var.set(value)
                else:
                    amount_var.set(current + value)
            
            def on_clear_click():
                """Clear the amount field"""
                amount_var.set('')
            
            # Create number pad buttons
            for row_idx, row in enumerate(buttons):
                pad_frame.columnconfigure(0, weight=1)
                pad_frame.columnconfigure(1, weight=1)
                pad_frame.columnconfigure(2, weight=1)
                
                for col_idx, btn_text in enumerate(row):
                    if btn_text == 'C':
                        btn = ttk.Button(pad_frame, text=btn_text, 
                                       command=on_clear_click,
                                       style="NumPad.TButton",
                                       width=2)
                    else:
                        btn = ttk.Button(pad_frame, text=btn_text,
                                       command=lambda t=btn_text: on_number_click(t),
                                       style="NumPad.TButton",
                                       width=2)
                    
                    btn.grid(row=row_idx, column=col_idx, padx=5, pady=5, sticky=(tk.W, tk.E))
            
            # Description field
            desc_frame = ttk.Frame(content_frame)
            desc_frame.pack(fill=tk.X, pady=(0, 20))
            
            desc_label = ttk.Label(desc_frame, text="Description:")
            desc_label.pack(anchor=tk.W)
            
            desc_entry = ttk.Entry(desc_frame, font=('Segoe UI', 10))
            desc_entry.pack(fill=tk.X, pady=(5, 0))
            
            # Buttons frame
            button_frame = ttk.Frame(content_frame)
            button_frame.pack(fill=tk.X)
            
            def on_add():
                """Handle add button click"""
                try:
                    # Validate amount
                    amount_str = amount_var.get().strip()
                    if not amount_str:
                        messagebox.showerror("Error", "Please enter an amount", parent=dialog)
                        return
                    
                    try:
                        amount = float(amount_str)
                        if amount <= 0:
                            messagebox.showerror("Error", "Amount must be greater than 0", parent=dialog)
                            return
                    except ValueError:
                        messagebox.showerror("Error", "Please enter a valid number", parent=dialog)
                        return
                    
                    # Validate description
                    description = desc_entry.get().strip()
                    if not description:
                        messagebox.showerror("Error", "Please enter a description", parent=dialog)
                        return
                    
                    # Add expense
                    expense_dict = {
                        'date': datetime.now().strftime("%Y-%m-%d"),
                        'amount': amount,
                        'description': description
                    }
                    
                    self.expenses.append(expense_dict)
                    self.monthly_total += amount
                    self.save_data()
                    self.gui.update_display()
                    self.update_tray_tooltip()
                    
                    log_info(f"Quick add expense: ${amount:.2f} - {description}")
                    dialog.destroy()
                    
                except Exception as e:
                    log_error("Error in quick add", e)
                    messagebox.showerror("Error", f"Failed to add expense: {e}", parent=dialog)
            
            def on_cancel():
                """Handle cancel button click"""
                dialog.destroy()
            
            # Add button
            add_button = ttk.Button(
                button_frame,
                text="Add",
                command=on_add
            )
            add_button.pack(side=tk.LEFT, padx=(0, 10))
            
            # Cancel button
            cancel_button = ttk.Button(
                button_frame,
                text="Cancel",
                command=on_cancel
            )
            cancel_button.pack(side=tk.LEFT)
            
            # Bind Enter key for sequential field navigation
            def handle_amount_enter(event):
                """Enter in amount field moves to description"""
                desc_entry.focus_set()
                return "break"  # Prevent default behavior
            
            def handle_description_enter(event):
                """Enter in description field submits the form"""
                on_add()
                return "break"  # Prevent default behavior
            
            amount_entry.bind('<Return>', handle_amount_enter)
            desc_entry.bind('<Return>', handle_description_enter)
            dialog.bind('<Escape>', lambda e: on_cancel())
            
            log_info(f"[DIALOG] Dialog positioned at x={x}, y={y}")
            
            # Show the dialog now that it's fully configured and positioned
            log_info("[DIALOG] Calling deiconify() to show dialog")
            dialog.deiconify()
            log_info("[DIALOG] Dialog is now visible")
            
            # Set window attributes after showing
            if self.is_hidden:
                log_info("[DIALOG] Main window is hidden, using grab_set()")
                dialog.grab_set()
            else:
                # Make dialog stay on top but don't grab focus
                log_info("[DIALOG] Main window is visible, setting topmost attribute")
                dialog.attributes('-topmost', True)
            
            # Set initial focus on amount entry field
            log_info("[DIALOG] Setting focus to dialog and amount entry")
            dialog.update()  # Ensure dialog is fully rendered
            dialog.focus_force()  # Force focus on the dialog window
            amount_entry.focus_set()  # Set focus on amount entry
            log_info("[DIALOG] Focus set successfully")
            
            # IMPORTANT: Bind FocusOut AFTER dialog is shown and focused
            # This prevents the initial show/focus from triggering auto-close
            def on_focus_out(event):
                log_info(f"[DIALOG] FocusOut event triggered by widget: {event.widget}")
                log_info("[DIALOG] Scheduling focus check with 50ms delay")
                # Small delay to check if focus truly left the dialog window
                dialog.after(50, lambda: check_focus_and_close())
            
            def check_focus_and_close():
                log_info("[DIALOG] === Focus Check Started ===")
                try:
                    # Check if dialog still exists and focus is outside the dialog
                    if not dialog.winfo_exists():
                        log_info("[DIALOG] Dialog no longer exists, aborting close check")
                        return
                    
                    log_info("[DIALOG] Dialog exists, checking focus location")
                    focused = dialog.focus_get()
                    log_info(f"[DIALOG] Currently focused widget: {focused}")
                    
                    # Close if no widget has focus or focus is in a different window
                    if focused is None:
                        log_info("[DIALOG] No widget has focus - DESTROYING DIALOG")
                        dialog.destroy()
                        self._quick_add_dialog_open = False
                        log_info("[DIALOG] Dialog destroyed and flag set to False")
                    elif focused.winfo_toplevel() != dialog:
                        log_info(f"[DIALOG] Focus is in different window ({focused.winfo_toplevel()}) - DESTROYING DIALOG")
                        dialog.destroy()
                        self._quick_add_dialog_open = False
                        log_info("[DIALOG] Dialog destroyed and flag set to False")
                    else:
                        log_info("[DIALOG] Focus still inside dialog - keeping open")
                except Exception as e:
                    log_error(f"[DIALOG] ERROR during check_focus_and_close: {e}", e)
                    try:
                        self._quick_add_dialog_open = False
                    except:
                        pass  # Dialog might already be destroyed
                
                log_info("[DIALOG] === Focus Check Complete ===")
            
            # Bind FocusOut to all widgets in the dialog recursively
            def bind_focus_out_recursive(widget):
                try:
                    log_info(f"[DIALOG] Binding FocusOut to widget: {widget}")
                    widget.bind('<FocusOut>', on_focus_out, add='+')
                    for child in widget.winfo_children():
                        bind_focus_out_recursive(child)
                except Exception as e:
                    log_error(f"[DIALOG] ERROR binding FocusOut to {widget}: {e}", e)
            
            # Use after() to bind focus events after the dialog is fully initialized
            log_info("[DIALOG] Scheduling FocusOut binding with 100ms delay")
            dialog.after(100, lambda: self._bind_dialog_focus_out(dialog, bind_focus_out_recursive))
            
            # Track dialog
            self.open_dialogs.append(dialog)
            
            # Setup cleanup
            def on_dialog_destroy():
                if dialog in self.open_dialogs:
                    self.open_dialogs.remove(dialog)
                # Reset the flag when dialog closes
                self._quick_add_dialog_open = False
            
            dialog.bind('<Destroy>', lambda e: on_dialog_destroy())
            
        except Exception as e:
            log_error("[DIALOG] ERROR in show_quick_add_dialog", e)
            # Reset flag on error
            self._quick_add_dialog_open = False
    
    def _bind_dialog_focus_out(self, dialog, bind_func):
        """Helper method to bind FocusOut events with logging"""
        log_info("[DIALOG] === Starting FocusOut Binding ===")
        try:
            bind_func(dialog)
            log_info("[DIALOG] FocusOut binding complete for all widgets")
        except Exception as e:
            log_error(f"[DIALOG] ERROR during FocusOut binding: {e}", e)
        log_info("[DIALOG] === FocusOut Binding Complete ===")
            
    def close_all_dialogs(self):
        """Close all open dialogs to prevent focus issues when hiding window"""
        try:
            log_debug(f"Closing {len(self.open_dialogs)} open dialogs...")
            for dialog in self.open_dialogs[:]:  # Use slice to avoid modification during iteration
                try:
                    if hasattr(dialog, 'dialog') and dialog.dialog.winfo_exists():
                        dialog.dialog.destroy()
                        log_debug("Dialog destroyed successfully")
                except Exception as e:
                    log_error(f"Error destroying dialog: {e}")
            self.open_dialogs.clear()
            log_info("All dialogs closed")
        except Exception as e:
            log_error("Error closing dialogs", e)
    
    def view_expenses(self):
        """View all expenses in a table"""
        self.show_expense_list_page()
        
    def show_expense_list_page(self):
        """Show the expense list page within the main window"""
        self.current_page = "expense_list"
        self.gui.show_expense_list_page()
        
    def export_expenses_dialog(self):
        """Show export dialog for exporting expenses to Excel or PDF"""
        try:
            # Use the new export system with dialog
            export_expenses(self.expenses, self.current_month)
        except Exception as e:
            log_error("Error opening export dialog", e)
            messagebox.showerror("Export Error", f"Failed to open export dialog: {e}")
    
    def import_expenses_dialog(self):
        """Show file picker and import expense data from JSON backup"""
        try:
            # Use the import system
            import_expense_backup(self)
        except Exception as e:
            log_error("Error importing backup", e)
            messagebox.showerror("Import Error", f"Failed to import backup: {e}")
            
    def get_day_progress(self):
        """Get current day progress in the month"""
        today = datetime.now()
        current_day = today.day
        total_days = calendar.monthrange(today.year, today.month)[1]
        return current_day, total_days
        
    def get_week_progress(self):
        """Get current week progress in the month"""
        today = datetime.now()
        current_day = today.day
        
        # Base week number (1 for days 1-7, 2 for days 8-14, etc.)
        base_week = ((current_day - 1) // 7) + 1
        
        # Position within the week (0-6 for the 7 days)
        day_in_week = (current_day - 1) % 7
        
        # Decimal component (0.0 for first day, 0.1 for second, ... 0.9 for last day)
        week_decimal = day_in_week / 10.0
        
        precise_week = base_week + week_decimal
        
        # Total weeks in month (estimate based on total days)
        total_days = calendar.monthrange(today.year, today.month)[1]
        total_weeks = (total_days // 7) + (1 if total_days % 7 > 0 else 0)
        
        return precise_week, total_weeks
        
    def get_daily_average(self):
        """Calculate average spending per day: (month total ÷ days elapsed)"""
        if not self.expenses:
            return 0.0, 0
            
        # Get current month's expenses (excluding future dates)
        today = datetime.now()
        month_start = today.replace(day=1)
        month_expenses = [e for e in self.expenses 
                         if datetime.strptime(e['date'], '%Y-%m-%d') >= month_start
                         and datetime.strptime(e['date'], '%Y-%m-%d').date() <= today.date()]
        
        monthly_total = sum(e['amount'] for e in month_expenses)
        days_elapsed = today.day
        
        # Average per day = monthly total ÷ days elapsed
        avg_per_day = monthly_total / days_elapsed if days_elapsed > 0 else 0
        
        return avg_per_day, days_elapsed
            
    def get_weekly_average(self):
        """Calculate average spending per week: (month total ÷ weeks elapsed in month)"""
        if not self.expenses:
            return 0.0, 0
            
        # Get current month's expenses (excluding future dates)
        today = datetime.now()
        month_start = today.replace(day=1)
        month_expenses = [e for e in self.expenses 
                         if datetime.strptime(e['date'], '%Y-%m-%d') >= month_start
                         and datetime.strptime(e['date'], '%Y-%m-%d').date() <= today.date()]
        
        monthly_total = sum(e['amount'] for e in month_expenses)
        
        # Calculate weeks elapsed: (current day - 1) ÷ 7 + 1
        # This gives us the week number we're in (1, 2, 3, 4, etc.)
        current_day = today.day
        weeks_elapsed = ((current_day - 1) // 7) + 1
        
        # Average per week = monthly total ÷ weeks elapsed
        avg_per_week = monthly_total / weeks_elapsed if weeks_elapsed > 0 else 0
        
        return avg_per_week, weeks_elapsed
            
    def get_weekly_pace(self):
        """Calculate current week's spending pace: (this week's total ÷ days elapsed this week)"""
        if not self.expenses:
            return 0.0, 0
            
        # Get current week's expenses (Monday to today, excluding future dates)
        today = datetime.now()
        week_start = today - timedelta(days=today.weekday())  # Monday of current week
        week_expenses = [e for e in self.expenses 
                        if datetime.strptime(e['date'], '%Y-%m-%d').date() >= week_start.date()
                        and datetime.strptime(e['date'], '%Y-%m-%d').date() <= today.date()]
        
        weekly_total = sum(e['amount'] for e in week_expenses)
        days_elapsed = (today - week_start).days + 1  # Days from Monday to today (inclusive)
        
        # Pace = weekly total ÷ days elapsed in current week
        pace_per_day = weekly_total / days_elapsed if days_elapsed > 0 else 0
        
        # Return pace and days for context
        return pace_per_day, days_elapsed
            
    def get_monthly_trend_analysis(self):
        """Get previous month's total and name"""
        # Get previous month date and name
        prev_month_date = datetime.now().replace(day=1) - timedelta(days=1)
        prev_month_key = prev_month_date.strftime('%Y-%m')
        prev_month_name = prev_month_date.strftime('%B %Y')  # e.g., "September 2025"
        
        # Check if we have previous month data file
        prev_data_folder = f"data_{prev_month_key}"
        prev_expenses_file = os.path.join(prev_data_folder, 'expenses.json')
        
        if os.path.exists(prev_expenses_file):
            try:
                with open(prev_expenses_file, 'r') as f:
                    data = json.load(f)
                    # Handle both old format (list) and new format (dict with 'expenses' key)
                    if isinstance(data, list):
                        prev_expenses = data
                    elif isinstance(data, dict):
                        prev_expenses = data.get('expenses', [])
                    else:
                        prev_expenses = []
                    
                    prev_total = sum(e['amount'] for e in prev_expenses)
                    return f"${prev_total:.2f}", prev_month_name
            except Exception as e:
                log_error("Error loading previous month data", e)
                return "$0.00", prev_month_name
        else:
            return "$0.00", prev_month_name
    
    def get_median_expense(self):
        """Calculate median expense amount (typical expense size)"""
        from datetime import datetime
        today = datetime.now()
        
        # Filter out future expenses
        past_expenses = [e for e in self.expenses 
                        if datetime.strptime(e['date'], '%Y-%m-%d').date() <= today.date()]
        
        if not past_expenses:
            return 0.0, 0
        
        # Get all expense amounts and sort them
        amounts = sorted([e['amount'] for e in past_expenses])
        count = len(amounts)
        
        # Calculate median
        if count % 2 == 0:
            # Even number: average of two middle values
            median = (amounts[count // 2 - 1] + amounts[count // 2]) / 2
        else:
            # Odd number: middle value
            median = amounts[count // 2]
        
        return median, count
    
    def get_largest_expense(self):
        """Get the largest expense amount and description"""
        from datetime import datetime
        today = datetime.now()
        
        # Filter out future expenses
        past_expenses = [e for e in self.expenses 
                        if datetime.strptime(e['date'], '%Y-%m-%d').date() <= today.date()]
        
        if not past_expenses:
            return 0.0, "No expenses"
        
        # Find the largest expense
        largest = max(past_expenses, key=lambda e: e['amount'])
        
        return largest['amount'], largest['description']
        
    def run(self):
        """Run the application"""
        # Start main GUI
        # Note: Protocol handler is already set up in __init__ to quit_app
        
        try:
            self.root.mainloop()
        except KeyboardInterrupt:
            self.shutdown()
    
            
    def shutdown(self):
        """Shutdown the application"""
        if hasattr(self, 'tray_icon') and self.tray_icon:
            self.tray_icon.stop()
        self.root.quit()

if __name__ == "__main__":
    app = ExpenseTracker()
    app.run()
