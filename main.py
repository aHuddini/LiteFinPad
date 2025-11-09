import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
from datetime import datetime, timedelta
import calendar
import threading
import queue
import sys
import time
# PIL removed - icon.ico is bundled directly by PyInstaller
import ctypes
from expense_table import ExpenseTableManager, ExpenseAddDialog, ExpenseData
from gui import LiteFinPadGUI
from tray_icon_manager import TrayIconManager
from error_logger import log_error, log_info, log_warning, log_debug, error_logger, log_data_load
from export_data import export_expenses
from import_data import import_expense_backup
from window_animation import create_window_animator
from analytics import ExpenseAnalytics
from data_manager import ExpenseDataManager
from validation import InputValidation, ValidationPresets, ValidationResult
from widgets.number_pad import NumberPadWidget
from dialog_helpers import DialogHelper
from window_manager import WindowManager
from month_viewer import MonthViewer
import config
from date_utils import DateUtils
from description_autocomplete import DescriptionHistory
from widgets import AutoCompleteEntry

def _configure_process_dpi_awareness():
    """
    Configure process-level DPI awareness for crisp text on high-DPI displays.
    
    Tries multiple methods in order of preference for Windows version compatibility.
    This prevents blurry text on high-resolution displays (4K, etc.).
    
    Returns:
        bool: True if any method succeeded, False if all failed
    """
    dpi_methods = [
        # (library, method_name, arguments, description)
        (ctypes.windll.shcore, 'SetProcessDpiAwareness', (1,), 'Windows 8.1+'),
        (ctypes.windll.user32, 'SetProcessDPIAware', (), 'Windows Vista+'),
    ]
    
    for lib, method_name, args, win_version in dpi_methods:
        try:
            method = getattr(lib, method_name)
            method(*args)
            log_debug(f"Process DPI awareness configured using {method_name} ({win_version})")
            return True
        except (AttributeError, OSError):
            # Method not available on this Windows version
            continue
    
    # None worked - log for debugging but continue (DPI awareness is optional UI polish)
    log_debug("Process DPI awareness not configured (older Windows or unavailable)")
    return False

# Configure DPI awareness at module level (before creating windows)
_configure_process_dpi_awareness()

# Setup debug logger



