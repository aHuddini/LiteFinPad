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
    
    def __init__(self, parent_frame, expense_tracker, callbacks, tooltip_manager, theme_manager):
        """
        Initialize the dashboard builder.
        
        Args:
            parent_frame: The main frame to build widgets in
            expense_tracker: Reference to ExpenseTracker for data access
            callbacks: Dict of callback functions for events
            tooltip_manager: TooltipManager for creating tooltips
            theme_manager: ThemeManager instance for theme-aware colors
        """
        self.frame = parent_frame
        self.tracker = expense_tracker
        self.callbacks = callbacks
        self.tooltip_manager = tooltip_manager
        self.theme_manager = theme_manager
        
        # Get theme-aware colors
        self.colors = theme_manager.get_colors() if theme_manager else config.Colors
        
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
            text_color=self.colors.TEXT_BLACK,  # Theme-aware color
            cursor='hand2'  # Hand cursor to indicate clickability
        )
        month_label.grid(row=0, column=0, sticky=tk.W)  # Left-align, not centered
        
        # Bind click event to open month navigation menu
        month_label.bind('<Button-1>', self.callbacks['show_month_navigation_menu'])
        
        # Store reference
        self.widgets['month_label'] = month_label
        
        # Control buttons frame - positioned absolutely on the right edge
        controls_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        controls_frame.place(relx=1.0, x=0, y=5, anchor='ne')  # Aligned to right edge (x=0)
        
        # About button (info icon) - using CTkLabel for modern appearance
        about_label = ctk.CTkLabel(
            controls_frame,
            text="ℹ️",
            font=config.get_font(config.Fonts.SIZE_MEDIUM),
            text_color=self.colors.TEXT_BLACK,  # Theme-aware color
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
        
        # Use CTkLabel for modern appearance - consistent sizing with minimize button
        stay_on_top_label = ctk.CTkLabel(
            controls_frame,
            text="📌",
            font=config.get_font(config.Fonts.SIZE_MEDIUM),
            fg_color=self.colors.BG_BUTTON_DISABLED,  # Theme-aware color
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
        # Consistent sizing with pin button: padx=5, pady=2 means ~30px width, ~28px height
        # Increased height slightly to match PoC (from 25 to 28)
        minimize_button = ctk.CTkButton(
            controls_frame,
            text="➖",
            command=self.tracker.window_manager.hide_window,
            width=30,  # Match pin button effective width (5+5+content)
            height=28,  # Increased from 25 to match PoC and pin button height
            corner_radius=config.CustomTkinterTheme.CORNER_RADIUS,
            font=config.get_font(config.Fonts.SIZE_MEDIUM),
            fg_color=self.colors.BLUE_DARK_NAVY,  # Dark navy blue
            hover_color=self.colors.BLUE_NAVY,  # Lighter navy on hover
            text_color="white"
        )
        minimize_button.pack(side=tk.LEFT, padx=(0, 0))  # No padding to align to right edge
        
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
            text_color=self.colors.GREEN_PRIMARY
        )
        total_label.grid(row=1, column=0, columnspan=2, pady=(0, 0))  # No spacing - bring "(Total Monthly)" very close
        self.widgets['total_label'] = total_label
        
        # Sublabel: (Total Monthly) - using CTkLabel
        ctk.CTkLabel(
            self.frame,
            text="(Total Monthly)",
            font=config.Fonts.LABEL,
            text_color=self.colors.TEXT_GRAY_MEDIUM
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
            text_color=self.colors.TEXT_BLACK  # Explicit color for visibility
        )
        count_label.grid(row=3, column=0, columnspan=2, pady=(0, 6))  # Reduced to 6 for more compact layout
        self.widgets['count_label'] = count_label
        
    def create_progress_section(self):
        """Create current progress section with averages - using CustomTkinter"""
        # Title label OUTSIDE the frame (like ttk.LabelFrame puts title above border)
        # ttk.LabelFrame titles use smaller font (typically 9-10pt), reduce from SIZE_NORMAL (11pt)
        # Use theme-aware text color: TEXT_BLACK (light) or TEXT_PRIMARY (dark)
        # Match parent frame background (main_frame) - BG_SECONDARY in dark, BG_LIGHT_GRAY in light
        frame_bg = self.colors.BG_SECONDARY if self.theme_manager.is_dark_mode() else self.colors.BG_LIGHT_GRAY
        style = ttk.Style()
        style.configure('SectionTitle.TLabel', 
                       font=config.get_font(config.Fonts.SIZE_SMALL),
                       foreground=self.colors.TEXT_BLACK,
                       background=frame_bg)
        title_label = ttk.Label(
            self.frame, 
            text="Current Progress", 
            style='SectionTitle.TLabel'
        )
        title_label.grid(row=4, column=0, columnspan=2, pady=(0, 0), sticky=tk.W)  # No spacing - bring frame closer
        
        # Match PoC: Use BG_LIGHT_GRAY (light) or BG_SECONDARY (dark) with subtle border
        frame_bg = self.colors.BG_SECONDARY if self.theme_manager.is_dark_mode() else self.colors.BG_LIGHT_GRAY
        border_color = self.colors.BG_DARK_GRAY  # Subtle border like PoC
        progress_frame = ctk.CTkFrame(
            self.frame, 
            fg_color=frame_bg,
            border_width=1,
            border_color=border_color
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
        # Configure ttk.Frame to match CTkFrame background (prevents black bar)
        frame_bg = self.colors.BG_SECONDARY if self.theme_manager.is_dark_mode() else self.colors.BG_LIGHT_GRAY
        style = ttk.Style()
        style.configure('Progress.TFrame', background=frame_bg)
        top_row = ttk.Frame(progress_frame, style='Progress.TFrame')
        top_row.pack(fill=tk.X, pady=(8, 6), padx=10)  # Reduced padding - 8px top instead of 10px, 6px bottom instead of 8px
        
        # Centered container to hold both labels (centers Day and Week together)
        top_center_container = ttk.Frame(top_row, style='Progress.TFrame')
        top_center_container.pack(expand=True)  # Center the container
        
        # Day progress (left) - Match PoC: explicit background colors
        day_container = ttk.Frame(top_center_container, style='Progress.TFrame')
        day_container.pack(side=tk.LEFT, padx=(0, 25))  # 25px gap between Day and Week
        frame_bg = self.colors.BG_SECONDARY if self.theme_manager.is_dark_mode() else self.colors.BG_LIGHT_GRAY
        ttk.Label(day_container, text="Day: ", font=config.get_font(config.Fonts.SIZE_NORMAL, 'bold'), 
                 foreground=self.colors.BLUE_NAVY, background=frame_bg).pack(side=tk.LEFT)
        day_progress_label = ttk.Label(day_container, text=f"{current_day} / {total_days}", 
                                       font=config.get_font(config.Fonts.SIZE_NORMAL),
                                       foreground=self.colors.TEXT_BLACK, background=frame_bg)
        day_progress_label.pack(side=tk.LEFT)
        self.widgets['day_progress_label'] = day_progress_label
        
        # Week progress (right) - Match PoC: explicit background colors
        week_container = ttk.Frame(top_center_container, style='Progress.TFrame')
        week_container.pack(side=tk.LEFT, padx=(25, 0))  # 25px gap between Day and Week
        ttk.Label(week_container, text="Week: ", font=config.get_font(config.Fonts.SIZE_NORMAL, 'bold'), 
                 foreground=self.colors.BLUE_NAVY, background=frame_bg).pack(side=tk.LEFT)
        
        # For archive mode, show clean week numbers (no decimals for completed months)
        if self.callbacks['is_archive_mode']():
            week_display = f"{round(current_week)} / {total_weeks}"
        else:
            week_display = f"{current_week:.1f} / {total_weeks}"
        week_progress_label = ttk.Label(week_container, text=week_display, 
                                       font=config.get_font(config.Fonts.SIZE_NORMAL),
                                       foreground=self.colors.TEXT_BLACK, background=frame_bg)
        week_progress_label.pack(side=tk.LEFT)
        self.widgets['week_progress_label'] = week_progress_label
        
        # Bottom row: Daily and Weekly averages (centered and close together)
        # Original: bottom_row.pack(fill=tk.X, pady=(8, 0))
        bottom_row = ttk.Frame(progress_frame, style='Progress.TFrame')
        bottom_row.pack(fill=tk.X, pady=(6, 8), padx=10)  # Reduced spacing - 6px top instead of 8px, 8px bottom instead of 10px
        
        # Centered container to hold both averages (centers Daily and Weekly together)
        bottom_center_container = ttk.Frame(bottom_row, style='Progress.TFrame')
        bottom_center_container.pack(expand=True)  # Center the container
        
        # Daily average (left) - Match PoC: explicit background colors
        daily_avg_frame = ttk.Frame(bottom_center_container, style='Progress.TFrame')
        daily_avg_frame.pack(side=tk.LEFT, padx=(0, 25))  # 25px gap between Daily and Weekly
        ttk.Label(daily_avg_frame, text="Daily Average", 
                 font=config.get_font(config.Fonts.SIZE_NORMAL, 'bold'), 
                 foreground=self.colors.TEAL_DARK, background=frame_bg).pack()
        daily_avg_label = ttk.Label(daily_avg_frame, text=f"${daily_avg:.2f} /day", 
                                   font=config.get_font(config.Fonts.SIZE_NORMAL),
                                   foreground=self.colors.TEXT_BLACK, background=frame_bg)
        daily_avg_label.pack()
        self.widgets['daily_avg_label'] = daily_avg_label
        
        # Weekly average (right) - Match PoC: explicit background colors
        weekly_avg_frame = ttk.Frame(bottom_center_container, style='Progress.TFrame')
        weekly_avg_frame.pack(side=tk.LEFT, padx=(25, 0))  # 25px gap between Daily and Weekly
        ttk.Label(weekly_avg_frame, text="Weekly Average", 
                 font=config.get_font(config.Fonts.SIZE_NORMAL, 'bold'), 
                 foreground=self.colors.AMBER_DARK, background=frame_bg).pack()
        weekly_avg_label = ttk.Label(weekly_avg_frame, text=f"${weekly_avg:.2f} /week", 
                                    font=config.get_font(config.Fonts.SIZE_NORMAL),
                                    foreground=self.colors.TEXT_BLACK, background=frame_bg)
        weekly_avg_label.pack()
        self.widgets['weekly_avg_label'] = weekly_avg_label
        
    def create_analytics_section(self):
        """Create spending analysis section - using CustomTkinter"""
        # Title label OUTSIDE the frame (like ttk.LabelFrame puts title above border)
        # ttk.LabelFrame titles use smaller font (typically 9-10pt), reduce from SIZE_NORMAL (11pt)
        # Use theme-aware text color: TEXT_BLACK (light) or TEXT_PRIMARY (dark)
        # Match parent frame background (main_frame) - BG_SECONDARY in dark, BG_LIGHT_GRAY in light
        frame_bg = self.colors.BG_SECONDARY if self.theme_manager.is_dark_mode() else self.colors.BG_LIGHT_GRAY
        style = ttk.Style()
        style.configure('SectionTitle.TLabel', 
                       font=config.get_font(config.Fonts.SIZE_SMALL),
                       foreground=self.colors.TEXT_BLACK,
                       background=frame_bg)
        title_label = ttk.Label(
            self.frame, 
            text="Spending Analysis", 
            style='SectionTitle.TLabel'
        )
        title_label.grid(row=6, column=0, columnspan=2, pady=(0, 0), sticky=tk.W)  # No spacing - bring frame closer
        
        # Match PoC: Use BG_LIGHT_GRAY (light) or BG_SECONDARY (dark) with subtle border
        frame_bg = self.colors.BG_SECONDARY if self.theme_manager.is_dark_mode() else self.colors.BG_LIGHT_GRAY
        border_color = self.colors.BG_DARK_GRAY  # Subtle border like PoC
        analytics_frame = ctk.CTkFrame(
            self.frame, 
            fg_color=frame_bg,
            border_width=1,
            border_color=border_color
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
        # Configure ttk.Frame to match CTkFrame background (prevents black bar)
        frame_bg = self.colors.BG_SECONDARY if self.theme_manager.is_dark_mode() else self.colors.BG_LIGHT_GRAY
        style = ttk.Style()
        style.configure('Analytics.TFrame', background=frame_bg)
        row = ttk.Frame(analytics_frame, style='Analytics.TFrame')
        row.pack(fill=tk.X, padx=10, pady=(8, 8))  # Reduced from 10 to 8 for more compact layout
        
        # Weekly pace (left) - Match PoC: All labels use same background as frame
        pace_frame = ttk.Frame(row, style='Analytics.TFrame')
        pace_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))  # Reduced gap from 10 to 5
        
        # Match PoC: All labels use same background as frame
        ttk.Label(pace_frame, text="Weekly Pace", 
                 font=config.get_font(config.Fonts.SIZE_NORMAL, 'bold'), 
                 foreground=self.colors.ORANGE_PRIMARY, background=frame_bg).pack()
        pace_label = ttk.Label(pace_frame, text=f"${weekly_pace:.2f} /day", 
                              font=config.get_font(config.Fonts.SIZE_NORMAL),
                              foreground=self.colors.TEXT_BLACK, background=frame_bg)
        pace_label.pack()
        ttk.Label(pace_frame, text=f"(this week: {pace_days} day{'s' if pace_days != 1 else ''})", 
                 font=config.Fonts.LABEL, 
                 foreground=self.colors.TEXT_GRAY_MEDIUM, background=frame_bg).pack()
        self.widgets['pace_label'] = pace_label
        
        # vs. Budget (middle) - Match PoC exactly
        budget_frame = ttk.Frame(row, style='Analytics.TFrame')
        budget_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
        
        # vs. Budget label: Use BLUE_BUDGET in dark mode (#3E6AAA), BLUE_DARK_NAVY in light mode (#1E3A8A)
        # Match PoC: budget_color = colors.BLUE_BUDGET if is_dark and hasattr(colors, 'BLUE_BUDGET') else colors.BLUE_DARK_NAVY
        is_dark = self.theme_manager.is_dark_mode() if self.theme_manager else False
        budget_label_color = self.colors.BLUE_BUDGET if (is_dark and hasattr(self.colors, 'BLUE_BUDGET')) else self.colors.BLUE_DARK_NAVY
        # Match PoC: All labels use same background as frame
        frame_bg = self.colors.BG_SECONDARY if is_dark else self.colors.BG_LIGHT_GRAY
        ttk.Label(budget_frame, text="vs. Budget", font=config.get_font(config.Fonts.SIZE_NORMAL, 'bold'), 
                 foreground=budget_label_color, background=frame_bg).pack()
        
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
                # Under budget (good) - use brighter green in dark mode to match PoC
                budget_amount_text = f"+${difference:,.2f}"
                budget_status_text = "(Under)"
                # In dark mode, GREEN_PRIMARY is already bright (#00cc66), in light mode use standard green
                if self.theme_manager and self.theme_manager.is_dark_mode():
                    budget_color = self.colors.GREEN_PRIMARY  # #00cc66 (bright green for dark mode)
                else:
                    budget_color = config.Colors.GREEN_PRIMARY  # #107c10 (standard green for light mode)
            else:
                # Over budget (warning) - use brighter red in dark mode to match PoC
                budget_amount_text = f"-${abs(difference):,.2f}"
                budget_status_text = "(Over)"
                # In dark mode, RED_PRIMARY is already bright (#f48771), in light mode use standard red
                if self.theme_manager and self.theme_manager.is_dark_mode():
                    budget_color = self.colors.RED_PRIMARY  # #f48771 (coral-red for dark mode)
                else:
                    budget_color = config.Colors.RED_PRIMARY  # #8B0000 (standard red for light mode)
        else:
            # Not set
            budget_amount_text = "Not set"
            budget_status_text = "(Click Here)"
            budget_color = self.colors.TEXT_GRAY_MEDIUM
        
        # Amount label (number) - clickable - Match PoC: use same background as frame
        budget_amount_label = ttk.Label(budget_frame, text=budget_amount_text, 
                                       font=config.get_font(config.Fonts.SIZE_NORMAL),
                                       foreground=budget_color, background=frame_bg, cursor='hand2')
        budget_amount_label.pack()
        budget_amount_label.bind('<Button-1>', self.callbacks['show_budget_dialog'])
        self.widgets['budget_amount_label'] = budget_amount_label
        
        # Status label (Under/Over/Click Here) - always show, also clickable - Match PoC: use same background as frame
        budget_status_label = ttk.Label(budget_frame, text=budget_status_text, 
                                       font=config.Fonts.LABEL, 
                                       foreground=budget_color, background=frame_bg, cursor='hand2')
        budget_status_label.pack()
        budget_status_label.bind('<Button-1>', self.callbacks['show_budget_dialog'])
        self.widgets['budget_status_label'] = budget_status_label
        
        # Previous month (right)
        # Original: prev_month_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(10, 0))
        prev_month_frame = ttk.Frame(row, style='Analytics.TFrame')
        prev_month_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))  # Reduced gap from 10 to 5
        
        # Match PoC: All labels use same background as frame
        frame_bg = self.colors.BG_SECONDARY if self.theme_manager.is_dark_mode() else self.colors.BG_LIGHT_GRAY
        ttk.Label(prev_month_frame, text="Previous Month", 
                 font=config.get_font(config.Fonts.SIZE_NORMAL, 'bold'), 
                 foreground=self.colors.PURPLE_PRIMARY, background=frame_bg).pack()
        
        # Amount with comparison indicator (side-by-side)
        amount_container = ttk.Frame(prev_month_frame, style='Analytics.TFrame')
        amount_container.pack()
        
        # Previous month amount - Match PoC: TEXT_BLACK (light) or TEXT_PRIMARY (dark)
        trend_label = ttk.Label(amount_container, text=f"{prev_month_total} ", 
                               font=config.get_font(config.Fonts.SIZE_NORMAL),
                               foreground=self.colors.TEXT_BLACK, background=frame_bg)
        trend_label.pack(side=tk.LEFT)
        self.widgets['trend_label'] = trend_label
        
        # Comparison indicator (smaller font, colored) - Match PoC: TEXT_GRAY_MEDIUM (light) or TEXT_TERTIARY (dark)
        comparison_label = ttk.Label(
            amount_container,
            text="",  # Will be updated with indicator
            font=config.Fonts.LABEL,  # Match PoC font size (10pt)
            foreground=self.colors.TEXT_GRAY_MEDIUM, background=frame_bg
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
        
        # Month name context (will update dynamically when switching months) - Match PoC
        trend_context_label = ttk.Label(prev_month_frame, text=prev_month_name, 
                                       font=config.Fonts.LABEL, 
                                       foreground=self.colors.TEXT_GRAY_MEDIUM, background=frame_bg)
        trend_context_label.pack()
        self.widgets['trend_context_label'] = trend_context_label
        
    def create_expenses_section(self):
        """Create recent expenses section - using CustomTkinter"""
        # Title label OUTSIDE the frame (like ttk.LabelFrame puts title above border)
        # ttk.LabelFrame titles use smaller font (typically 9-10pt), reduce from SIZE_NORMAL (11pt)
        # Use theme-aware text color: TEXT_BLACK (light) or TEXT_PRIMARY (dark)
        # Match parent frame background (main_frame) - BG_SECONDARY in dark, BG_LIGHT_GRAY in light
        frame_bg = self.colors.BG_SECONDARY if self.theme_manager.is_dark_mode() else self.colors.BG_LIGHT_GRAY
        style = ttk.Style()
        style.configure('SectionTitle.TLabel', 
                       font=config.get_font(config.Fonts.SIZE_SMALL),
                       foreground=self.colors.TEXT_BLACK,
                       background=frame_bg)
        title_label = ttk.Label(
            self.frame, 
            text="Recent Expenses", 
            style='SectionTitle.TLabel'
        )
        title_label.grid(row=8, column=0, columnspan=2, pady=(0, 0), sticky=tk.W)  # No spacing - bring frame closer
        
        # Match PoC: Use BG_LIGHT_GRAY (light) or BG_SECONDARY (dark) with subtle border
        frame_bg = self.colors.BG_SECONDARY if self.theme_manager.is_dark_mode() else self.colors.BG_LIGHT_GRAY
        border_color = self.colors.BG_DARK_GRAY  # Subtle border like PoC
        expenses_frame = ctk.CTkFrame(
            self.frame, 
            fg_color=frame_bg,
            border_width=1,
            border_color=border_color
        )
        expenses_frame.grid(row=9, column=0, columnspan=2, pady=(0, 5), sticky=(tk.W, tk.E, tk.N, tk.S))  # Reduced spacing, allow expansion
        
        # Configure minimum height for the frame - make it taller so Recent Expenses is visible
        # Original used height=90, but we need more space for visibility
        # Don't use grid_propagate(False) - let it expand naturally with row weight
        expenses_frame.columnconfigure(0, weight=1)  # Original: columnconfigure(0, weight=1)
        
        # Container for expense labels with padding
        # Match Analytics section: Use custom style to match CTkFrame background (prevents black bar)
        frame_bg = self.colors.BG_SECONDARY if self.theme_manager.is_dark_mode() else self.colors.BG_LIGHT_GRAY
        style = ttk.Style()
        style.configure('Expenses.TFrame', background=frame_bg)
        expenses_container = ttk.Frame(expenses_frame, style='Expenses.TFrame')
        expenses_container.pack(fill=tk.BOTH, expand=True, padx=8, pady=(8, 8))  # Reduced from 10 to 8 for compactness
        
        # Create individual expense labels for better visibility (left-aligned, brown color)
        # Only showing 2 most recent expenses
        # Match PoC: All labels use same background as frame
        recent_expense_1 = ttk.Label(
            expenses_container, 
            text="No recent expenses", 
            font=config.Fonts.LABEL, 
            foreground=self.colors.TEXT_BROWN, 
            background=frame_bg,
            anchor='w'
        )
        recent_expense_1.pack(pady=2, fill=tk.X)  # Reduced from 3 to 2 for tighter spacing
        self.widgets['recent_expense_1'] = recent_expense_1
        
        recent_expense_2 = ttk.Label(
            expenses_container, 
            text="", 
            font=config.Fonts.LABEL, 
            foreground=self.colors.TEXT_BROWN, 
            background=frame_bg,
            anchor='w'
        )
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
        # Add Expense button: Always use #107c10 (same in both light and dark mode per PoC)
        # In light mode: GREEN_PRIMARY = #107c10
        # In dark mode: GREEN_BUTTON = #107c10 (explicitly set to match light mode)
        # Use GREEN_BUTTON if available (dark mode), otherwise GREEN_PRIMARY (light mode)
        if hasattr(self.colors, 'GREEN_BUTTON'):
            button_color = self.colors.GREEN_BUTTON  # Dark mode: #107c10
        else:
            button_color = self.colors.GREEN_PRIMARY  # Light mode: #107c10
        
        add_expense_btn = ctk.CTkButton(
            button_frame,
            text="+ Add Expense",
            command=self.tracker.add_expense,
            fg_color=button_color,
            hover_color=self.colors.GREEN_HOVER,
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
            fg_color=self.colors.BLUE_DARK_NAVY,  # Dark navy blue
            hover_color=self.colors.BLUE_NAVY,  # Lighter navy on hover
            text_color="white"  # Explicit text color for visibility
        )
        nav_button.grid(row=0, column=1, padx=(8, 0), sticky=(tk.W, tk.E))  # Reduced padx from 10 to 8
        
        # Configure button frame columns - original had weight=1 to allow expansion
        button_frame.columnconfigure(0, weight=1)  # Original: allow column 0 to expand
        button_frame.columnconfigure(1, weight=1)  # Original: allow column 1 to expand

