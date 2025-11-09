import tkinter as tk
from tkinter import ttk
import customtkinter as ctk
from datetime import datetime, timedelta
import calendar
import webbrowser
import config
from dialog_helpers import DialogHelper
from analytics import ExpenseAnalytics
from widgets import CollapsibleDateCombobox, NumberPadWidget
from status_bar_manager import StatusBarManager
from page_manager import PageManager
from quick_add_helper import QuickAddHelper
from archive_mode_manager import ArchiveModeManager
from tooltip_manager import TooltipManager
from dashboard_page_builder import DashboardPageBuilder
from expense_list_page_builder import ExpenseListPageBuilder
from validation import InputValidation
from date_utils import DateUtils
from settings_manager import get_settings_manager


class LiteFinPadGUI:
    def __init__(self, root, expense_tracker):
        self.root = root
        self.expense_tracker = expense_tracker
        self.setup_window()
        self.setup_styles()
        
        # Initialize managers
        self.status_manager = StatusBarManager(self.root)
        self.page_manager = PageManager()
        self.tooltip_manager = TooltipManager()
        
        self.create_widgets()
        
    def setup_window(self):
        """Configure the main window with proper sizing and anti-flicker optimizations"""
        # Read version dynamically from version.txt
        try:
            with open('version.txt', 'r') as f:
                version = f.read().strip()
        except:
            version = "Unknown"  # Fallback if version.txt is missing
        
        self.root.title(f"LiteFinPad v{version} - Monthly Expense Tracker")
        self.root.geometry(f"{config.Window.WIDTH}x{config.Window.HEIGHT}")  # Increased height for inline Quick Add section
        self.root.resizable(False, False)
        self.root.configure(bg=config.Colors.BG_LIGHT_GRAY)
        
        # Anti-flicker optimizations
        self.root.update_idletasks()  # Force initial rendering
        self.root.update()  # Complete any pending updates
        
    def setup_styles(self):
        """Configure modern Windows 11 styling and CustomTkinter theme"""
        # Initialize CustomTkinter theme
        ctk.set_appearance_mode(config.CustomTkinterTheme.APPEARANCE_MODE)
        ctk.set_default_color_theme(config.CustomTkinterTheme.COLOR_THEME)
        
        # Keep ttk styles for widgets not yet migrated to CustomTkinter
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        # === NORMAL MODE STYLES ===
        # Frame backgrounds
        self.style.configure('TFrame', background=config.Colors.BG_LIGHT_GRAY)
        self.style.configure('TLabelframe', background=config.Colors.BG_LIGHT_GRAY)
        self.style.configure('TLabelframe.Label', background=config.Colors.BG_LIGHT_GRAY)
        
        # Default TLabel - must explicitly match frame background for labels without specific styles
        self.style.configure('TLabel', background=config.Colors.BG_LIGHT_GRAY)
        
        # Specific label styles (explicit background to match frames)
        self.style.configure('Title.TLabel', font=config.Fonts.TITLE, foreground=config.Colors.TEXT_BLACK, background=config.Colors.BG_LIGHT_GRAY)
        self.style.configure('Month.TLabel', font=config.Fonts.SUBTITLE, foreground=config.Colors.TEXT_BLACK, background=config.Colors.BG_LIGHT_GRAY)
        self.style.configure('Count.TLabel', font=config.get_font(config.Fonts.SIZE_LARGE), foreground=config.Colors.TEXT_BLACK, background=config.Colors.BG_LIGHT_GRAY)
        self.style.configure('Total.TLabel', font=config.Fonts.HERO_TOTAL, foreground=config.Colors.GREEN_PRIMARY, background=config.Colors.BG_LIGHT_GRAY)
        self.style.configure('Rate.TLabel', font=config.get_font(config.Fonts.SIZE_MEDIUM), foreground=config.Colors.TEXT_GRAY_DARK, background=config.Colors.BG_LIGHT_GRAY)
        self.style.configure('Analytics.TLabel', font=config.get_font(config.Fonts.SIZE_NORMAL), foreground=config.Colors.TEXT_GRAY_MEDIUM, background=config.Colors.BG_LIGHT_GRAY)
        self.style.configure('Trend.TLabel', font=config.get_font(config.Fonts.SIZE_NORMAL), foreground=config.Colors.PURPLE_PRIMARY, background=config.Colors.BG_LIGHT_GRAY)
        
        # === ARCHIVE MODE STYLES ===
        self.style.configure('Archive.TFrame', background=config.Colors.BG_ARCHIVE_TINT)
        self.style.configure('Archive.TLabelframe', background=config.Colors.BG_ARCHIVE_TINT)
        self.style.configure('Archive.TLabelframe.Label', background=config.Colors.BG_ARCHIVE_TINT)
        self.style.configure('Archive.TLabel', background=config.Colors.BG_ARCHIVE_TINT)
        
        # Archive label styles
        self.style.configure('Archive.Title.TLabel', font=config.Fonts.TITLE, foreground=config.Colors.TEXT_BLACK, background=config.Colors.BG_ARCHIVE_TINT)
        self.style.configure('Archive.Month.TLabel', font=config.Fonts.SUBTITLE, foreground=config.Colors.TEXT_BLACK, background=config.Colors.BG_ARCHIVE_TINT)
        self.style.configure('Archive.Count.TLabel', font=config.get_font(config.Fonts.SIZE_LARGE), foreground=config.Colors.TEXT_BLACK, background=config.Colors.BG_ARCHIVE_TINT)
        self.style.configure('Archive.Total.TLabel', font=config.Fonts.HERO_TOTAL, foreground=config.Colors.PURPLE_ARCHIVE, background=config.Colors.BG_ARCHIVE_TINT)
        self.style.configure('Archive.Rate.TLabel', font=config.get_font(config.Fonts.SIZE_MEDIUM), foreground=config.Colors.TEXT_GRAY_DARK, background=config.Colors.BG_ARCHIVE_TINT)
        self.style.configure('Archive.Analytics.TLabel', font=config.get_font(config.Fonts.SIZE_NORMAL), foreground=config.Colors.TEXT_GRAY_MEDIUM, background=config.Colors.BG_ARCHIVE_TINT)
        self.style.configure('Archive.Trend.TLabel', font=config.get_font(config.Fonts.SIZE_NORMAL), foreground=config.Colors.PURPLE_PRIMARY, background=config.Colors.BG_ARCHIVE_TINT)
        
        # Button styles
        self.style.configure('Modern.TButton', font=config.Fonts.BUTTON, anchor='center')
        
        # Configure Add Expense button style with green accent and proper centering
        self.style.configure('AddExpense.TButton', font=config.Fonts.BUTTON, 
                           background=config.Colors.GREEN_PRIMARY, foreground='#ffffff',
                           anchor='center')
        self.style.map('AddExpense.TButton',
                      background=[('active', config.Colors.GREEN_HOVER), ('pressed', config.Colors.GREEN_PRESSED), ('disabled', '#cccccc')],
                      foreground=[('active', '#ffffff'), ('pressed', '#ffffff'), ('disabled', '#666666')])
        
        # Configure toolbutton style for crisp emoji rendering
        self.style.configure('Toolbutton', font=config.get_font(config.Fonts.SIZE_MEDIUM))
        self.style.map('Toolbutton', 
                      background=[('active', config.Colors.BUTTON_ACTIVE_BG), ('pressed', config.Colors.BUTTON_PRESSED_BG)],
                      relief=[('pressed', 'sunken'), ('!pressed', 'flat')])
        
    def create_widgets(self):
        """Create all GUI widgets with proper layout"""
        # Main container frame - this will hold both pages (using CTkFrame for consistency)
        # Match window background color for seamless appearance
        self.main_container = ctk.CTkFrame(self.root, fg_color=config.Colors.BG_LIGHT_GRAY)
        self.main_container.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        self.main_container.columnconfigure(0, weight=1)
        self.main_container.rowconfigure(0, weight=1)
        
        # Create main dashboard page
        self.create_main_page()
        
        # Create expense list page
        self.create_expense_list_page()
        
        # Register pages with page manager
        self.page_manager.register_page(PageManager.PAGE_MAIN, self.main_frame)
        self.page_manager.register_page(PageManager.PAGE_EXPENSE_LIST, self.expense_list_frame)
        
        # Initialize archive mode manager IMMEDIATELY after widgets (before any display updates)
        # This ensures _is_archive_mode() and _get_context_date() always have a manager to delegate to
        self.archive_mode_manager = ArchiveModeManager(
            root=self.root,
            expense_tracker=self.expense_tracker,
            page_manager=self.page_manager,
            main_frame=self.main_frame,
            expense_list_frame=self.expense_list_frame,
            main_container=self.main_container,
            month_label=self.month_label,
            add_expense_btn=self.add_expense_btn,
            quick_add_helper=self.quick_add_helper,
            table_manager=self.table_manager,
            tooltip_creator=self.tooltip_manager.create,
            update_display_callback=self.update_display,
            update_metrics_callback=self.update_expense_metrics
        )
        
        # Create status bar (at bottom of window)
        status_bar_frame = self.status_manager.create_ui()
        # Grid it but hide initially (shown only on expense list page)
        status_bar_frame.grid(row=1, column=0, sticky=(tk.W, tk.E))
        self.status_manager.set_visible(False)
        
    def create_main_page(self):
        """Create the main dashboard page"""
        # Main frame with standard padding (status bar hidden on main page) - using CTkFrame
        # Match window background for seamless appearance
        self.main_frame = ctk.CTkFrame(self.main_container, fg_color=config.Colors.BG_LIGHT_GRAY)
        self.main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=15, pady=(8, 2))  # Further reduced top padding for maximum compactness
        
        # Configure grid weights
        self.main_frame.columnconfigure(0, weight=1)
        self.main_frame.columnconfigure(1, weight=1)
        self.main_frame.rowconfigure(9, weight=1)  # Allow Recent Expenses to expand (row 9 - frame is now at row 9)
        
        # Build dashboard using DashboardPageBuilder
        callbacks = {
            'show_month_navigation_menu': self.show_month_navigation_menu,
            'show_about_dialog': self.show_about_dialog,
            'show_budget_dialog': self.show_budget_dialog,
            'toggle_stay_on_top_visual': self.toggle_stay_on_top_visual,
            'get_context_date': self._get_context_date,
            'is_archive_mode': self._is_archive_mode
        }
        
        builder = DashboardPageBuilder(
            self.main_frame,
            self.expense_tracker,
            callbacks,
            self.tooltip_manager
        )
        
        # Build all sections and store widget references
        widgets = builder.build_all()
        
        # Store widget references as instance attributes for updates
        self.month_label = widgets['month_label']
        self.about_label = widgets['about_label']
        self.stay_on_top_var = widgets['stay_on_top_var']
        self.stay_on_top_label = widgets['stay_on_top_label']
        self.minimize_button = widgets['minimize_button']
        self.total_label = widgets['total_label']
        self.count_label = widgets['count_label']
        self.day_progress_label = widgets['day_progress_label']
        self.week_progress_label = widgets['week_progress_label']
        self.daily_avg_label = widgets['daily_avg_label']
        self.weekly_avg_label = widgets['weekly_avg_label']
        self.pace_label = widgets['pace_label']
        self.trend_label = widgets['trend_label']
        self.comparison_label = widgets['comparison_label']
        self.trend_context_label = widgets['trend_context_label']
        self.budget_amount_label = widgets['budget_amount_label']
        self.budget_status_label = widgets['budget_status_label']
        self.recent_expense_1 = widgets['recent_expense_1']
        self.recent_expense_2 = widgets['recent_expense_2']
        self.add_expense_btn = widgets['add_expense_btn']
        
        # Update recent expenses display
        self.update_recent_expenses()
        
    
    def toggle_stay_on_top_visual(self):
        """Toggle stay on top with visual feedback - SIMPLE version"""
        # Toggle the state
        current_state = self.stay_on_top_var.get()
        new_state = not current_state
        self.stay_on_top_var.set(new_state)
        
        # Get the header frame's background color for OFF state
        header_bg = self.style.lookup('TFrame', 'background')
        
        # Update label appearance - simple background color change
        if new_state:
            # ON - gray background (CTkLabel uses fg_color, not background)
            self.stay_on_top_label.configure(fg_color=config.Colors.BG_BUTTON_DISABLED)
            # Update tooltip
            self.tooltip_manager.update(self.stay_on_top_label, "Stay on Top (ON)")
        else:
            # OFF - match header background (transparent for CTkLabel)
            self.stay_on_top_label.configure(fg_color="transparent")
            # Update tooltip
            self.tooltip_manager.update(self.stay_on_top_label, "Stay on Top (OFF)")
        
        # Call the actual toggle function
        self.expense_tracker.window_manager.toggle_stay_on_top()
    
    # ==========================================
    # DIALOG & MENU METHODS
    # ==========================================
    
    def show_about_dialog(self):
        """Show About dialog with version and credits"""
        # Read version
        try:
            version = open('version.txt').read().strip()
        except:
            version = "Unknown"  # Fallback if version.txt is missing
        
        # Create dialog
        dialog = DialogHelper.create_dialog(
            self.root, "About LiteFinPad",
            config.Dialog.ABOUT_WIDTH, config.Dialog.ABOUT_HEIGHT
        )
        content = ctk.CTkFrame(dialog, fg_color="transparent")
        content.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Helper function for creating labels (using CTkLabel)
        def add_label(text, font, color, pady=(0, 10), **kwargs):
            label = ctk.CTkLabel(content, text=text, font=font, 
                            text_color=color, justify=tk.CENTER, **kwargs)
            label.pack(pady=pady)
            return label
        
        # App title and version
        add_label("LiteFinPad", config.Fonts.ABOUT_TITLE, 
                 config.Colors.BLUE_LINK, pady=(0, 5))
        add_label(f"Version {version}\nMonthly Expense Tracker", 
                 config.Fonts.LABEL_SMALL, config.Colors.TEXT_GRAY_MEDIUM, 
                 pady=(0, 15))
        
        # Separator (CTkFrame with border)
        separator = ctk.CTkFrame(content, height=1, fg_color=config.Colors.BG_DARK_GRAY)
        separator.pack(fill=tk.X, pady=(0, 15))
        
        # Credits, features, and license combined
        add_label("Built with AI assistance\n(Cursor + Claude Sonnet 4)\n\n"
                 "✓ 100% offline - no internet connection required\n"
                 "✓ Lightweight and fast\n"
                 "✓ Export to Excel and PDF\n\n"
                 "License: MIT", 
                 config.Fonts.LABEL_SMALL, config.Colors.TEXT_GRAY_DARK,
                 pady=(0, 15))
        
        # Clickable GitHub link (using CTkLabel with underline font)
        github = ctk.CTkLabel(
            content,
            text="GitHub",
            font=config.get_font(config.Fonts.SIZE_TINY, 'underline'),
            text_color=config.Colors.BLUE_LINK,
            cursor='hand2'
        )
        github.pack(pady=(0, 20))
        github.bind('<Button-1>', lambda e: webbrowser.open('https://github.com/aHuddini/LiteFinPad'))
        
        # Clickable Close link
        close = ctk.CTkLabel(
            content,
            text="Close",
            font=config.get_font(config.Fonts.SIZE_SMALL, 'underline'),
            text_color=config.Colors.BLUE_LINK,
            cursor='hand2'
        )
        close.pack()
        close.bind('<Button-1>', lambda e: dialog.destroy())
        
        # Finalize dialog
        DialogHelper.bind_escape_to_close(dialog)
        DialogHelper.center_on_parent(dialog, self.root, 
            config.Dialog.ABOUT_WIDTH,
                                      config.Dialog.ABOUT_HEIGHT)
        DialogHelper.show_dialog(dialog)
    
    def show_budget_dialog(self, event=None):
        """Show dialog to set monthly budget threshold"""
        # Get current budget value
        current_budget = get_settings_manager().get('Budget', 'monthly_threshold', 0.0, value_type=float)
        
        # Create dialog using DialogHelper (exactly like ExpenseAddDialog)
        dialog = DialogHelper.create_dialog(
            self.root,
            "Monthly Budget",
            config.Dialog.BUDGET_WIDTH,
            config.Dialog.BUDGET_HEIGHT
        )
        
        # Set dialog background to match app theme (light gray)
        dialog.configure(bg=config.Colors.BG_LIGHT_GRAY)
        
        # Setup dialog content (using CTkFrame) - using grid() geometry manager (CustomTkinter recommended)
        # Note: CTkFrame doesn't support 'padding' parameter
        # External padding: padx/pady in geometry manager
        # Internal padding: CustomTkinter doesn't support ipadx/ipady like standard Tkinter
        # Internal spacing is controlled via widget width/height parameters
        main_frame = ctk.CTkFrame(dialog, fg_color=config.Colors.BG_LIGHT_GRAY, corner_radius=0)
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=15, pady=8)  # Standard padding - bottom padding on buttons_frame handles spacing
        
        # Configure grid for responsive layout
        dialog.columnconfigure(0, weight=1)
        dialog.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)  # Center column expands
        
        # Row 0: Instruction label (centered)
        # Note: No explicit width/height - auto-sizes based on text content
        # External padding: pady in geometry manager
        instruction_label = ctk.CTkLabel(
            main_frame,
            text="Set monthly spending budget",
            font=config.get_font(config.Fonts.SIZE_NORMAL, 'bold'),
            text_color=config.Colors.TEXT_BLACK,
            anchor="center"
        )
        instruction_label.grid(row=0, column=0, pady=(0, 5), sticky="")  # Centered (no sticky)
        
        # Row 1: Current budget display (centered)
        # Note: No explicit width/height - auto-sizes based on text content (may be multi-line)
        current_budget_text = f"Current Threshold: ${current_budget:.2f}" if current_budget > 0 else "Current Threshold: Not Set"
        if current_budget == 0:
            current_budget_text += "\n(Click Here)"
        
        current_budget_label = ctk.CTkLabel(
            main_frame,
            text=current_budget_text,
            font=config.get_font(config.Fonts.SIZE_SMALL, 'underline'),
            text_color=config.Colors.BLUE_DARK_NAVY,
            anchor="center"
        )
        current_budget_label.grid(row=1, column=0, pady=(0, 8), sticky="")  # Centered (no sticky)
        
        # Row 2: Amount entry with $ prefix (centered)
        entry_frame = ctk.CTkFrame(main_frame, fg_color="transparent", corner_radius=0)
        entry_frame.grid(row=2, column=0, pady=(0, 0), sticky="")  # Centered container
        
        # Dollar sign prefix label (inside entry_frame)
        dollar_label = ctk.CTkLabel(
            entry_frame, 
            text="$", 
            font=config.get_font(config.Fonts.SIZE_NORMAL, 'bold')
        )
        dollar_label.grid(row=0, column=0, padx=(0, 5), sticky="w")  # Left-aligned in frame
        
        budget_var = tk.StringVar(value="")  # Start BLANK
        # Budget entry field - EXPLICIT size parameters for compact layout
        # Internal padding: Controlled via width/height (affects space around text)
        budget_entry = ctk.CTkEntry(
            entry_frame,
            textvariable=budget_var,
            font=config.get_font(config.Fonts.SIZE_NORMAL),
            width=150,  # Explicit width in pixels (affects internal spacing)
            height=25   # Explicit height in pixels - compact entry field (affects internal spacing)
        )
        budget_entry.grid(row=0, column=1, sticky="w")  # Left-aligned next to dollar sign
        
        # Validation
        validate_cmd = dialog.register(InputValidation.validate_amount)
        budget_entry.configure(validate='key', validatecommand=(validate_cmd, '%P'))
        
        # Row 3: Error label (centered)
        # Using CTkLabel with EXPLICIT height control to minimize space when empty
        # Note: height=0 when empty, height=None when text present (auto-size)
        error_label = ctk.CTkLabel(
            main_frame,
            text="",
            font=config.get_font(config.Fonts.SIZE_SMALL),
            text_color=config.Colors.RED_PRIMARY,
            height=0,  # Explicit height in pixels when empty - collapses to minimal space
            anchor="center"
        )
        error_label.grid(row=3, column=0, pady=(5, 1), sticky="")  # Centered (no sticky)
        
        # Row 4: Number pad (fills width) - Custom styled for Budget Dialog
        number_pad = NumberPadWidget(main_frame, budget_var)
        number_pad.grid(row=4, column=0, pady=(0, 0), sticky=(tk.W, tk.E))  # Fills width
        
        # Customize numpad button colors - Neumorphic-inspired style
        # Inspired by modern dial pad designs with soft, raised button appearance
        style = ttk.Style()
        
        # Neumorphic Dark Blue Theme (inspired by reference image)
        # Deep blue buttons with light blue text for high contrast
        style.configure("BudgetNumPad.TButton",
                       font=(config.Fonts.FAMILY, config.NumberPad.FONT_SIZE, config.NumberPad.FONT_WEIGHT),
                       padding=config.NumberPad.PADDING,
                       background='#1E3A8A',  # Deep dark blue (similar to BLUE_DARK_NAVY but darker)
                       foreground='#7DD3FC',  # Light cyan/blue for text (high contrast)
                       borderwidth=2,
                       relief='raised')  # Raised relief for 3D effect
        
        # Configure hover/pressed states with lighter blue shades
        style.map("BudgetNumPad.TButton",
                 background=[('active', '#3B5FA0'),  # Lighter blue on hover (raised effect)
                           ('pressed', '#2A4A90')],  # Slightly lighter when pressed (indented effect)
                 foreground=[('active', '#A5E8FF'),  # Brighter cyan text on hover
                            ('pressed', '#B5F0FF')])  # Even brighter on press
        
        # Apply the custom style to all numpad buttons
        for widget in number_pad.winfo_children():
            if isinstance(widget, ttk.Button):
                widget.configure(style="BudgetNumPad.TButton")
        
        # Row 5: Buttons frame (centered, contains two buttons side-by-side)
        # Note: Using pack() inside buttons_frame to match original compact layout
        # Bottom padding creates space below buttons to prevent cutoff by dialog window
        buttons_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        buttons_frame.grid(row=5, column=0, pady=(10, 10), sticky="")  # Standard padding - dialog height provides clearance
        
        def save_budget():
            """Save budget - exactly like ExpenseAddDialog.add_expense()"""
            try:
                from error_logger import log_info
                log_info("Budget save requested")
                
                budget_str = budget_var.get().strip()
                log_info(f"Budget string: {budget_str}")
                
                # Clear any previous error
                error_label.configure(text="", height=0)  # Collapse when empty (matches initialization)
                
                # Validate
                result = InputValidation.validate_final_amount(budget_str)
                if not result.is_valid:
                    error_label.configure(text=result.error_message, height=None)  # Auto height when text present
                    budget_entry.focus()
                    return
                
                budget_value = result.sanitized_value
                log_info(f"Saving budget value: {budget_value}")
                
                # Save to settings
                get_settings_manager().set('Budget', 'monthly_threshold', budget_value)
                log_info("Budget saved to settings")
                
                # Close dialog first (like ExpenseAddDialog)
                dialog.destroy()
                log_info("Dialog destroyed")
                
                # Update display after dialog is destroyed
                self._update_budget_display()
                log_info("Display updated")
                
            except Exception as e:
                from error_logger import log_error
                log_error("Error saving budget", e)
                error_label.configure(text="Failed to save budget", height=None)  # Auto height when text present
        
        def handle_enter(event):
            """Handle Enter key"""
            save_budget()
            return "break"
        
        # Set button - navy purple color
        # Original sizing and styling restored - no border effects
        set_button = ctk.CTkButton(
            buttons_frame,
            text="Set",
            command=save_budget,
            width=70,   # Button width in pixels (reduced for compactness)
            height=25,  # Button height in pixels (reduced for more compact appearance)
            border_spacing=2,  # Explicit spacing between text and button border (default is 2)
            corner_radius=config.CustomTkinterTheme.CORNER_RADIUS,
            font=config.get_font(config.Fonts.SIZE_SMALL, 'bold'),
            fg_color=config.Colors.PURPLE_ARCHIVE,  # Navy purple color
            hover_color=config.Colors.PURPLE_VIBRANT,  # Slightly darker on hover
            text_color="white"
        )
        set_button.pack(side=tk.LEFT, padx=(0, 10))  # Use pack() for original compact side-by-side layout
        
        # Cancel button - dark gray (same sizing as Set button)
        cancel_button = ctk.CTkButton(
            buttons_frame,
            text="Cancel",
            command=dialog.destroy,
            width=70,   # Button width in pixels (same as Set button)
            height=25,  # Button height in pixels (same as Set button)
            border_spacing=2,  # Explicit spacing between text and button border (default is 2)
            corner_radius=config.CustomTkinterTheme.CORNER_RADIUS,
            font=config.get_font(config.Fonts.SIZE_SMALL, 'bold'),
            fg_color=config.Colors.BG_DARK_GRAY,
            hover_color=config.Colors.TEXT_GRAY_MEDIUM,
            text_color="white"
        )
        cancel_button.pack(side=tk.LEFT)  # Use pack() for original compact side-by-side layout
        
        # Center dialog
        DialogHelper.center_on_parent(
            dialog,
            self.root,
            config.Dialog.BUDGET_WIDTH,
            config.Dialog.BUDGET_HEIGHT
        )
        
        # Show dialog
        DialogHelper.show_dialog(dialog)
        
        # Focus and bind keys
        dialog.after(100, lambda: budget_entry.focus_set())
        dialog.bind('<Return>', handle_enter)
        budget_entry.bind('<Return>', handle_enter)
        DialogHelper.bind_escape_to_close(dialog)
    
    def _update_budget_display(self):
        """Update budget display labels after budget change"""
        try:
            # Re-read budget and recalculate using past expenses only (same as update_display)
            from datetime import datetime
            from data_manager import ExpenseDataManager
            budget_threshold = get_settings_manager().get('Budget', 'monthly_threshold', 0.0, value_type=float)
            
            # Calculate monthly total excluding future expenses (same logic as update_display)
            # Calculate monthly total (same logic as update_display)
            if self._is_archive_mode():
                # Archive mode: show all expenses for the viewed month
                expenses_for_budget = self.expense_tracker.expenses
            else:
                # Current mode: exclude future expenses
                today = datetime.now().date()
                expenses_for_budget = [e for e in self.expense_tracker.expenses 
                                      if (dt := DateUtils.parse_date(e['date'])) and dt.date() <= today]
            monthly_total_for_budget = ExpenseDataManager.calculate_monthly_total(expenses_for_budget)
            
            if budget_threshold > 0:
                difference = budget_threshold - monthly_total_for_budget  # Use calculated monthly total
                
                if difference > 0:
                    # Under budget (good)
                    budget_amount_text = f"+${difference:,.2f}"
                    budget_status_text = "(Under)"
                    budget_color = config.Colors.GREEN_PRIMARY
                else:
                    # Over budget (warning)
                    budget_amount_text = f"-${abs(difference):,.2f}"
                    budget_status_text = "(Over)"
                    budget_color = config.Colors.RED_PRIMARY
            else:
                # Not set
                budget_amount_text = "Not set"
                budget_status_text = "(Click Here)"
                budget_color = config.Colors.TEXT_GRAY_MEDIUM
            
            # Update labels if they exist and are valid widgets (ttk.Label uses foreground, not text_color)
            if hasattr(self, 'budget_amount_label') and self.budget_amount_label:
                try:
                    self.budget_amount_label.configure(
                        text=budget_amount_text,
                        foreground=budget_color  # ttk.Label uses foreground
                    )
                except (tk.TclError, AttributeError):
                    pass
            
            if hasattr(self, 'budget_status_label') and self.budget_status_label:
                try:
                    self.budget_status_label.configure(
                        text=budget_status_text,
                        foreground=budget_color  # ttk.Label uses foreground
                    )
                    # Always show the status label (it handles "Not set" and "(Click Here)" cases)
                    if not self.budget_status_label.winfo_ismapped():
                        self.budget_status_label.pack()
                except (tk.TclError, AttributeError):
                    pass
        except Exception as e:
            from error_logger import log_error
            log_error("Error in _update_budget_display", e)
    
    def show_month_navigation_menu(self, event):
        """Show hierarchical month navigation menu (Year > Months)"""
        # Create navigation menu using month viewer
        menu = self.expense_tracker.month_viewer.create_navigation_menu(
            self.root,
            on_select_callback=self.on_month_selected
        )
        
        # Show menu at mouse position
        try:
            menu.tk_popup(event.x_root, event.y_root)
        finally:
            menu.grab_release()
    
    def on_month_selected(self, month_key: str):
        """
        Callback when a month is selected from the dropdown
        
        Args:
            month_key: Selected month in YYYY-MM format
        """
        # Switch to the selected month
        self.expense_tracker.switch_month(month_key)
    
    # ==========================================
    # HELPER METHODS (Internal Utilities)
    # ==========================================
    
    def _is_archive_mode(self):
        """
        Helper method that delegates to archive_mode_manager if available.
        During initialization, provides direct fallback logic.
        """
        if hasattr(self, 'archive_mode_manager') and self.archive_mode_manager:
            return self.archive_mode_manager.is_archive_mode()
        else:
            # Fallback during initialization before archive_mode_manager exists
            viewed_month = getattr(self.expense_tracker, 'viewed_month', None)
            if viewed_month is None:
                return False
            current_month_key = datetime.now().strftime('%Y-%m')
            return viewed_month != current_month_key
    
    def _get_context_date(self):
        """
        Helper method that delegates to archive_mode_manager if available.
        During initialization, provides direct fallback logic.
        """
        if hasattr(self, 'archive_mode_manager') and self.archive_mode_manager:
            return self.archive_mode_manager.get_context_date()
        else:
            # Fallback during initialization before archive_mode_manager exists
            if self._is_archive_mode():
                viewed_month = self.expense_tracker.viewed_month
                year, month = map(int, viewed_month.split('-'))
                last_day = calendar.monthrange(year, month)[1]
                return datetime(year, month, last_day)
            else:
                return datetime.now()
    
    # ==========================================
    # DASHBOARD UPDATE METHODS
    # ==========================================
        
    def update_display(self):
        """Update all display elements"""
        from datetime import datetime
        from data_manager import ExpenseDataManager
        from error_logger import log_info
        
        # In archive mode, show ALL expenses for that month
        # In current mode, exclude future expenses
        if self._is_archive_mode():
            # Archive mode: show all expenses for the viewed month
            expenses_to_use = self.expense_tracker.expenses
            monthly_total = ExpenseDataManager.calculate_monthly_total(expenses_to_use)
            expense_count = len(expenses_to_use)
            log_info(f"[UPDATE_DISPLAY] Archive mode: {expense_count} expenses, total=${monthly_total:.2f}")
        else:
            # Current mode: exclude future expenses
            today = datetime.now().date()
            past_expenses = [e for e in self.expense_tracker.expenses 
                            if (dt := DateUtils.parse_date(e['date'])) and dt.date() <= today]
            monthly_total = ExpenseDataManager.calculate_monthly_total(past_expenses)
            expense_count = len(past_expenses)
            log_info(f"[UPDATE_DISPLAY] Current mode: {expense_count} expenses, total=${monthly_total:.2f}")
        
        # Update total - ensure label exists and is a CTkLabel
        if hasattr(self, 'total_label') and self.total_label:
            try:
                self.total_label.configure(text=f"${monthly_total:.2f}")
                log_info(f"[UPDATE_DISPLAY] Updated total_label to ${monthly_total:.2f}")
            except Exception as e:
                log_info(f"[UPDATE_DISPLAY] Error updating total_label: {e}")
        else:
            log_info(f"[UPDATE_DISPLAY] total_label not found or None")
        
        # Update count - ensure label exists and is a CTkLabel
        if hasattr(self, 'count_label') and self.count_label:
            try:
                self.count_label.configure(text=f"{expense_count} expenses this month")
                log_info(f"[UPDATE_DISPLAY] Updated count_label to {expense_count} expenses")
            except Exception as e:
                log_info(f"[UPDATE_DISPLAY] Error updating count_label: {e}")
        else:
            log_info(f"[UPDATE_DISPLAY] count_label not found or None")
        
        # Get context date for analytics
        context_date = self._get_context_date()
        
        # Update day/week progress
        current_day, total_days = ExpenseAnalytics.calculate_day_progress(context_date)
        current_week, total_weeks = ExpenseAnalytics.calculate_week_progress(context_date)
        if hasattr(self, 'day_progress_label') and self.day_progress_label:
            try:
                self.day_progress_label.configure(text=f"{current_day} / {total_days}")
            except Exception as e:
                log_info(f"[UPDATE_DISPLAY] Error updating day_progress_label: {e}")
        
        # For archive mode, show clean week numbers (no decimals for completed months)
        if self._is_archive_mode():
            # Round to nearest integer for past months (looks cleaner)
            week_display = f"{round(current_week)} / {total_weeks}"
        else:
            # Current month: show decimal precision for progress within week
            week_display = f"{current_week:.1f} / {total_weeks}"
        if hasattr(self, 'week_progress_label') and self.week_progress_label:
            try:
                self.week_progress_label.configure(text=week_display)
            except Exception as e:
                log_info(f"[UPDATE_DISPLAY] Error updating week_progress_label: {e}")
        
        # Update progress (averages in progress section)
        # Use the correct expenses list based on mode
        expenses_for_analytics = expenses_to_use if self._is_archive_mode() else self.expense_tracker.expenses
        daily_avg, days_elapsed = ExpenseAnalytics.calculate_daily_average(
            expenses_for_analytics, context_date
        )
        weekly_avg, weeks_elapsed = ExpenseAnalytics.calculate_weekly_average(
            expenses_for_analytics, context_date
        )
        
        self.daily_avg_label.configure(text=f"${daily_avg:.2f} /day")
        self.weekly_avg_label.configure(text=f"${weekly_avg:.2f} /week")
        
        # Update analytics (weekly pace and previous month) with archive context
        context_date = self._get_context_date()
        # Use the correct expenses list based on mode
        expenses_for_pace = expenses_to_use if self._is_archive_mode() else self.expense_tracker.expenses
        weekly_pace, pace_days = ExpenseAnalytics.calculate_weekly_pace(
            expenses_for_pace, context_date
        )
        
        # Calculate previous month data with comparison
        # Pass viewed_month only if truly in archive mode (not current month)
        viewed_month = self.expense_tracker.viewed_month if self._is_archive_mode() else None
        prev_month_date = datetime.now().replace(day=1) - timedelta(days=1)
        prev_month_key = prev_month_date.strftime('%Y-%m')
        prev_data_folder = f"data_{prev_month_key}"
        # Use calculated monthly total for comparison
        trend_text, trend_context, comparison = ExpenseAnalytics.calculate_monthly_trend(
            prev_data_folder,
            monthly_total,  # Use calculated monthly total (already filtered for archive/current mode)
            viewed_month
        )
        
        if hasattr(self, 'pace_label') and self.pace_label:
            try:
                self.pace_label.configure(text=f"${weekly_pace:.2f} /day")
            except Exception as e:
                log_info(f"[UPDATE_DISPLAY] Error updating pace_label: {e}")
        if hasattr(self, 'trend_label') and self.trend_label:
            try:
                self.trend_label.configure(text=f"{trend_text} ")
            except Exception as e:
                log_info(f"[UPDATE_DISPLAY] Error updating trend_label: {e}")
        if hasattr(self, 'trend_context_label') and self.trend_context_label:
            try:
                self.trend_context_label.configure(text=trend_context)  # Update month name
            except Exception as e:
                log_info(f"[UPDATE_DISPLAY] Error updating trend_context_label: {e}")
        
        # Update comparison indicator (comparison_label is ttk.Label, use foreground)
        if hasattr(self, 'comparison_label') and comparison:
            indicator_text = f"{comparison['symbol']} "
            if comparison['direction'] == 'similar':
                indicator_text += f"+{comparison['percentage']:.1f}%"
            else:
                sign = "+" if comparison['direction'] == 'increase' else "-"
                indicator_text += f"{sign}{comparison['percentage']:.0f}%"
            
            self.comparison_label.configure(
                text=indicator_text,
                foreground=comparison['color']  # ttk.Label uses foreground, not text_color
            )
        elif hasattr(self, 'comparison_label'):
            # Clear indicator if no comparison available
            self.comparison_label.configure(text="")
        
        # Update budget comparison (budget display updates based on monthly_total_past)
        if hasattr(self, 'budget_amount_label') and self.budget_amount_label:
            from settings_manager import get_settings_manager
            try:
                budget_threshold = get_settings_manager().get('Budget', 'monthly_threshold', 0.0)
                try:
                    budget_threshold = float(budget_threshold) if budget_threshold else 0.0
                except (ValueError, TypeError):
                    budget_threshold = 0.0
                
                if budget_threshold > 0:
                    difference = budget_threshold - monthly_total  # Use calculated monthly total
                    if difference > 0:
                        budget_amount_text = f"+${difference:,.2f}"
                        budget_status_text = "(Under)"
                        budget_color = config.Colors.GREEN_PRIMARY
                    else:
                        budget_amount_text = f"-${abs(difference):,.2f}"
                        budget_status_text = "(Over)"
                        budget_color = config.Colors.RED_PRIMARY
                else:
                    budget_amount_text = "Not set"
                    budget_status_text = "(Click Here)"
                    budget_color = config.Colors.TEXT_GRAY_MEDIUM

                # Budget labels are ttk.Label widgets, use foreground
                self.budget_amount_label.configure(text=budget_amount_text, foreground=budget_color)
                if hasattr(self, 'budget_status_label') and self.budget_status_label:
                    self.budget_status_label.configure(text=budget_status_text, foreground=budget_color)
            except Exception as e:
                from error_logger import log_error
                log_error(f"Error updating budget display", e)
        
        # Update recent expenses
        self.update_recent_expenses()
    
    def update_recent_expenses(self):
        """Update the recent expenses display (excluding future expenses)"""
        from datetime import datetime
        
        # Filter out future expenses and get last 2 (not 3)
        today = datetime.now().date()
        past_expenses = [e for e in self.expense_tracker.expenses 
                        if (dt := DateUtils.parse_date(e['date'])) and dt.date() <= today]
        recent_expenses = past_expenses[-2:] if past_expenses else []
        
        expense_labels = [self.recent_expense_1, self.recent_expense_2]
        
        for i, expense in enumerate(recent_expenses):
            if i < len(expense_labels):
                # Format date as MM/DD/YY
                date_obj = DateUtils.parse_date(expense['date'])
                formatted_date = date_obj.strftime("%m/%d/%y") if date_obj else expense['date']
                
                # Format: • Date - Amount - Description
                expense_text = f"• {formatted_date} - ${expense['amount']:.2f} - {expense['description']}"
                expense_labels[i].configure(text=expense_text)
        
        # Clear remaining labels
        for i in range(len(recent_expenses), len(expense_labels)):
            expense_labels[i].configure(text="")
        
    def create_expense_list_page(self):
        """Create the expense list page using ExpenseListPageBuilder"""
        # Create builder with all necessary callbacks
        builder = ExpenseListPageBuilder(
            parent_frame=self.main_container,
            expense_tracker=self.expense_tracker,
            callbacks={
                'show_main_page': self.show_main_page,
                'export_dialog': self.expense_tracker.export_expenses_dialog,
                'import_dialog': self.expense_tracker.import_expenses_dialog,
                'on_expense_change': None,  # Builder creates this internally
                'update_display': self.update_display,
                'update_expense_metrics': self.update_expense_metrics,
                'status_manager': self.status_manager,
                'page_manager': self.page_manager,
                'gui_instance': self
            }
        )
        
        # Build the page and get widget references
        widgets = builder.build_all()
        
        # Store references needed for updates
        self.expense_list_frame = widgets['expense_list_frame']
        self.table_manager = widgets['table_manager']
        self._expense_count_tracker = widgets['count_tracker']
        self.quick_add_helper = widgets['quick_add_helper']
        
        # Store metric label references for update_expense_metrics()
        for label_name, label_widget in widgets['metric_labels'].items():
            setattr(self, label_name, label_widget)
    
    # ==========================================
    # EXPENSE LIST UPDATE METHODS
    # ==========================================
        
    def update_expense_metrics(self):
        """Update the expense metrics on the expense list page"""
        from datetime import datetime
        from data_manager import ExpenseDataManager
        
        # Filter out future expenses for calculations
        today = datetime.now().date()
        past_expenses = [e for e in self.expense_tracker.expenses 
                        if (dt := DateUtils.parse_date(e['date'])) and dt.date() <= today]
        
        # Calculate metrics using only past expenses
        median_expense, expense_count = ExpenseAnalytics.calculate_median_expense(
            past_expenses  # Use past expenses only
        )
        largest_expense, largest_desc = ExpenseAnalytics.calculate_largest_expense(
            past_expenses  # Use past expenses only
        )
        
        # Calculate total excluding future expenses
        total_amount = ExpenseDataManager.calculate_monthly_total(self.expense_tracker.expenses)
        
        self.list_median_label.configure(text=f"${median_expense:.2f}")
        self.median_count_label.configure(text=f"(median of {expense_count} expense{'s' if expense_count != 1 else ''})")
        self.list_total_label.configure(text=f"${total_amount:.2f}")
        # Count only past expenses for display
        expense_count_total = len(past_expenses)
        self.total_count_label.configure(text=f"({expense_count_total} expense{'s' if expense_count_total != 1 else ''})")
        self.largest_label.configure(text=f"${largest_expense:.2f}")
        self.largest_desc_label.configure(text=f"({largest_desc})")
    
    # ==========================================
    # PAGE NAVIGATION METHODS
    # ==========================================
    
    def show_expense_list_page(self):
        """Show the expense list page"""
        self.page_manager.show_expense_list_page(
            status_manager=self.status_manager,
            table_manager=self.table_manager,
            expense_tracker=self.expense_tracker,
            update_metrics_callback=self.update_expense_metrics
        )
        
    def show_main_page(self):
        """Show the main dashboard page"""
        self.page_manager.show_main_page(status_manager=self.status_manager)