class ExpenseTracker:
    def __init__(self):
        # Initialize error logging
        error_logger.log_application_start()
        
        # Initialize month viewer for navigation and archive mode
        self.month_viewer = MonthViewer(data_directory=".")
        
        # Use month viewer for month tracking
        self.current_month = self.month_viewer.actual_month
        self.viewed_month = self.month_viewer.viewed_month
        self.viewing_mode = self.month_viewer.viewing_mode
        
        # Note: current_month is already in YYYY-MM format from month_viewer
        self.data_folder = f"data_{self.current_month}"
        self.expenses_file = os.path.join(self.data_folder, "expenses.json")
        self.calculations_file = os.path.join(self.data_folder, "calculations.json")
        self.expenses = []
        self.monthly_total = 0.0
        self.current_page = "main"  # Track current page
        self.open_dialogs = []  # Track open dialogs for proper cleanup
        self.gui_queue = queue.Queue()  # Thread-safe queue for GUI operations from background threads
        self._shutting_down = False  # Guard flag to prevent duplicate shutdown calls
        
        # Initialize description history for auto-complete
        self.description_history = DescriptionHistory()
        
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
        
        # Configure DPI scaling for crisp text rendering
        self.configure_dpi_scaling()
        
        # Create window animator
        self.animator = create_window_animator(self.root)
        
        # Create window manager (gui will be set after GUI initialization)
        self.window_manager = WindowManager(
            root=self.root,
            animator=self.animator,
            gui=None,  # Will be set after GUI is created
            close_dialogs_callback=self.close_all_dialogs,
            quit_callback=self.quit_app
        )
        
        # Initialize GUI using separated GUI class
        self.gui = LiteFinPadGUI(self.root, self)
        
        # Set GUI reference in window manager now that GUI is created
        self.window_manager.gui = self.gui
        
        # Create tray icon manager and start tray icon
        self.tray_icon_manager = TrayIconManager(self)
        self.tray_icon_manager.create()
        
        # Hide window initially - use tray icon to access
        self.root.withdraw()
        
    def configure_dpi_scaling(self):
        """
        Configure Tkinter DPI scaling for crisp text on high-DPI displays.
        
        Queries the window's DPI and sets Tkinter's scaling factor accordingly.
        Falls back to default scaling if detection fails.
        """
        try:
            # Get window handle and query DPI
            window_handle = self.root.winfo_id()
            dpi = ctypes.windll.user32.GetDpiForWindow(window_handle)
            
            if dpi <= 0:
                # Invalid DPI value returned
                log_debug("DPI detection returned invalid value, using default scaling")
                self.root.tk.call('tk', 'scaling', 1.0)
                return
            
            # Calculate scaling factor (96 DPI is standard/100% scaling)
            scaling_factor = dpi / 96.0
            
            # Apply scaling to Tkinter
            self.root.tk.call('tk', 'scaling', scaling_factor)
            log_debug(f"Tkinter DPI scaling configured: {scaling_factor:.2f}x (DPI: {dpi})")
            
        except (AttributeError, OSError) as e:
            # Expected on older Windows or if window handle not ready
            log_debug(f"DPI scaling not configured (expected on older Windows): {e}")
            self.root.tk.call('tk', 'scaling', 1.0)
            
        except Exception as e:
            # Unexpected error - log as warning for debugging
            log_warning(f"Unexpected error configuring DPI scaling: {e}")
            self.root.tk.call('tk', 'scaling', 1.0)
        
    def get_icon_path(self):
        """Get the correct icon path for both development and PyInstaller builds"""
        try:
            # PyInstaller detection: Standard pattern for detecting bundled executables.
            # _MEIPASS is the documented PyInstaller attribute that contains the temp
            # directory path where bundled files are extracted. This is the official
            # way to detect PyInstaller builds (not a workaround).
            if hasattr(sys, '_MEIPASS'):
                # PyInstaller mode: try primary location first
                icon_path = os.path.join(sys._MEIPASS, 'icon.ico')
                if os.path.exists(icon_path):
                    return icon_path
                
                # Try alternative locations
                alt_paths = [
                    os.path.join(sys._MEIPASS, 'dist', 'icon.ico'),
                    os.path.join(os.path.dirname(sys.executable), 'icon.ico'),
                    os.path.join(os.path.dirname(sys.executable), 'dist', 'icon.ico')
                ]
                for alt_path in alt_paths:
                    if os.path.exists(alt_path):
                        return alt_path
                
                # Icon not found - log warning and return None
                log_warning("[ICON] Icon not found in PyInstaller bundle")
                return None
            else:
                # Development mode: simple check
                icon_path = "icon.ico"
                if os.path.exists(icon_path):
                    return icon_path
                
                log_warning("[ICON] Icon not found in development mode")
                return None
                
        except Exception as e:
            log_error(f"[ICON] Error resolving icon path: {e}", e)
            return None
    
    def create_default_icon(self):
        """Fallback - icon.ico should always be bundled by PyInstaller"""
        # PIL removed for size optimization
        # icon.ico is bundled by PyInstaller via --icon and --add-data flags
        # If icon is None, tkinter will use default
        return None
        
    def quit_app(self):
        """
        Quit the application with proper cleanup.
        
        Ensures all resources are cleaned up in the correct order:
        1. Close any open dialogs
        2. Stop the tray icon
        3. Destroy the GUI window
        """
        # Guard against duplicate calls (e.g., from WM_DELETE_WINDOW protocol during destroy)
        if self._shutting_down:
            return
        self._shutting_down = True
        
        try:
            log_debug("Application shutdown initiated...")
            
            # 1. Close any open dialogs first
            self.close_all_dialogs()
            
            # 2. Stop tray icon before destroying window
            # Defensive check: tray_icon_manager may not exist if initialization failed
            # or if shutdown occurs before full initialization. Initialization order can
            # vary, and shutdown sequence must be resilient to partial initialization.
            if hasattr(self, 'tray_icon_manager') and self.tray_icon_manager:
                self.tray_icon_manager.stop()
            
            # 3. Destroy the GUI window
            self.root.quit()
            self.root.destroy()
            
            log_info("Application shutdown complete")
            
        except Exception as e:
            log_error(f"Error during shutdown: {e}")
            # Force exit even if cleanup fails
            import sys
            sys.exit(1)
                
    def load_data(self, month_key: str = None):
        """
        Load expense data from JSON file
        
        Args:
            month_key: Month to load (YYYY-MM format). If None, uses viewed_month.
        """
        if month_key is None:
            month_key = self.viewed_month
        
        # Get paths for the target month
        data_folder = f"data_{month_key}"
        expenses_file = os.path.join(data_folder, "expenses.json")
        
        # Load expenses
        self.expenses, self.monthly_total = ExpenseDataManager.load_expenses(
            expenses_file,
            data_folder,
            month_key
        )
    
    def switch_month(self, month_key: str):
        """
        Switch to viewing a different month
        
        Args:
            month_key: Month to switch to (YYYY-MM format)
        """
        # Update month viewer state
        self.viewed_month, self.viewing_mode = self.month_viewer.switch_to_month(month_key)
        
        # Load data for the new month
        self.load_data(month_key)
        
        # Update GUI to reflect new mode
        self.gui.archive_mode_manager.refresh_ui()
        
        # Log the switch
        log_info(f"Switched to {month_key} ({self.viewing_mode} mode)")
            
    def save_data(self):
        """Save expense data to JSON file"""
        ExpenseDataManager.save_expenses(
            self.data_folder,
            self.expenses_file,
            self.expenses,
            self.monthly_total
        )
        # Also save calculations metadata
        self._save_calculations(self.calculations_file, self.current_month, self.monthly_total)
    
    def add_expense_to_correct_month(self, expense_dict):
        """
        Add expense to the correct month's data folder based on expense date.
        If the expense belongs to a previous month, it will be saved to that month's folder.
        
        Args:
            expense_dict (dict): Expense dictionary with 'date', 'amount', 'description'
            
        Returns:
            str: Message to display to user about where the expense was saved
        """
        from datetime import datetime
        from tkinter import messagebox
        
        # Parse the expense date to determine target month
        expense_date = DateUtils.parse_date(expense_dict['date'])
        if not expense_date:
            return "Error: Invalid expense date"
        
        target_month = expense_date.strftime("%Y-%m")  # e.g., "2025-09"
        
        # Check if expense belongs to current month, past month, or future month
        if target_month == self.current_month:
            # Add to current month (existing behavior)
            self.expenses.append(expense_dict)
            self.monthly_total += expense_dict['amount']
            self.save_data()
            return None  # No special message needed
        else:
            # Expense belongs to a different month - save to that month's folder
            target_data_folder = f"data_{target_month}"
            target_expenses_file = os.path.join(target_data_folder, "expenses.json")
            target_calculations_file = os.path.join(target_data_folder, "calculations.json")
            
            # Load the target month's data
            target_expenses, target_total = ExpenseDataManager.load_expenses(
                target_expenses_file,
                target_data_folder,
                target_month
            )
            
            # Add expense to target month
            target_expenses.append(expense_dict)
            target_total += expense_dict['amount']
            
            # Save expenses to target month's folder
            ExpenseDataManager.save_expenses(
                target_data_folder,
                target_expenses_file,
                target_expenses,
                target_total
            )
            
            # Save calculations metadata for future viewing
            self._save_calculations(target_calculations_file, target_month, target_total)
            
            # Parse month name for user message
            month_name = expense_date.strftime("%B %Y")  # e.g., "September 2025"
            
            # Determine if it's a past or future expense
            if target_month < self.current_month:
                # Past expense
                return f"💡 Past expense saved to {month_name} data folder (${expense_dict['amount']:.2f})"
            else:
                # Future expense
                return f"💡 Future expense saved to {month_name} data folder (${expense_dict['amount']:.2f})"
    
    def _save_calculations(self, calculations_file, month, total):
        """
        Save calculations metadata for a given month.
        This enables viewing previous months' data in the future.
        
        Args:
            calculations_file (str): Path to calculations.json file
            month (str): Month string (YYYY-MM)
            total (float): Monthly total
        """
        from datetime import datetime
        import json
        
        calculations_data = {
            "current_month": month,
            "monthly_total": total,
            "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        try:
            with open(calculations_file, 'w') as f:
                json.dump(calculations_data, f, indent=2)
            log_info(f"Calculations saved for {month}: ${total:.2f}")
        except Exception as e:
            log_error(f"Error saving calculations to {calculations_file}", e)
            print(f"Error saving calculations: {e}")
            
    def add_expense(self):
        """Add a new expense"""
        def on_add_expense(expense_data):
            from tkinter import messagebox
            
            # Convert ExpenseData to dict format
            expense_dict = expense_data.to_dict()
            
            # Add expense to correct month folder
            message = self.add_expense_to_correct_month(expense_dict)
            
            # Update display and tray icon
            self.gui.update_display()
            self.tray_icon_manager.update_tooltip()
            
            # Show message if expense was saved to a previous month
            if message:
                messagebox.showinfo("Cross-Month Save", message)
        
        dialog = ExpenseAddDialog(self.root, on_add_expense, self.description_history)
        self.open_dialogs.append(dialog)  # Track the dialog
        
        # Set up cleanup when dialog is destroyed
        def on_dialog_destroy():
            if dialog in self.open_dialogs:
                self.open_dialogs.remove(dialog)
        
        dialog.dialog.bind('<Destroy>', lambda e: on_dialog_destroy())
    
    def show_quick_add_dialog(self):
        """
        Show quick add expense dialog without opening main window.
        Thread-safe: Posts request to GUI queue for main thread execution.
        """
        log_info("[DIALOG] Quick Add requested - posting to GUI queue")
        self.gui_queue.put(self._show_quick_add_dialog_main_thread)
    
    def _show_quick_add_dialog_main_thread(self):
        """
        PRIVATE: Create Quick Add dialog in main thread.
        Called via GUI queue from show_quick_add_dialog().
        """
        try:
            log_info(f"[DIALOG] === Quick Add Dialog Creation Started at {time.time():.3f} ===")
            
            # Prevent multiple dialogs from opening
            # Defensive check: _quick_add_dialog_open may not exist on first call.
            # This flag is set during dialog creation, so we check existence before
            # accessing to handle the initial state gracefully.
            if hasattr(self, '_quick_add_dialog_open') and self._quick_add_dialog_open:
                log_info("[DIALOG] Dialog already open, ignoring request")
                return
            
            log_info("[DIALOG] Setting dialog flag to True")
            self._quick_add_dialog_open = True
            
            from datetime import datetime
            import tkinter as tk
            from tkinter import ttk, messagebox
            
            # Create dialog using DialogHelper (no transient for tray icon independence)
            dialog = DialogHelper.create_dialog_no_transient(
                self.root,
                "Quick Add Expense",
                config.Dialog.ADD_EXPENSE_WIDTH,
                config.Dialog.ADD_EXPENSE_WITH_NUMPAD_HEIGHT
            )
            
            # Position dialog using DialogHelper
            screen_width = dialog.winfo_screenwidth()
            screen_height = dialog.winfo_screenheight()
            DialogHelper.position_with_main_window(
                dialog, 
                screen_width, 
                screen_height,
                main_width=650,
                main_height=725,
                offset=450,
                dialog_width=config.Dialog.ADD_EXPENSE_WIDTH,
                dialog_height=config.Dialog.ADD_EXPENSE_WITH_NUMPAD_HEIGHT
            )
            
            # Content frame
            content_frame = ttk.Frame(dialog, padding="15")
            content_frame.pack(fill=tk.BOTH, expand=True)
            
            # Title
            title_label = ttk.Label(
                content_frame,
                text="Quick Add Expense",
                font=config.Fonts.HEADER
            )
            title_label.pack(pady=(0, 15))
            
            # Current month and total info
            current_month = datetime.now().strftime("%B %Y")
            info_frame = ttk.Frame(content_frame)
            info_frame.pack(fill=tk.X, pady=(0, 20))
            
            month_label = ttk.Label(
                info_frame,
                text=current_month,
                font=config.Fonts.LABEL,
                foreground=config.Colors.TEXT_BLACK
            )
            month_label.pack(anchor=tk.CENTER)
            
            total_label = ttk.Label(
                info_frame,
                text=f"Current Total: ${self.monthly_total:.2f}",
                font=config.get_font(config.Fonts.SIZE_SMALL, 'bold'),
                foreground=config.Colors.GREEN_PRIMARY
            )
            total_label.pack(anchor=tk.CENTER, pady=(5, 0))
            
            # Amount field
            amount_frame = ttk.Frame(content_frame)
            amount_frame.pack(fill=tk.X, pady=(0, 10))
            
            amount_label = ttk.Label(amount_frame, text="Amount ($):")
            amount_label.pack(anchor=tk.W)
            
            amount_var = tk.StringVar()
            
            # Register validation command (uses shared InputValidation module)
            vcmd = (dialog.register(InputValidation.validate_amount), '%P')
            
            amount_entry = ttk.Entry(amount_frame, textvariable=amount_var, font=config.Fonts.LABEL,
                                    validate='key', validatecommand=vcmd)
            amount_entry.pack(fill=tk.X, pady=(5, 0))
            amount_entry.focus_set()
            
            # Number pad widget
            number_pad = NumberPadWidget(content_frame, amount_var)
            number_pad.pack(fill=tk.X, pady=(0, 10))
            
            # Description field
            desc_frame = ttk.Frame(content_frame)
            desc_frame.pack(fill=tk.X, pady=(0, 20))
            
            desc_label = ttk.Label(desc_frame, text="Description:")
            desc_label.pack(anchor=tk.W)
            
            # Auto-complete entry for description
            def get_suggestions(partial_text, limit=None):
                """Get suggestions, accepting optional limit parameter"""
                if limit is not None:
                    return self.description_history.get_suggestions(partial_text, limit=limit)
                else:
                    return self.description_history.get_suggestions(partial_text)
            
            desc_entry = AutoCompleteEntry(
                desc_frame,
                get_suggestions_callback=get_suggestions,
                show_on_focus=self.description_history.should_show_on_focus(),
                min_chars=self.description_history.get_min_chars(),
                font=config.Fonts.LABEL
            )
            desc_entry.pack(fill=tk.X, pady=(5, 0))
            
            # Buttons frame
            button_frame = ttk.Frame(content_frame)
            button_frame.pack(fill=tk.X)
            
            # Flag to prevent auto-close when showing validation errors
            dialog._showing_messagebox = False
            
            def on_add():
                """Handle add button click"""
                try:
                    # Validate all fields using preset validator
                    result = ValidationPresets.quick_add_expense(
                        amount_var.get(),
                        desc_entry.get()
                    )
                    
                    # If validation failed, show error and focus appropriate field
                    if not result:
                        dialog._showing_messagebox = True
                        messagebox.showerror("Validation Error", result.error_message, parent=dialog)
                        dialog._showing_messagebox = False
                        dialog.focus_force()
                        
                        # Auto-focus the field that failed validation
                        if result.error_field == "amount":
                            amount_entry.focus_set()
                        elif result.error_field == "description":
                            desc_entry.focus_set()
                        return
                    
                    # Get sanitized values from validation result
                    sanitized = result.sanitized_value
                    
                    # Add expense with pre-validated, cleaned data
                    expense_dict = {
                        'date': datetime.now().strftime("%Y-%m-%d"),
                        'amount': sanitized['amount'],
                        'description': sanitized['description']
                    }
                    
                    self.expenses.append(expense_dict)
                    self.monthly_total += sanitized['amount']
                    
                    # Track description for auto-complete
                    self.description_history.add_or_update(
                        sanitized['description'],
                        sanitized['amount']
                    )
                    
                    self.save_data()
                    self.gui.update_display()
                    self.tray_icon_manager.update_tooltip()
                    
                    log_info(f"Quick add expense: ${sanitized['amount']:.2f} - {sanitized['description']}")
                    self._quick_add_dialog_open = False
                    dialog.destroy()
                    
                except Exception as e:
                    log_error("Error in quick add", e)
                    dialog._showing_messagebox = True
                    messagebox.showerror("Error", f"Failed to add expense: {e}", parent=dialog)
                    dialog._showing_messagebox = False
                    dialog.focus_force()
                    amount_entry.focus_set()
            
            def on_cancel():
                """Handle cancel button click and cleanup"""
                self._quick_add_dialog_open = False
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
                # Check if dropdown is visible - if so, let widget handle it
                # Widget's handler will apply suggestion and return "break"
                if desc_entry.dropdown_visible:
                    # Let widget handle it (will run after this handler)
                    # Widget returns "break" which prevents form submission
                    return None  # Let widget's handler run
                # Dropdown not visible - submit form
                on_add()
                return "break"
            
            amount_entry.bind('<Return>', handle_amount_enter)
            # CRITICAL: Use add='+' to preserve widget's handler
            # Handlers run in reverse order, so this runs first, then widget's handler
            # If dropdown visible, widget returns "break" preventing this handler's form submission
            desc_entry.entry.bind('<Return>', handle_description_enter, add='+')
            dialog.bind('<Escape>', lambda e: on_cancel())
            
            # Show the dialog now that it's fully configured and positioned
            log_info("[DIALOG] Calling deiconify() to show dialog")
            dialog.deiconify()
            log_info("[DIALOG] Dialog is now visible")
            
            # Set window attributes after showing
            if self.window_manager.is_hidden:
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
            
            # Auto-close when focus leaves dialog (simplified approach)
            # Bind only to dialog window, not all child widgets
            def on_focus_loss(event):
                # Small delay to allow focus to settle (e.g., clicking between widgets)
                self.root.after(config.Threading.FOCUS_CHECK_DELAY_MS, lambda: check_if_should_close())
            
            def check_if_should_close():
                if not dialog.winfo_exists():
                    return
                # Tkinter workaround: Track messagebox state to prevent recursive calls.
                # Tkinter doesn't provide native state tracking for messageboxes, and
                # showing a messagebox while another is open can cause UI freezes or
                # unexpected behavior. This custom flag is the standard workaround.
                if getattr(dialog, '_showing_messagebox', False):
                    return
                focused = dialog.focus_get()
                # Close if no widget has focus or focus moved outside dialog
                if focused is None or focused.winfo_toplevel() != dialog:
                    self._quick_add_dialog_open = False
                    dialog.destroy()
            
            # Bind to dialog window only (not children)
            dialog.bind('<FocusOut>', on_focus_loss)
            
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
    def close_all_dialogs(self):
        """Close all open dialogs to prevent focus issues when hiding window"""
        try:
            log_debug(f"Closing {len(self.open_dialogs)} open dialogs...")
            for dialog in self.open_dialogs[:]:  # Use slice to avoid modification during iteration
                try:
                    if hasattr(dialog, 'dialog') and dialog.dialog.winfo_exists():
                        dialog.dialog.destroy()
                        log_debug("Dialog destroyed successfully")
                except (tk.TclError, AttributeError) as e:
                    # Dialog already destroyed or widget doesn't exist
                    # This is normal during shutdown or if dialog was already closed
                    log_debug(f"Dialog already destroyed: {e}")
                except Exception as e:
                    # Unexpected error destroying dialog
                    log_error(f"Error destroying dialog: {e}")
            self.open_dialogs.clear()
            log_debug("All dialogs closed")
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
            # Use the new export system with dialog and status bar callback
            # Note: status_manager is guaranteed to exist after GUI initialization
            status_callback = self.gui.status_manager.show
            export_expenses(self.expenses, self.current_month, status_callback)
        except Exception as e:
            log_error("Error opening export dialog", e)
            messagebox.showerror("Export Error", f"Failed to open export dialog: {e}")
    
    def import_expenses_dialog(self):
        """Show file picker and import expense data from JSON backup"""
        try:
            # Use the import system with status bar callback
            # Note: status_manager is guaranteed to exist after GUI initialization
            status_callback = self.gui.status_manager.show
            import_expense_backup(self, status_callback=status_callback)
        except Exception as e:
            log_error("Error importing backup", e)
            messagebox.showerror("Import Error", f"Failed to import backup: {e}")
            
    def _process_gui_queue(self):
        """
        Process all pending GUI operations from the queue.
        
        This enables thread-safe GUI operations from background threads like the tray icon.
        All GUI operations posted to self.gui_queue will be executed in the main thread.
        """
        try:
            # Process all pending items (non-blocking)
            while True:
                try:
                    # Get item from queue (don't block)
                    callback = self.gui_queue.get_nowait()
                    
                    # Execute the callback in the main thread
                    callback()
                    
                    # Mark task as done
                    self.gui_queue.task_done()
                    
                except queue.Empty:
                    # No more items in queue
                    break
                    
        except Exception as e:
            log_error(f"Error processing GUI queue: {e}")
        
        # Schedule next queue check (if application is still running)
        try:
            # Defensive check: root may not exist during shutdown or if initialization failed.
            # winfo_exists() checks if Tkinter widget is still valid (not destroyed).
            # Both checks are necessary because shutdown can occur in any order.
            if hasattr(self, 'root') and self.root.winfo_exists():
                self.root.after(config.Threading.GUI_QUEUE_POLL_MS, self._process_gui_queue)
        except (tk.TclError, AttributeError) as e:
            # Expected during shutdown: Tkinter widgets destroyed, root window closed.
            # TclError: Tkinter already destroyed
            # AttributeError: root object deleted
            log_debug(f"GUI queue stopped (shutdown): {e}")
        except RuntimeError as e:
            # Tkinter main loop ended
            log_debug(f"GUI queue stopped (main loop ended): {e}")
        except Exception as e:
            # Unexpected error - log for debugging
            log_warning(f"Unexpected error in GUI queue: {e}")
        
    def run(self):
        """Run the application"""
        # Start main GUI
        # Note: Protocol handler is already set up in __init__ to quit_app
        
        # Start GUI queue processor for thread-safe operations
        self._process_gui_queue()
        
        try:
            self.root.mainloop()
        except KeyboardInterrupt:
            self.shutdown()
    
            
    def shutdown(self):
        """
        Shutdown the application.
        
        Alias for quit_app() for backwards compatibility with KeyboardInterrupt handler.
        """
        self.quit_app()

if __name__ == "__main__":
    app = ExpenseTracker()
    app.run()
