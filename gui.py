import tkinter as tk
from tkinter import ttk
from datetime import datetime
import webbrowser
import config
from dialog_helpers import DialogHelper


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


class LiteFinPadGUI:
    def __init__(self, root, expense_tracker):
        self.root = root
        self.expense_tracker = expense_tracker
        self.current_page = "main"
        self.setup_window()
        self.setup_styles()
        self.create_widgets()
        
    def setup_window(self):
        """Configure the main window with proper sizing and anti-flicker optimizations"""
        # Read version dynamically from version.txt
        try:
            with open('version.txt', 'r') as f:
                version = f.read().strip()
        except:
            version = "3.4"  # Fallback version
        
        self.root.title(f"LiteFinPad v{version} - Monthly Expense Tracker")
        self.root.geometry(f"{config.Window.WIDTH}x{config.Window.HEIGHT}")  # Increased height for inline Quick Add section
        self.root.resizable(False, False)
        self.root.configure(bg=config.Colors.BG_LIGHT_GRAY)
        
        # Anti-flicker optimizations
        self.root.update_idletasks()  # Force initial rendering
        self.root.update()  # Complete any pending updates
        
    def setup_styles(self):
        """Configure modern Windows 11 styling"""
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        # Configure custom styles for better legibility with increased font sizes
        self.style.configure('Title.TLabel', font=config.Fonts.TITLE, foreground=config.Colors.TEXT_BLACK)
        self.style.configure('Month.TLabel', font=config.Fonts.SUBTITLE, foreground=config.Colors.TEXT_BLACK)
        self.style.configure('Count.TLabel', font=config.get_font(config.Fonts.SIZE_LARGE), foreground=config.Colors.TEXT_BLACK)
        self.style.configure('Total.TLabel', font=config.Fonts.HERO_TOTAL, foreground=config.Colors.GREEN_PRIMARY)
        self.style.configure('Rate.TLabel', font=config.get_font(config.Fonts.SIZE_MEDIUM), foreground=config.Colors.TEXT_GRAY_DARK)
        self.style.configure('Analytics.TLabel', font=config.get_font(config.Fonts.SIZE_NORMAL), foreground=config.Colors.TEXT_GRAY_MEDIUM)
        self.style.configure('Trend.TLabel', font=config.get_font(config.Fonts.SIZE_NORMAL), foreground=config.Colors.PURPLE_PRIMARY)
        self.style.configure('Modern.TButton', font=config.Fonts.BUTTON,
                           anchor='center')
        
        # Configure Add Expense button style with green accent and proper centering
        self.style.configure('AddExpense.TButton', font=config.Fonts.BUTTON, 
                           background=config.Colors.GREEN_PRIMARY, foreground='#ffffff',
                           anchor='center')
        self.style.map('AddExpense.TButton',
                      background=[('active', config.Colors.GREEN_HOVER), ('pressed', config.Colors.GREEN_PRESSED)],
                      foreground=[('active', '#ffffff'), ('pressed', '#ffffff')])
        
        # Configure toolbutton style for crisp emoji rendering
        self.style.configure('Toolbutton', font=config.get_font(config.Fonts.SIZE_MEDIUM))
        self.style.map('Toolbutton', 
                      background=[('active', config.Colors.BUTTON_ACTIVE_BG), ('pressed', config.Colors.BUTTON_PRESSED_BG)],
                      relief=[('pressed', 'sunken'), ('!pressed', 'flat')])
        
    def create_widgets(self):
        """Create all GUI widgets with proper layout"""
        # Main container frame - this will hold both pages
        self.main_container = ttk.Frame(self.root)
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
        
    def create_main_page(self):
        """Create the main dashboard page"""
        # Main frame with reduced bottom padding to prevent button cropping
        self.main_frame = ttk.Frame(self.main_container, padding="15 15 15 2")
        self.main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.main_frame.columnconfigure(0, weight=1)
        self.main_frame.columnconfigure(1, weight=1)
        self.main_frame.rowconfigure(7, weight=1)  # Allow Recent Expenses to expand
        
        # Create header section
        self.create_header()
        
        # Create main content sections
        self.create_total_section()
        self.create_progress_section()
        self.create_analytics_section()
        self.create_buttons_section()
        self.create_expenses_section()
        
    def create_header(self):
        """Create header with perfectly centered title and controls"""
        # Header frame - full width
        header_frame = ttk.Frame(self.main_frame)
        header_frame.grid(row=0, column=0, columnspan=2, pady=(0, 15), sticky=(tk.W, tk.E))
        header_frame.columnconfigure(0, weight=1)  # Full width for centering
        
        # Month/Year title - perfectly centered
        month_text = datetime.now().strftime('%B %Y')
        self.month_label = ttk.Label(header_frame, text=month_text, style='Title.TLabel')
        self.month_label.grid(row=0, column=0, sticky=(tk.W, tk.E))
        
        # Control buttons frame - positioned absolutely on the right
        controls_frame = ttk.Frame(header_frame)
        controls_frame.place(relx=1.0, x=-15, y=5, anchor='ne')
        
        # About button (info icon) - leftmost
        self.about_label = ttk.Label(
            controls_frame,
            text="ℹ️",
            font=config.get_font(config.Fonts.SIZE_MEDIUM),
            cursor='hand2'
        )
        self.about_label.pack(side=tk.LEFT, padx=(0, 2))
        
        # Bind click event
        self.about_label.bind('<Button-1>', lambda e: self.show_about_dialog())
        
        # Add tooltip
        self.create_tooltip(self.about_label, "About LiteFinPad")
        
        # Stay on top control (default: enabled) - use a simple Label as a clickable icon
        self.stay_on_top_var = tk.BooleanVar(value=True)
        
        # Use a Label instead of Button - no hover effects, no button behavior
        self.stay_on_top_label = tk.Label(
            controls_frame,
            text="📌",
            font=config.get_font(config.Fonts.SIZE_MEDIUM),
            background=config.Colors.BG_BUTTON_DISABLED,  # Gray background when ON
            cursor='hand2',  # Hand cursor to show it's clickable
            padx=5,
            pady=2
        )
        self.stay_on_top_label.pack(side=tk.LEFT, padx=(0, 5))
        
        # Bind click event
        self.stay_on_top_label.bind('<Button-1>', lambda e: self.toggle_stay_on_top_visual())
        
        # Add tooltip
        self.create_tooltip(self.stay_on_top_label, "Stay on Top (ON)")
        
        # Minimize to tray button
        self.minimize_button = ttk.Button(
            controls_frame,
            text="➖",
            command=self.expense_tracker.hide_window,
            style='Toolbutton',
            width=3
        )
        self.minimize_button.pack(side=tk.LEFT)
        
        # Add tooltip
        self.create_tooltip(self.minimize_button, "Minimize to Tray")
        
    def create_total_section(self):
        """Create monthly total display section"""
        # Monthly total display
        self.total_label = ttk.Label(self.main_frame, text=f"${self.expense_tracker.monthly_total:.2f}", style='Total.TLabel')
        self.total_label.grid(row=1, column=0, columnspan=2, pady=(0, 5))
        
        # Sublabel: (Total Monthly)
        ttk.Label(self.main_frame, text="(Total Monthly)", font=config.Fonts.LABEL, foreground=config.Colors.TEXT_GRAY_MEDIUM).grid(row=2, column=0, columnspan=2, pady=(0, 10))
        
        # Expense count display (exclude future expenses)
        from datetime import datetime
        today = datetime.now().date()
        past_expenses = [e for e in self.expense_tracker.expenses 
                        if datetime.strptime(e['date'], '%Y-%m-%d').date() <= today]
        expense_count = len(past_expenses)
        self.count_label = ttk.Label(self.main_frame, text=f"{expense_count} expenses this month", style='Count.TLabel')
        self.count_label.grid(row=3, column=0, columnspan=2, pady=(0, 12))
        
    def create_progress_section(self):
        """Create current progress section with averages"""
        progress_frame = ttk.LabelFrame(self.main_frame, text="Current Progress", padding="10")
        progress_frame.grid(row=4, column=0, columnspan=2, pady=(0, 10), sticky=(tk.W, tk.E))
        
        # Get progress data
        current_day, total_days = self.expense_tracker.get_day_progress()
        current_week, total_weeks = self.expense_tracker.get_week_progress()
        daily_avg, days_elapsed = self.expense_tracker.get_daily_average()
        weekly_avg, weeks_elapsed = self.expense_tracker.get_weekly_average()
        
        # Top row: Day and Week progress (simplified, single line)
        top_row = ttk.Frame(progress_frame)
        top_row.pack(fill=tk.X, pady=(0, 8))
        
        # Day progress (left) - split label and value
        day_frame = ttk.Frame(top_row)
        day_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        day_container = ttk.Frame(day_frame)
        day_container.pack()
        ttk.Label(day_container, text="Day: ", font=config.get_font(config.Fonts.SIZE_NORMAL, 'bold'), foreground=config.Colors.BLUE_NAVY).pack(side=tk.LEFT)
        ttk.Label(day_container, text=f"{current_day} / {total_days}", style='Analytics.TLabel').pack(side=tk.LEFT)
        
        # Week progress (right) - split label and value
        week_frame = ttk.Frame(top_row)
        week_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(10, 0))
        
        week_container = ttk.Frame(week_frame)
        week_container.pack()
        ttk.Label(week_container, text="Week: ", font=config.get_font(config.Fonts.SIZE_NORMAL, 'bold'), foreground=config.Colors.BLUE_NAVY).pack(side=tk.LEFT)
        ttk.Label(week_container, text=f"{current_week:.1f} / {total_weeks}", style='Analytics.TLabel').pack(side=tk.LEFT)
        
        # Bottom row: Daily and Weekly averages
        bottom_row = ttk.Frame(progress_frame)
        bottom_row.pack(fill=tk.X, pady=(8, 0))
        
        # Daily average (left)
        daily_avg_frame = ttk.Frame(bottom_row)
        daily_avg_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        ttk.Label(daily_avg_frame, text="Daily Average", font=config.get_font(config.Fonts.SIZE_NORMAL, 'bold'), foreground=config.Colors.RED_PRIMARY).pack()
        self.daily_avg_label = ttk.Label(daily_avg_frame, text=f"${daily_avg:.2f} /day", style='Analytics.TLabel')
        self.daily_avg_label.pack()
        
        # Weekly average (right)
        weekly_avg_frame = ttk.Frame(bottom_row)
        weekly_avg_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(10, 0))
        
        ttk.Label(weekly_avg_frame, text="Weekly Average", font=config.get_font(config.Fonts.SIZE_NORMAL, 'bold'), foreground=config.Colors.GREEN_PRIMARY).pack()
        self.weekly_avg_label = ttk.Label(weekly_avg_frame, text=f"${weekly_avg:.2f} /week", style='Analytics.TLabel')
        self.weekly_avg_label.pack()
        
    def create_analytics_section(self):
        """Create spending analysis section"""
        analytics_frame = ttk.LabelFrame(self.main_frame, text="Spending Analysis", padding="10")
        analytics_frame.grid(row=5, column=0, columnspan=2, pady=(0, 10), sticky=(tk.W, tk.E))
        
        # Get analytics data
        weekly_pace, pace_days = self.expense_tracker.get_weekly_pace()
        prev_month_total, prev_month_name = self.expense_tracker.get_monthly_trend_analysis()
        
        # Side by side: Weekly Pace and Previous Month
        row = ttk.Frame(analytics_frame)
        row.pack(fill=tk.X)
        
        # Weekly pace (left)
        pace_frame = ttk.Frame(row)
        pace_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        ttk.Label(pace_frame, text="Weekly Pace", font=config.get_font(config.Fonts.SIZE_NORMAL, 'bold'), foreground=config.Colors.ORANGE_PRIMARY).pack()
        self.pace_label = ttk.Label(pace_frame, text=f"${weekly_pace:.2f} /day", style='Analytics.TLabel')
        self.pace_label.pack()
        ttk.Label(pace_frame, text=f"(this week: {pace_days} day{'s' if pace_days != 1 else ''})", font=config.Fonts.LABEL, foreground=config.Colors.TEXT_GRAY_MEDIUM).pack()
        
        # Previous month (right)
        prev_month_frame = ttk.Frame(row)
        prev_month_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(10, 0))
        
        ttk.Label(prev_month_frame, text="Previous Month", font=config.get_font(config.Fonts.SIZE_NORMAL, 'bold'), foreground=config.Colors.PURPLE_PRIMARY).pack()
        self.trend_label = ttk.Label(prev_month_frame, text=prev_month_total, style='Trend.TLabel')
        self.trend_label.pack()
        ttk.Label(prev_month_frame, text=prev_month_name, font=config.Fonts.LABEL, foreground=config.Colors.TEXT_GRAY_MEDIUM).pack()
        
    def create_buttons_section(self):
        """Create button section with proper spacing"""
        button_frame = ttk.Frame(self.main_frame)
        button_frame.grid(row=7, column=0, columnspan=2, pady=(0, 10), sticky=(tk.W, tk.E))
        
        # Add expense button (with green accent) - on left for easier access
        add_button = ttk.Button(button_frame, text="+ Add Expense", command=self.expense_tracker.add_expense, style='AddExpense.TButton')
        add_button.grid(row=0, column=0, padx=(0, 10), sticky=(tk.W, tk.E))
        
        # Navigation button to switch to Expense List page
        nav_button = ttk.Button(button_frame, text="📋 Expense List", command=self.expense_tracker.show_expense_list_page, style='Modern.TButton')
        nav_button.grid(row=0, column=1, padx=(10, 0), sticky=(tk.W, tk.E))
        
        # Configure button frame columns
        button_frame.columnconfigure(0, weight=1)
        button_frame.columnconfigure(1, weight=1)
        
    def create_expenses_section(self):
        """Create recent expenses section"""
        expenses_frame = ttk.LabelFrame(self.main_frame, text="Recent Expenses", padding="10")
        expenses_frame.grid(row=6, column=0, columnspan=2, pady=(0, 10), sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure minimum height for the frame
        expenses_frame.grid_propagate(False)
        expenses_frame.configure(height=90)  # Reduced height for 2 entries
        
        # Configure the expenses frame to expand
        expenses_frame.rowconfigure(0, weight=1)
        expenses_frame.columnconfigure(0, weight=1)
        
        # Container for expense labels with padding
        expenses_container = ttk.Frame(expenses_frame)
        expenses_container.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Create individual expense labels for better visibility (left-aligned, brown color)
        # Only showing 2 most recent expenses
        self.recent_expense_1 = ttk.Label(expenses_container, text="No recent expenses", 
                                        font=config.Fonts.LABEL, foreground=config.Colors.TEXT_BROWN, anchor='w')
        self.recent_expense_1.pack(pady=3, fill=tk.X)
        
        self.recent_expense_2 = ttk.Label(expenses_container, text="", 
                                        font=config.Fonts.LABEL, foreground=config.Colors.TEXT_BROWN, anchor='w')
        self.recent_expense_2.pack(pady=3, fill=tk.X)
        
        # Update recent expenses display
        self.update_recent_expenses()
        
    def update_recent_expenses(self):
        """Update the recent expenses display (excluding future expenses)"""
        from datetime import datetime
        
        # Filter out future expenses and get last 2 (not 3)
        today = datetime.now().date()
        past_expenses = [e for e in self.expense_tracker.expenses 
                        if datetime.strptime(e['date'], '%Y-%m-%d').date() <= today]
        recent_expenses = past_expenses[-2:] if past_expenses else []
        
        expense_labels = [self.recent_expense_1, self.recent_expense_2]
        
        for i, expense in enumerate(recent_expenses):
            if i < len(expense_labels):
                # Format date as MM/DD/YY
                date_obj = datetime.strptime(expense['date'], '%Y-%m-%d')
                formatted_date = date_obj.strftime("%m/%d/%y")
                
                # Format: • Date - Amount - Description
                expense_text = f"• {formatted_date} - ${expense['amount']:.2f} - {expense['description']}"
                expense_labels[i].config(text=expense_text)
        
        # Clear remaining labels
        for i in range(len(recent_expenses), len(expense_labels)):
            expense_labels[i].config(text="")
            
    def create_tooltip(self, widget, text):
        """Create a tooltip for a widget"""
        def on_enter(event):
            tooltip = tk.Toplevel()
            tooltip.wm_overrideredirect(True)
            tooltip.wm_attributes('-topmost', True)  # Ensure tooltip appears on top
            
            # Create label first to get its size
            label = tk.Label(tooltip, text=text, background="lightyellow", 
                           relief="solid", borderwidth=1, font=config.Fonts.LABEL_SMALL)
            label.pack()
            
            # Update to get actual size
            tooltip.update_idletasks()
            tooltip_width = tooltip.winfo_width()
            
            # Position tooltip to the LEFT of cursor to prevent off-screen overflow
            x_pos = event.x_root - tooltip_width - 10
            y_pos = event.y_root + 10
            
            tooltip.wm_geometry(f"+{x_pos}+{y_pos}")
            widget.tooltip = tooltip
            
        def on_leave(event):
            if hasattr(widget, 'tooltip'):
                widget.tooltip.destroy()
                del widget.tooltip
                
        widget.bind("<Enter>", on_enter)
        widget.bind("<Leave>", on_leave)
    
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
            # ON - gray background
            self.stay_on_top_label.config(background=config.Colors.BG_BUTTON_DISABLED)
            # Update tooltip
            if hasattr(self.stay_on_top_label, 'tooltip'):
                self.stay_on_top_label.tooltip.destroy()
                del self.stay_on_top_label.tooltip
            self.create_tooltip(self.stay_on_top_label, "Stay on Top (ON)")
        else:
            # OFF - match header background (no visible background)
            self.stay_on_top_label.config(background=header_bg)
            # Update tooltip
            if hasattr(self.stay_on_top_label, 'tooltip'):
                self.stay_on_top_label.tooltip.destroy()
                del self.stay_on_top_label.tooltip
            self.create_tooltip(self.stay_on_top_label, "Stay on Top (OFF)")
        
        # Call the actual toggle function
        self.expense_tracker.toggle_stay_on_top()
    
    def show_about_dialog(self):
        """Show About dialog with version and credits"""
        # Read version from version.txt
        try:
            with open('version.txt', 'r') as f:
                version = f.read().strip()
        except:
            version = "3.1"  # Fallback version
        
        # Create dialog using DialogHelper
        dialog = DialogHelper.create_dialog(
            self.root,
            "About LiteFinPad",
            config.Dialog.ABOUT_WIDTH,
            config.Dialog.ABOUT_HEIGHT
        )
        
        # Main content frame
        content_frame = DialogHelper.create_content_frame(dialog, padding="20")
        
        # App name and version
        app_name_label = ttk.Label(
            content_frame,
            text="LiteFinPad",
            font=config.Fonts.ABOUT_TITLE,
            foreground=config.Colors.BLUE_LINK
        )
        app_name_label.pack(pady=(0, 5))
        
        version_label = ttk.Label(
            content_frame,
            text=f"Version {version}",
            font=config.get_font(config.Fonts.SIZE_NORMAL),
            foreground=config.Colors.TEXT_GRAY_MEDIUM
        )
        version_label.pack(pady=(0, 15))
        
        # Tagline
        tagline_label = ttk.Label(
            content_frame,
            text="Monthly Expense Tracker",
            font=config.get_font(config.Fonts.SIZE_SMALL, 'italic'),
            foreground=config.Colors.TEXT_GRAY_DARK
        )
        tagline_label.pack(pady=(0, 20))
        
        # Separator
        separator1 = ttk.Separator(content_frame, orient='horizontal')
        separator1.pack(fill=tk.X, pady=(0, 15))
        
        # Credits
        credits_label = ttk.Label(
            content_frame,
            text="Built with AI assistance\n(Cursor + Claude Sonnet 4)",
            font=config.Fonts.LABEL_SMALL,
            foreground=config.Colors.TEXT_GRAY_DARK,
            justify=tk.CENTER
        )
        credits_label.pack(pady=(0, 15))
        
        # Features
        features_label = ttk.Label(
            content_frame,
            text="✓ 100% offline - no internet connection required\n✓ Lightweight and fast\n✓ Export to Excel and PDF",
            font=config.Fonts.LABEL_SMALL,
            foreground=config.Colors.TEXT_GRAY_DARK,
            justify=tk.CENTER
        )
        features_label.pack(pady=(0, 15))
        
        # Separator
        separator2 = ttk.Separator(content_frame, orient='horizontal')
        separator2.pack(fill=tk.X, pady=(0, 15))
        
        # License
        license_label = ttk.Label(
            content_frame,
            text="License: MIT",
            font=config.Fonts.LABEL_SMALL,
            foreground=config.Colors.TEXT_GRAY_MEDIUM
        )
        license_label.pack(pady=(0, 5))
        
        # GitHub link (clickable)
        github_label = ttk.Label(
            content_frame,
            text="GitHub",
            font=config.get_font(config.Fonts.SIZE_TINY, 'underline'),
            foreground=config.Colors.BLUE_LINK,
            cursor='hand2'
        )
        github_label.pack(pady=(0, 20))
        
        # Make GitHub link clickable
        def open_github(event):
            webbrowser.open('https://github.com/aHuddini/LiteFinPad')
        
        github_label.bind('<Button-1>', open_github)
        
        # Close link - simple clickable text
        close_label = ttk.Label(
            content_frame,
            text="Close",
            font=config.get_font(config.Fonts.SIZE_SMALL, 'underline'),
            foreground=config.Colors.BLUE_LINK,
            cursor='hand2'
        )
        close_label.pack()
        close_label.bind('<Button-1>', lambda e: dialog.destroy())
        
        # Bind Escape key to close
        DialogHelper.bind_escape_to_close(dialog)
        
        # Center the dialog
        DialogHelper.center_on_parent(
            dialog,
            self.root,
            config.Dialog.ABOUT_WIDTH,
            config.Dialog.ABOUT_HEIGHT
        )
        
        # Show the dialog
        DialogHelper.show_dialog(dialog)
        
    def update_display(self):
        """Update all display elements"""
        # Update total
        self.total_label.config(text=f"${self.expense_tracker.monthly_total:.2f}")
        
        # Update count (exclude future expenses)
        from datetime import datetime
        today = datetime.now().date()
        past_expenses = [e for e in self.expense_tracker.expenses 
                        if datetime.strptime(e['date'], '%Y-%m-%d').date() <= today]
        expense_count = len(past_expenses)
        self.count_label.config(text=f"{expense_count} expenses this month")
        
        # Update progress (averages in progress section)
        daily_avg, days_elapsed = self.expense_tracker.get_daily_average()
        weekly_avg, weeks_elapsed = self.expense_tracker.get_weekly_average()
        
        self.daily_avg_label.config(text=f"${daily_avg:.2f} /day")
        self.weekly_avg_label.config(text=f"${weekly_avg:.2f} /week")
        
        # Update analytics (weekly pace and previous month)
        weekly_pace, pace_days = self.expense_tracker.get_weekly_pace()
        trend_text, trend_context = self.expense_tracker.get_monthly_trend_analysis()
        
        self.pace_label.config(text=f"${weekly_pace:.2f} /day")
        self.trend_label.config(text=f"{trend_text}")
        
        # Update recent expenses
        self.update_recent_expenses()
        
    def create_expense_metrics_section(self):
        """Create expense metrics section for the expense list page"""
        metrics_frame = ttk.LabelFrame(self.expense_list_frame, text="Expense Insights", padding="10")
        metrics_frame.grid(row=1, column=0, pady=(0, 10), sticky=(tk.W, tk.E))
        
        # Get metrics data
        median_expense, expense_count = self.expense_tracker.get_median_expense()
        largest_expense, largest_desc = self.expense_tracker.get_largest_expense()
        total_amount = self.expense_tracker.monthly_total
        
        # Three columns: Typical Expense | Total Amount | Largest Expense
        row = ttk.Frame(metrics_frame)
        row.pack(fill=tk.X)
        
        # Typical expense (left)
        typical_frame = ttk.Frame(row)
        typical_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        
        ttk.Label(typical_frame, text="Typical Expense", font=config.get_font(config.Fonts.SIZE_SMALL, 'bold'), foreground=config.Colors.TEXT_GRAY_DARK).pack()
        self.list_median_label = ttk.Label(typical_frame, text=f"${median_expense:.2f}", style='Analytics.TLabel')
        self.list_median_label.pack()
        self.median_count_label = ttk.Label(typical_frame, text=f"(median of {expense_count} expense{'s' if expense_count != 1 else ''})", font=config.Fonts.LABEL_SMALL, foreground=config.Colors.TEXT_GRAY_MEDIUM)
        self.median_count_label.pack()
        
        # Total amount (center)
        total_frame = ttk.Frame(row)
        total_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
        
        ttk.Label(total_frame, text="Total Amount", font=config.get_font(config.Fonts.SIZE_SMALL, 'bold'), foreground=config.Colors.GREEN_PRIMARY).pack()
        self.list_total_label = ttk.Label(total_frame, text=f"${total_amount:.2f}", style='Analytics.TLabel', foreground=config.Colors.GREEN_PRIMARY)
        self.list_total_label.pack()
        expense_count_total = len(self.expense_tracker.expenses)
        self.total_count_label = ttk.Label(total_frame, text=f"({expense_count_total} expense{'s' if expense_count_total != 1 else ''})", font=config.Fonts.LABEL_SMALL, foreground=config.Colors.TEXT_GRAY_MEDIUM)
        self.total_count_label.pack()
        
        # Largest expense (right)
        largest_frame = ttk.Frame(row)
        largest_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))
        
        ttk.Label(largest_frame, text="Largest Expense", font=config.get_font(config.Fonts.SIZE_SMALL, 'bold'), foreground=config.Colors.RED_PRIMARY).pack()
        self.largest_label = ttk.Label(largest_frame, text=f"${largest_expense:.2f}", style='Analytics.TLabel')
        self.largest_label.pack()
        self.largest_desc_label = ttk.Label(largest_frame, text=f"({largest_desc})", font=config.Fonts.LABEL_SMALL, foreground=config.Colors.TEXT_GRAY_MEDIUM)
        self.largest_desc_label.pack()
    
    def create_quick_add_section(self):
        """Create inline quick add section at bottom of expense list page"""
        from datetime import datetime
        from calendar import monthrange
        
        # Quick Add container at bottom (row 3)
        quick_add_frame = ttk.LabelFrame(self.expense_list_frame, text="Quick Add Expense", padding="15")
        quick_add_frame.grid(row=3, column=0, pady=(10, 0), sticky=(tk.W, tk.E))
        quick_add_frame.columnconfigure(0, weight=1)
        
        # Row 1: Amount and Description
        row1_container = ttk.Frame(quick_add_frame)
        row1_container.pack(fill=tk.X, pady=(0, 10))
        
        # Amount field (left, reduced width)
        amount_frame = ttk.Frame(row1_container)
        amount_frame.pack(side=tk.LEFT, padx=(0, 15))
        ttk.Label(amount_frame, text="Amount ($):", font=config.Fonts.LABEL).pack(anchor=tk.W)
        self.inline_amount_var = tk.StringVar()
        
        # Register validation function for amount field
        vcmd = (self.root.register(validate_amount_input), '%P')
        
        self.inline_amount_entry = ttk.Entry(amount_frame, textvariable=self.inline_amount_var, font=config.Fonts.ENTRY, width=15,
                                            validate='key', validatecommand=vcmd)
        self.inline_amount_entry.pack(pady=(2, 0))
        
        # Description field (right, reduced width)
        desc_frame = ttk.Frame(row1_container)
        desc_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Label(desc_frame, text="Description:", font=config.Fonts.LABEL).pack(anchor=tk.W)
        self.inline_description_entry = ttk.Entry(desc_frame, font=config.Fonts.ENTRY)
        self.inline_description_entry.pack(fill=tk.X, pady=(2, 0))
        
        # Bind Enter key for sequential field navigation
        def handle_amount_enter(event):
            """Enter in amount field moves to description"""
            self.inline_description_entry.focus_set()
            return "break"  # Prevent default behavior
        
        def handle_description_enter(event):
            """Enter in description field submits the form"""
            self.on_inline_add_expense()
            return "break"  # Prevent default behavior
        
        self.inline_amount_entry.bind('<Return>', handle_amount_enter)
        self.inline_description_entry.bind('<Return>', handle_description_enter)
        
        # Row 2: Date and Add button
        row2_container = ttk.Frame(quick_add_frame)
        row2_container.pack(fill=tk.X)
        
        # Date field (left)
        date_frame = ttk.Frame(row2_container)
        date_frame.pack(side=tk.LEFT, padx=(0, 15))
        ttk.Label(date_frame, text="Date:", font=config.Fonts.LABEL).pack(anchor=tk.W)
        
        # Generate date options
        today = datetime.now()
        current_day = today.day
        current_month = today.strftime("%B")
        last_day = monthrange(today.year, today.month)[1]
        
        date_options = []
        for day in range(1, last_day + 1):
            if day == current_day:
                display = f"{day} - {current_month} {day} (Today)"
            elif day > current_day:
                display = f"{day} - {current_month} {day} (Future)"
            else:
                display = f"{day} - {current_month} {day}"
            date_options.append(display)
        
        # Configure custom style for date combobox with darker blue highlight and white text
        style = ttk.Style()
        style.map('DateCombo.TCombobox',
                  fieldbackground=[('readonly', config.Colors.DATE_BG)],
                  foreground=[('readonly', config.Colors.DATE_FG)],
                  selectbackground=[('readonly', config.Colors.DATE_BG)],
                  selectforeground=[('readonly', config.Colors.DATE_FG)])
        style.configure('DateCombo.TCombobox',
                       foreground=config.Colors.DATE_FG,
                       fieldbackground=config.Colors.DATE_BG)
        
        self.inline_date_combo = ttk.Combobox(date_frame, values=date_options, state="readonly", font=config.Fonts.LABEL, width=30, style='DateCombo.TCombobox')
        self.inline_date_combo.set(date_options[current_day - 1])  # Default to today
        self.inline_date_combo.pack(pady=(2, 0))
        
        # Add Item button (right)
        button_frame = ttk.Frame(row2_container)
        button_frame.pack(side=tk.LEFT, padx=(15, 0))
        # Add spacer to align button with entry fields
        ttk.Label(button_frame, text=" ", font=config.Fonts.LABEL).pack()
        self.inline_add_button = ttk.Button(button_frame, text="Add Item", 
                                           command=self.on_inline_add_expense,
                                           style='Modern.TButton')
        self.inline_add_button.pack(pady=(2, 0))
    
    def on_inline_add_expense(self):
        """Handle adding expense from inline form"""
        from datetime import datetime
        from tkinter import messagebox
        from expense_table import ExpenseData
        
        # Validate amount
        amount_str = self.inline_amount_var.get().strip()
        if not amount_str:
            messagebox.showerror("Error", "Please enter an amount")
            return
        
        try:
            amount = float(amount_str)
            if amount <= 0:
                messagebox.showerror("Error", "Amount must be greater than 0")
                return
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid number")
            return
        
        # Validate description
        description = self.inline_description_entry.get().strip()
        if not description:
            messagebox.showerror("Error", "Please enter a description")
            return
        
        # Get selected date
        date_display = self.inline_date_combo.get()
        # Extract day number from display (e.g., "15 - October 15th (Today)" -> 15)
        day_num = int(date_display.split(' - ')[0])
        
        # Format date as YYYY-MM-DD
        today = datetime.now()
        selected_date = today.replace(day=day_num).strftime("%Y-%m-%d")
        
        # Create expense
        expense = ExpenseData(selected_date, amount, description)
        
        # Add to table manager (this will trigger on_expense_change callback)
        self.table_manager.add_expense(expense)
        
        # Clear form
        self.inline_amount_var.set('')
        self.inline_description_entry.delete(0, tk.END)
        # Reset date to today
        current_day = datetime.now().day
        self.inline_date_combo.current(current_day - 1)
        
        # Focus back to amount field for quick entry
        self.inline_amount_entry.focus_set()
    
    def create_table_manager(self):
        """Create the table manager for expense list"""
        def on_expense_change():
            # CRITICAL: Sync the table's expense list back to main application
            table_expenses = self.table_manager.get_expenses()
            self.expense_tracker.expenses = [exp.to_dict() for exp in table_expenses]
            
            # Recalculate monthly total
            self.expense_tracker.monthly_total = sum(exp['amount'] for exp in self.expense_tracker.expenses)
            
            # Save the updated data to disk
            self.expense_tracker.save_data()
            
            # Update the main application display
            self.expense_tracker.gui.update_display()
            # Update expense metrics
            self.update_expense_metrics()
            # Update tray icon tooltip with new total
            self.expense_tracker.update_tray_tooltip()
        
        # Create a frame for the table at row=2 (row=1 is metrics, row=3 is quick add at bottom)
        table_container = ttk.Frame(self.expense_list_frame)
        table_container.grid(row=2, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        table_container.columnconfigure(0, weight=1)
        table_container.rowconfigure(0, weight=1)
        
        from expense_table import ExpenseTableManager
        self.table_manager = ExpenseTableManager(table_container, on_expense_change)
        
    def create_expense_list_page(self):
        """Create the expense list page"""
        # Create expense list frame as a sibling to main_frame
        self.expense_list_frame = ttk.Frame(self.main_container, padding="25")
        self.expense_list_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.expense_list_frame.columnconfigure(0, weight=1)
        self.expense_list_frame.rowconfigure(2, weight=1)  # Give weight to table area (row 2 - main focus)
        
        # Header with back button and export button
        header_frame = ttk.Frame(self.expense_list_frame)
        header_frame.grid(row=0, column=0, pady=(0, 15), sticky=(tk.W, tk.E))
        header_frame.columnconfigure(1, weight=1)  # Give weight to title
        
        # Back button (simple arrow icon)
        back_button = ttk.Button(header_frame, text="←", 
                               command=self.show_main_page, style='Modern.TButton', width=3)
        back_button.grid(row=0, column=0, sticky=tk.W, padx=(0, 15))
        
        # Title
        title_label = ttk.Label(header_frame, text="Expense List", style='Title.TLabel')
        title_label.grid(row=0, column=1, sticky=(tk.W, tk.E))
        
        # Button frame (on the right side) - stacks Export and Import buttons
        button_frame = ttk.Frame(header_frame)
        button_frame.grid(row=0, column=2, sticky=tk.E, padx=(15, 0))
        
        # Export button
        export_button = ttk.Button(button_frame, text="📤 Export", 
                                   command=self.expense_tracker.export_expenses_dialog,
                                   width=10)
        export_button.pack(pady=(0, 5))
        
        # Import button (below Export)
        import_button = ttk.Button(button_frame, text="📥 Import", 
                                   command=self.expense_tracker.import_expenses_dialog,
                                   width=10)
        import_button.pack()
        
        # Expense metrics section (row 1)
        self.create_expense_metrics_section()
        
        # Table manager (row 2 - main focus)
        self.create_table_manager()
        
        # Quick Add section (row 3 - bottom)
        self.create_quick_add_section()
        
        # Initially hide the expense list page
        self.expense_list_frame.grid_remove()
        
    def update_expense_metrics(self):
        """Update the expense metrics on the expense list page"""
        median_expense, expense_count = self.expense_tracker.get_median_expense()
        largest_expense, largest_desc = self.expense_tracker.get_largest_expense()
        total_amount = self.expense_tracker.monthly_total
        
        self.list_median_label.config(text=f"${median_expense:.2f}")
        self.median_count_label.config(text=f"(median of {expense_count} expense{'s' if expense_count != 1 else ''})")
        self.list_total_label.config(text=f"${total_amount:.2f}")
        expense_count_total = len(self.expense_tracker.expenses)
        self.total_count_label.config(text=f"({expense_count_total} expense{'s' if expense_count_total != 1 else ''})")
        self.largest_label.config(text=f"${largest_expense:.2f}")
        self.largest_desc_label.config(text=f"({largest_desc})")
    
    def show_expense_list_page(self):
        """Show the expense list page"""
        self.current_page = "expense_list"
        # Hide main content
        self.main_frame.grid_remove()
        # Show expense list
        self.expense_list_frame.grid()
        # Update metrics
        self.update_expense_metrics()
        # Load expenses into table
        if hasattr(self, 'table_manager') and self.table_manager:
            self.table_manager.load_expenses(self.expense_tracker.expenses)
        
    def show_main_page(self):
        """Show the main dashboard page"""
        self.current_page = "main"
        # Hide expense list
        self.expense_list_frame.grid_remove()
        # Show main content
        self.main_frame.grid()
