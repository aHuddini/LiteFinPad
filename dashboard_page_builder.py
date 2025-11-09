"""
Dashboard Page Builder - UI Construction for Main Dashboard

Handles all widget creation and layout for the main dashboard page.
Separates UI construction from update logic and event handling.
"""

import tkinter as tk
from tkinter import ttk
import customtkinter as ctk
from datetime import datetime, timedelta
import config
from analytics import ExpenseAnalytics
from date_utils import DateUtils
from settings_manager import get_settings_manager


class DashboardPageBuilder:
    """
    Constructs the main dashboard UI with all sections.
    
    Responsibilities:
    - Create all dashboard widgets
    - Set up layout and styling
    - Wire up event handlers
    - Return widget references for updates
    """
    
    def __init__(self, parent_frame, expense_tracker, callbacks, tooltip_manager):
        """
        Initialize the dashboard builder.
        
        Args:
            parent_frame: The main frame to build widgets in
            expense_tracker: Reference to ExpenseTracker for data access
            callbacks: Dict of callback functions for events
            tooltip_manager: TooltipManager for creating tooltips
        """
        self.frame = parent_frame
        self.tracker = expense_tracker
        self.callbacks = callbacks
        self.tooltip_manager = tooltip_manager
        
        # Widget references to be returned
        self.widgets = {}
        
    def build_all(self):
        """Build all dashboard sections and return widget references"""
        self.create_header()
        self.create_total_section()
        self.create_progress_section()  # Now includes title at row 4, frame at row 5
        self.create_analytics_section()  # Title at row 6, frame at row 7
        self.create_expenses_section()  # Title at row 8, frame at row 9
        self.create_buttons_section()    # Row 10
        
        return self.widgets
        
    def create_header(self):
        """Create header with perfectly centered title and controls - using CustomTkinter"""
        # Header frame - full width (using CTkFrame for consistency)
        header_frame = ctk.CTkFrame(self.frame, fg_color="transparent")
        header_frame.grid(row=0, column=0, columnspan=2, pady=(0, 5), sticky=(tk.W, tk.E))  # Further reduced header spacing
        # No weight needed - we want left alignment, not centering
        
        # Month/Year title - perfectly centered and clickable (using CTkLabel)
        month_text = self.tracker.month_viewer.format_month_display(
            self.tracker.viewed_month
        )
        month_label = ctk.CTkLabel(
            header_frame, 
            text=month_text, 
            font=config.Fonts.TITLE,
            text_color=config.Colors.TEXT_BLACK,  # Explicit color for visibility
            cursor='hand2'  # Hand cursor to indicate clickability
        )
        month_label.grid(row=0, column=0, sticky=tk.W)  # Left-align, not centered
        
        # Bind click event to open month navigation menu
        month_label.bind('<Button-1>', self.callbacks['show_month_navigation_menu'])
        
        # Store reference
        self.widgets['month_label'] = month_label
        
        # Control buttons frame - positioned absolutely on the right
        controls_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        controls_frame.place(relx=1.0, x=-4, y=5, anchor='ne')  # Moved 3 pixels to the right
        
        # About button (info icon) - using CTkLabel for modern appearance
        about_label = ctk.CTkLabel(
            controls_frame,
            text="ℹ️",
            font=config.get_font(config.Fonts.SIZE_MEDIUM),
            text_color=config.Colors.TEXT_BLACK,  # Explicit color for visibility
            cursor='hand2'
        )
        about_label.pack(side=tk.LEFT, padx=(0, 1))
        
        # Bind click event
        about_label.bind('<Button-1>', lambda e: self.callbacks['show_about_dialog']())
        
        # Add tooltip
        self.tooltip_manager.create(about_label, "About LiteFinPad")
        
        # Store reference
        self.widgets['about_label'] = about_label
        
        # Stay on top control (default: enabled) - using CTkLabel for modern appearance
        stay_on_top_var = tk.BooleanVar(value=True)
        self.widgets['stay_on_top_var'] = stay_on_top_var
        
        # Use CTkLabel for modern appearance
        stay_on_top_label = ctk.CTkLabel(
            controls_frame,
            text="📌",
            font=config.get_font(config.Fonts.SIZE_MEDIUM),
            fg_color=config.Colors.BG_BUTTON_DISABLED,  # Gray background when ON
            cursor='hand2',  # Hand cursor to show it's clickable
            padx=5,
            pady=2,
            corner_radius=config.CustomTkinterTheme.CORNER_RADIUS
        )
        stay_on_top_label.pack(side=tk.LEFT, padx=(0, 5))
        
        # Bind click event
        stay_on_top_label.bind('<Button-1>', lambda e: self.callbacks['toggle_stay_on_top_visual']())
        
        # Add tooltip
        self.tooltip_manager.create(stay_on_top_label, "Stay on Top (ON)")
        
        # Store reference
        self.widgets['stay_on_top_label'] = stay_on_top_label
        
        # Minimize to tray button - using CTkButton with dark navy blue
        minimize_button = ctk.CTkButton(
            controls_frame,
            text="➖",
            command=self.tracker.window_manager.hide_window,
            width=30,
            height=25,
            corner_radius=config.CustomTkinterTheme.CORNER_RADIUS,
            font=config.get_font(config.Fonts.SIZE_MEDIUM),
            fg_color=config.Colors.BLUE_DARK_NAVY,  # Dark navy blue
            hover_color=config.Colors.BLUE_NAVY,  # Lighter navy on hover
            text_color="white"
        )
        minimize_button.pack(side=tk.LEFT)
        
        # Add tooltip
        self.tooltip_manager.create(minimize_button, "Minimize to Tray")
        
        # Store reference
        self.widgets['minimize_button'] = minimize_button
        
    def create_total_section(self):
        """Create monthly total display section - using CustomTkinter"""
        # Monthly total display (using CTkLabel for modern appearance)
        total_label = ctk.CTkLabel(
            self.frame,
            text=f"${self.tracker.monthly_total:.2f}",
            font=config.Fonts.HERO_TOTAL,
            text_color=config.Colors.GREEN_PRIMARY
        )
        total_label.grid(row=1, column=0, columnspan=2, pady=(0, 0))  # No spacing - bring "(Total Monthly)" very close
        self.widgets['total_label'] = total_label
        
        # Sublabel: (Total Monthly) - using CTkLabel
        ctk.CTkLabel(
            self.frame,
            text="(Total Monthly)",
            font=config.Fonts.LABEL,
            text_color=config.Colors.TEXT_GRAY_MEDIUM
        ).grid(row=2, column=0, columnspan=2, pady=(0, 0))  # No spacing - bring expense count very close
        
        # Expense count display (exclude future expenses) - using CTkLabel
        today = datetime.now().date()
        past_expenses = [e for e in self.tracker.expenses 
                        if (dt := DateUtils.parse_date(e['date'])) and dt.date() <= today]
        expense_count = len(past_expenses)
        count_label = ctk.CTkLabel(
            self.frame,
            text=f"{expense_count} expenses this month",
            font=config.get_font(config.Fonts.SIZE_LARGE),
            text_color=config.Colors.TEXT_BLACK  # Explicit color for visibility
        )
        count_label.grid(row=3, column=0, columnspan=2, pady=(0, 6))  # Reduced to 6 for more compact layout
        self.widgets['count_label'] = count_label
        
    def create_progress_section(self):
        """Create current progress section with averages - using CustomTkinter"""
        # Title label OUTSIDE the frame (like ttk.LabelFrame puts title above border)
        # ttk.LabelFrame titles use smaller font (typically 9-10pt), reduce from SIZE_NORMAL (11pt)
        title_label = ttk.Label(self.frame, text="Current Progress", font=config.get_font(config.Fonts.SIZE_SMALL))  # 10pt instead of 11pt
        title_label.grid(row=4, column=0, columnspan=2, pady=(0, 0), sticky=tk.W)  # No spacing - bring frame closer
        
        # Match EXACT original ttk.LabelFrame: padding="10", visible border
        progress_frame = ctk.CTkFrame(
            self.frame, 
            fg_color=config.Colors.BG_LIGHT_GRAY,
            border_width=1,
            border_color=config.Colors.BG_DARK_GRAY  # Visible border like ttk.LabelFrame
        )
        progress_frame.grid(row=5, column=0, columnspan=2, pady=(0, 6), sticky=(tk.W, tk.E))  # Reduced spacing between sections
        
        # Get progress data (use archive context if in archive mode)
        context_date = self.callbacks['get_context_date']()
        current_day, total_days = ExpenseAnalytics.calculate_day_progress(context_date)
        current_week, total_weeks = ExpenseAnalytics.calculate_week_progress(context_date)
        daily_avg, days_elapsed = ExpenseAnalytics.calculate_daily_average(
            self.tracker.expenses, context_date
        )
        weekly_avg, weeks_elapsed = ExpenseAnalytics.calculate_weekly_average(
            self.tracker.expenses, context_date
        )
        
        # Top row: Day and Week progress (centered and close together)
        # Original: top_row.pack(fill=tk.X, pady=(0, 8))
        top_row = ttk.Frame(progress_frame)
        top_row.pack(fill=tk.X, pady=(8, 6), padx=10)  # Reduced padding - 8px top instead of 10px, 6px bottom instead of 8px
        
        # Centered container to hold both labels (centers Day and Week together)
        top_center_container = ttk.Frame(top_row)
        top_center_container.pack(expand=True)  # Center the container
        
        # Day progress (left) - keep close to center
        day_container = ttk.Frame(top_center_container)
        day_container.pack(side=tk.LEFT, padx=(0, 25))  # 25px gap between Day and Week
        ttk.Label(day_container, text="Day: ", font=config.get_font(config.Fonts.SIZE_NORMAL, 'bold'), foreground=config.Colors.BLUE_NAVY).pack(side=tk.LEFT)
        day_progress_label = ttk.Label(day_container, text=f"{current_day} / {total_days}", style='Analytics.TLabel')
        day_progress_label.pack(side=tk.LEFT)
        self.widgets['day_progress_label'] = day_progress_label
        
        # Week progress (right) - keep close to center
        week_container = ttk.Frame(top_center_container)
        week_container.pack(side=tk.LEFT, padx=(25, 0))  # 25px gap between Day and Week
        ttk.Label(week_container, text="Week: ", font=config.get_font(config.Fonts.SIZE_NORMAL, 'bold'), foreground=config.Colors.BLUE_NAVY).pack(side=tk.LEFT)
        
        # For archive mode, show clean week numbers (no decimals for completed months)
        if self.callbacks['is_archive_mode']():
            week_display = f"{round(current_week)} / {total_weeks}"
        else:
            week_display = f"{current_week:.1f} / {total_weeks}"
        week_progress_label = ttk.Label(week_container, text=week_display, style='Analytics.TLabel')
        week_progress_label.pack(side=tk.LEFT)
        self.widgets['week_progress_label'] = week_progress_label
        
        # Bottom row: Daily and Weekly averages (centered and close together)
        # Original: bottom_row.pack(fill=tk.X, pady=(8, 0))
        bottom_row = ttk.Frame(progress_frame)
        bottom_row.pack(fill=tk.X, pady=(6, 8), padx=10)  # Reduced spacing - 6px top instead of 8px, 8px bottom instead of 10px
        
        # Centered container to hold both averages (centers Daily and Weekly together)
        bottom_center_container = ttk.Frame(bottom_row)
        bottom_center_container.pack(expand=True)  # Center the container
        
        # Daily average (left) - keep close to center
        daily_avg_frame = ttk.Frame(bottom_center_container)
        daily_avg_frame.pack(side=tk.LEFT, padx=(0, 25))  # 25px gap between Daily and Weekly
        ttk.Label(daily_avg_frame, text="Daily Average", font=config.get_font(config.Fonts.SIZE_NORMAL, 'bold'), foreground=config.Colors.TEAL_DARK).pack()
        daily_avg_label = ttk.Label(daily_avg_frame, text=f"${daily_avg:.2f} /day", style='Analytics.TLabel')
        daily_avg_label.pack()
        self.widgets['daily_avg_label'] = daily_avg_label
        
        # Weekly average (right) - keep close to center
        weekly_avg_frame = ttk.Frame(bottom_center_container)
        weekly_avg_frame.pack(side=tk.LEFT, padx=(25, 0))  # 25px gap between Daily and Weekly
        ttk.Label(weekly_avg_frame, text="Weekly Average", font=config.get_font(config.Fonts.SIZE_NORMAL, 'bold'), foreground=config.Colors.AMBER_DARK).pack()
        weekly_avg_label = ttk.Label(weekly_avg_frame, text=f"${weekly_avg:.2f} /week", style='Analytics.TLabel')
        weekly_avg_label.pack()
        self.widgets['weekly_avg_label'] = weekly_avg_label
        
    def create_analytics_section(self):
        """Create spending analysis section - using CustomTkinter"""
        # Title label OUTSIDE the frame (like ttk.LabelFrame puts title above border)
        # ttk.LabelFrame titles use smaller font (typically 9-10pt), reduce from SIZE_NORMAL (11pt)
        title_label = ttk.Label(self.frame, text="Spending Analysis", font=config.get_font(config.Fonts.SIZE_SMALL))  # 10pt instead of 11pt
        title_label.grid(row=6, column=0, columnspan=2, pady=(0, 0), sticky=tk.W)  # No spacing - bring frame closer
        
        # Match EXACT original ttk.LabelFrame: padding="10", visible border
        analytics_frame = ctk.CTkFrame(
            self.frame, 
            fg_color=config.Colors.BG_LIGHT_GRAY,
            border_width=1,
            border_color=config.Colors.BG_DARK_GRAY  # Visible border like ttk.LabelFrame
        )
        analytics_frame.grid(row=7, column=0, columnspan=2, pady=(0, 6), sticky=(tk.W, tk.E))  # Reduced spacing between sections
        
        # Get analytics data (use archive context if in archive mode)
        context_date = self.callbacks['get_context_date']()
        weekly_pace, pace_days = ExpenseAnalytics.calculate_weekly_pace(
            self.tracker.expenses, context_date
        )
        
        # Calculate previous month data with comparison
        # Pass viewed_month only if truly in archive mode (not current month)
        viewed_month = self.tracker.viewed_month if self.callbacks['is_archive_mode']() else None
        prev_month_date = datetime.now().replace(day=1) - timedelta(days=1)
        prev_month_key = prev_month_date.strftime('%Y-%m')
        prev_data_folder = f"data_{prev_month_key}"
        prev_month_total, prev_month_name, comparison = ExpenseAnalytics.calculate_monthly_trend(
            prev_data_folder,
            self.tracker.monthly_total,
            viewed_month
        )
        
        # Side by side: Weekly Pace and Previous Month
        # Original: row = ttk.Frame(analytics_frame); row.pack(fill=tk.X)
        # padding="10" means 10px all around, but optimize for compactness
        row = ttk.Frame(analytics_frame)
        row.pack(fill=tk.X, padx=10, pady=(8, 8))  # Reduced from 10 to 8 for more compact layout
        
        # Weekly pace (left)
        # Original: pace_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        pace_frame = ttk.Frame(row)
        pace_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))  # Reduced gap from 10 to 5
        
        # Original: ttk.Label().pack() - default pack() with no pady means minimal spacing
        ttk.Label(pace_frame, text="Weekly Pace", font=config.get_font(config.Fonts.SIZE_NORMAL, 'bold'), foreground=config.Colors.ORANGE_PRIMARY).pack()
        pace_label = ttk.Label(pace_frame, text=f"${weekly_pace:.2f} /day", style='Analytics.TLabel')
        pace_label.pack()
        ttk.Label(pace_frame, text=f"(this week: {pace_days} day{'s' if pace_days != 1 else ''})", font=config.Fonts.LABEL, foreground=config.Colors.TEXT_GRAY_MEDIUM).pack()
        self.widgets['pace_label'] = pace_label
        
        # vs. Budget (middle)
        budget_frame = ttk.Frame(row)
        budget_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
        
        ttk.Label(budget_frame, text="vs. Budget", font=config.get_font(config.Fonts.SIZE_NORMAL, 'bold'), foreground=config.Colors.BLUE_DARK_NAVY).pack()
        
        # Read budget threshold from settings
        budget_threshold = get_settings_manager().get('Budget', 'monthly_threshold', 0.0)
        
        # Convert to float (settings returns string)
        try:
            budget_threshold = float(budget_threshold)
        except (ValueError, TypeError):
            budget_threshold = 0.0
        
        if budget_threshold > 0:
            difference = budget_threshold - self.tracker.monthly_total
            
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
        
        # Amount label (number) - clickable - using ttk.Label for exact match
        budget_amount_label = ttk.Label(budget_frame, text=budget_amount_text, style='Analytics.TLabel', foreground=budget_color, cursor='hand2')
        budget_amount_label.pack()
        budget_amount_label.bind('<Button-1>', self.callbacks['show_budget_dialog'])
        self.widgets['budget_amount_label'] = budget_amount_label
        
        # Status label (Under/Over/Click Here) - always show, also clickable
        budget_status_label = ttk.Label(budget_frame, text=budget_status_text, font=config.Fonts.LABEL, foreground=budget_color, cursor='hand2')
        budget_status_label.pack()
        budget_status_label.bind('<Button-1>', self.callbacks['show_budget_dialog'])
        self.widgets['budget_status_label'] = budget_status_label
        
        # Previous month (right)
        # Original: prev_month_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(10, 0))
        prev_month_frame = ttk.Frame(row)
        prev_month_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))  # Reduced gap from 10 to 5
        
        # Original: ttk.Label().pack() - default pack() with no pady means minimal spacing
        ttk.Label(prev_month_frame, text="Previous Month", font=config.get_font(config.Fonts.SIZE_NORMAL, 'bold'), foreground=config.Colors.PURPLE_PRIMARY).pack()
        
        # Amount with comparison indicator (side-by-side)
        amount_container = ttk.Frame(prev_month_frame)
        amount_container.pack()
        
        # Previous month amount
        trend_label = ttk.Label(amount_container, text=f"{prev_month_total} ", style='Trend.TLabel')
        trend_label.pack(side=tk.LEFT)
        self.widgets['trend_label'] = trend_label
        
        # Comparison indicator (smaller font, colored)
        comparison_label = ttk.Label(
            amount_container,
            text="",  # Will be updated with indicator
            font=config.get_font(9),  # Smaller font (9pt instead of 11pt in PoC)
            foreground='#999999'  # Default gray
        )
        comparison_label.pack(side=tk.LEFT)
        self.widgets['comparison_label'] = comparison_label
        
        # Update comparison indicator if available
        if comparison:
            indicator_text = f"{comparison['symbol']} "
            if comparison['direction'] == 'similar':
                indicator_text += f"+{comparison['percentage']:.1f}%"
            else:
                sign = "+" if comparison['direction'] == 'increase' else "-"
                indicator_text += f"{sign}{comparison['percentage']:.0f}%"
            
            comparison_label.configure(foreground=comparison['color'], text=indicator_text)
        
        # Month name context (will update dynamically when switching months)
        trend_context_label = ttk.Label(prev_month_frame, text=prev_month_name, font=config.Fonts.LABEL, foreground=config.Colors.TEXT_GRAY_MEDIUM)
        trend_context_label.pack()
        self.widgets['trend_context_label'] = trend_context_label
        
    def create_expenses_section(self):
        """Create recent expenses section - using CustomTkinter"""
        # Title label OUTSIDE the frame (like ttk.LabelFrame puts title above border)
        # ttk.LabelFrame titles use smaller font (typically 9-10pt), reduce from SIZE_NORMAL (11pt)
        title_label = ttk.Label(self.frame, text="Recent Expenses", font=config.get_font(config.Fonts.SIZE_SMALL))  # 10pt instead of 11pt
        title_label.grid(row=8, column=0, columnspan=2, pady=(0, 0), sticky=tk.W)  # No spacing - bring frame closer
        
        # Match EXACT original ttk.LabelFrame: padding="10", visible border
        expenses_frame = ctk.CTkFrame(
            self.frame, 
            fg_color=config.Colors.BG_LIGHT_GRAY,
            border_width=1,
            border_color=config.Colors.BG_DARK_GRAY  # Visible border like ttk.LabelFrame
        )
        expenses_frame.grid(row=9, column=0, columnspan=2, pady=(0, 5), sticky=(tk.W, tk.E, tk.N, tk.S))  # Reduced spacing, allow expansion
        
        # Configure minimum height for the frame - make it taller so Recent Expenses is visible
        # Original used height=90, but we need more space for visibility
        # Don't use grid_propagate(False) - let it expand naturally with row weight
        expenses_frame.columnconfigure(0, weight=1)  # Original: columnconfigure(0, weight=1)
        
        # Container for expense labels with padding
        # Original: expenses_container.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        # Optimize padding for compactness while maintaining visibility
        expenses_container = ttk.Frame(expenses_frame)
        expenses_container.pack(fill=tk.BOTH, expand=True, padx=8, pady=(8, 8))  # Reduced from 10 to 8 for compactness
        
        # Create individual expense labels for better visibility (left-aligned, brown color)
        # Only showing 2 most recent expenses
        # Original: ttk.Label with anchor='w', pady=3
        recent_expense_1 = ttk.Label(expenses_container, text="No recent expenses", font=config.Fonts.LABEL, foreground=config.Colors.TEXT_BROWN, anchor='w')
        recent_expense_1.pack(pady=2, fill=tk.X)  # Reduced from 3 to 2 for tighter spacing
        self.widgets['recent_expense_1'] = recent_expense_1
        
        recent_expense_2 = ttk.Label(expenses_container, text="", font=config.Fonts.LABEL, foreground=config.Colors.TEXT_BROWN, anchor='w')
        recent_expense_2.pack(pady=2, fill=tk.X)  # Reduced from 3 to 2 for tighter spacing
        self.widgets['recent_expense_2'] = recent_expense_2
        
    def create_buttons_section(self):
        """Create button section with proper spacing - using CustomTkinter CTkButton"""
        # Original: button_frame.grid(row=7, column=0, columnspan=2, pady=(0, 10), sticky=(tk.W, tk.E))
        button_frame = ttk.Frame(self.frame)
        button_frame.grid(row=10, column=0, columnspan=2, pady=(0, 5), sticky=(tk.W, tk.E))  # Reduced bottom padding
        
        # Add expense button (with green accent) - using CustomTkinter for modern appearance
        # Original: ttk.Button with style='AddExpense.TButton', sticky=(tk.W, tk.E) - buttons expand to fill
        # Make buttons skinnier by reducing height
        add_expense_btn = ctk.CTkButton(
            button_frame,
            text="+ Add Expense",
            command=self.tracker.add_expense,
            fg_color=config.Colors.GREEN_PRIMARY,
            hover_color=config.Colors.GREEN_HOVER,
            corner_radius=config.CustomTkinterTheme.CORNER_RADIUS,
            height=30,  # Reduced from BUTTON_HEIGHT (35) to 30 for more compact appearance
            font=config.Fonts.BUTTON,
            text_color="white"  # Explicit text color for visibility
        )
        add_expense_btn.grid(row=0, column=0, padx=(0, 8), sticky=(tk.W, tk.E))  # Reduced padx from 10 to 8
        self.widgets['add_expense_btn'] = add_expense_btn
        
        # Navigation button to switch to Expense List page - using CustomTkinter with dark navy blue
        # Original: ttk.Button with style='Modern.TButton', sticky=(tk.W, tk.E) - buttons expand to fill
        # Make buttons skinnier by reducing height
        nav_button = ctk.CTkButton(
            button_frame,
            text="📋 Expense List",
            command=self.tracker.show_expense_list_page,
            corner_radius=config.CustomTkinterTheme.CORNER_RADIUS,
            height=30,  # Reduced from BUTTON_HEIGHT (35) to 30 for more compact appearance
            font=config.Fonts.BUTTON,
            fg_color=config.Colors.BLUE_DARK_NAVY,  # Dark navy blue
            hover_color=config.Colors.BLUE_NAVY,  # Lighter navy on hover
            text_color="white"  # Explicit text color for visibility
        )
        nav_button.grid(row=0, column=1, padx=(8, 0), sticky=(tk.W, tk.E))  # Reduced padx from 10 to 8
        
        # Configure button frame columns - original had weight=1 to allow expansion
        button_frame.columnconfigure(0, weight=1)  # Original: allow column 0 to expand
        button_frame.columnconfigure(1, weight=1)  # Original: allow column 1 to expand

