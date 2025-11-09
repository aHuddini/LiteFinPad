"""
Archive Mode Manager - Handles visual styling and UI updates for Archive Mode

This module manages all archive mode-related functionality:
- UI styling transitions (normal ↔ archive)
- Window title and background updates
- Button state management (enable/disable add buttons)
- Recursive widget styling (ttk widgets)
- Context date calculation for analytics

Archive mode is activated when viewing past or future months.
"""

import tkinter as tk
from tkinter import ttk
from datetime import datetime
import calendar
import config
import customtkinter as ctk


class ArchiveModeManager:
    """
    Manages Archive Mode UI and behavior.
    
    Responsibilities:
    - Detect archive mode (viewing past/future month vs. current)
    - Apply/remove archive styling to entire UI
    - Update window title and backgrounds
    - Enable/disable add expense functionality
    - Provide context date for analytics
    """
    
    def __init__(self, root, expense_tracker, page_manager=None, 
                 main_frame=None, expense_list_frame=None,
                 main_container=None,
                 month_label=None, add_expense_btn=None, 
                 quick_add_helper=None, table_manager=None,
                 tooltip_creator=None,
                 update_display_callback=None,
                 update_metrics_callback=None):
        """
        Initialize the Archive Mode Manager.
        
        Args:
            root: Main Tkinter window
            expense_tracker: ExpenseTracker instance
            page_manager: PageManager instance for page detection
            main_frame: Main dashboard frame
            expense_list_frame: Expense list page frame
            month_label: Label showing current month
            add_expense_btn: "+ Add Expense" button
            quick_add_helper: QuickAddHelper instance
            table_manager: ExpenseTableManager instance
            tooltip_creator: Function to create tooltips (gui.create_tooltip)
            update_display_callback: Callback to update display (gui.update_display)
            update_metrics_callback: Callback to update metrics (gui.update_expense_metrics)
        """
        self.root = root
        self.expense_tracker = expense_tracker
        self.page_manager = page_manager
        self.main_frame = main_frame
        self.expense_list_frame = expense_list_frame
        self.main_container = main_container
        self.month_label = month_label
        self.add_expense_btn = add_expense_btn
        self.quick_add_helper = quick_add_helper
        self.table_manager = table_manager
        self.tooltip_creator = tooltip_creator
        self.update_display_callback = update_display_callback
        self.update_metrics_callback = update_metrics_callback
    
    def is_archive_mode(self):
        """
        Check if we're in archive mode (viewing a past/future month, not current month).
        
        Returns:
            bool: True if viewing past/future month, False if viewing current month
        """
        viewed_month = getattr(self.expense_tracker, 'viewed_month', None)
        if viewed_month is None:
            return False
        
        # Check if viewed month is the current month
        current_month_key = datetime.now().strftime('%Y-%m')
        return viewed_month != current_month_key
    
    def get_context_date(self):
        """
        Get the appropriate context date for analytics.
        
        Returns:
            datetime: Last day of viewed month (archive mode) or current date (normal mode)
        """
        if self.is_archive_mode():
            # Archive mode: use last day of viewed month
            viewed_month = self.expense_tracker.viewed_month
            year, month = map(int, viewed_month.split('-'))
            last_day = calendar.monthrange(year, month)[1]
            return datetime(year, month, last_day)
        else:
            # Normal mode (current month): use today's actual date
            return datetime.now()
    
    def refresh_ui(self):
        """
        Update UI styling based on viewing mode (current vs archive).
        
        This is the main method that orchestrates all archive mode UI updates:
        - Window title and background
        - Frame and widget styling
        - Button states and tooltips
        - Display data refresh
        """
        viewing_mode = self.expense_tracker.viewing_mode
        viewed_month = self.expense_tracker.viewed_month
        
        # Read version for window title
        try:
            with open('version.txt', 'r') as f:
                version = f.read().strip()
        except:
            version = "Unknown"  # Fallback if version.txt is missing
        
        # Format month for display using month_viewer's formatter
        # Use include_archive_indicator=False for month label (archive indicator is in window title)
        month_display_text = self.expense_tracker.month_viewer.format_month_display(
            viewed_month,
            include_archive_indicator=False
        )
        
        if viewing_mode == "archive":
            self._apply_archive_mode(version, month_display_text)
        else:
            self._apply_normal_mode(version, month_display_text)
        
        # Update display to show the correct data
        if self.update_display_callback:
            try:
                self.update_display_callback()
            except Exception as e:
                from error_logger import log_error
                log_error(f"Error calling update_display_callback: {e}", e)
        else:
            from error_logger import log_warning
            log_warning("update_display_callback is None - display will not update")
        
        # Update expense list if we're on that page
        if (self.page_manager and self.page_manager.is_on_page("expense_list") 
            and self.table_manager):
            self.table_manager.load_expenses(self.expense_tracker.expenses)
            if self.update_metrics_callback:
                self.update_metrics_callback()
    
    def _apply_archive_mode(self, version, month_display_text):
        """Apply archive mode styling to all UI elements."""
        # Format month name for window title (with archive indicator)
        month_obj = datetime.strptime(self.expense_tracker.viewed_month, "%Y-%m")
        month_name = month_obj.strftime('%B %Y')
        
        # Window title: Show archive mode
        self.root.title(f"LiteFinPad v{version} - 📚 Archive: {month_name}")
        
        # Background: Lavender tint
        self.root.configure(bg=config.Colors.BG_ARCHIVE_TINT)
        
        # Update main_container (outer frame) to archive style
        if self.main_container:
            if isinstance(self.main_container, ctk.CTkFrame):
                self.main_container.configure(fg_color=config.Colors.BG_ARCHIVE_TINT)
        
        # Switch main_frame to archive style
        if self.main_frame:
            # Check if it's a CustomTkinter widget or ttk widget
            # Use both isinstance and winfo_class for robust detection
            is_ctk_frame = isinstance(self.main_frame, ctk.CTkFrame) or hasattr(self.main_frame, 'fg_color')
            if is_ctk_frame:
                # CustomTkinter: use fg_color
                try:
                    self.main_frame.configure(fg_color=config.Colors.BG_ARCHIVE_TINT)
                except Exception as e:
                    from error_logger import log_error
                    log_error(f"Error configuring main_frame fg_color: {e}", e)
            else:
                # ttk widget: use style
                try:
                    self.main_frame.configure(style='Archive.TFrame')
                except Exception as e:
                    from error_logger import log_error
                    log_error(f"Error configuring main_frame style: {e}", e)
            self.apply_styles_to_widgets(self.main_frame, archive=True)
        
        # Also apply to expense list frame if it exists
        if self.expense_list_frame:
            # Check if it's a CustomTkinter widget or ttk widget
            # Use both isinstance and hasattr for robust detection
            is_ctk_frame = isinstance(self.expense_list_frame, ctk.CTkFrame) or hasattr(self.expense_list_frame, 'fg_color')
            if is_ctk_frame:
                # CustomTkinter: use fg_color
                try:
                    self.expense_list_frame.configure(fg_color=config.Colors.BG_ARCHIVE_TINT)
                except Exception as e:
                    from error_logger import log_error
                    log_error(f"Error configuring expense_list_frame fg_color: {e}", e)
            else:
                # ttk widget: use style
                try:
                    self.expense_list_frame.configure(style='Archive.TFrame')
                except Exception as e:
                    from error_logger import log_error
                    log_error(f"Error configuring expense_list_frame style: {e}", e)
            self.apply_styles_to_widgets(self.expense_list_frame, archive=True)
        
        # Month title: Update text and styling for CustomTkinter widget
        if self.month_label:
            # Update month label text with formatted display
            self.month_label.configure(text=month_display_text)
            # Keep month label transparent (inherits background from parent frame)
            # The parent frame will have the archive tint background
        
        # Apply archive styling to CustomTkinter widgets in main frame
        if self.main_frame:
            self.apply_customtkinter_styles(self.main_frame, archive=True)
        
        # Disable "+ Add Expense" button
        if self.add_expense_btn:
            # CustomTkinter buttons use configure() not config()
            if isinstance(self.add_expense_btn, ctk.CTkButton):
                self.add_expense_btn.configure(state='disabled')
            else:
                # ttk button fallback
                self.add_expense_btn.config(state='disabled')
            # Update button tooltip
            actual_month_name = self.expense_tracker.month_viewer.format_month_display(
                self.expense_tracker.current_month,
                include_archive_indicator=False
            )
            # Update tooltip using tooltip_manager's update method (properly unbinds old handlers)
            if self.tooltip_creator:
                # Use update method if available, otherwise create
                if hasattr(self.tooltip_creator, '__self__') and hasattr(self.tooltip_creator.__self__, 'update'):
                    # tooltip_creator is a method of TooltipManager, use update
                    self.tooltip_creator.__self__.update(
                        self.add_expense_btn,
                        f"Cannot add expenses in Archive mode. Switch to {actual_month_name}."
                    )
                else:
                    # Fallback: manually unbind and create
                    try:
                        self.add_expense_btn.unbind("<Enter>")
                        self.add_expense_btn.unbind("<Leave>")
                    except:
                        pass
                    if hasattr(self.add_expense_btn, 'tooltip'):
                        try:
                            self.add_expense_btn.tooltip.destroy()
                        except:
                            pass
                        delattr(self.add_expense_btn, 'tooltip')
                    self.tooltip_creator(
                        self.add_expense_btn,
                        f"Cannot add expenses in Archive mode. Switch to {actual_month_name}."
                    )
        
        # Disable Quick Add section (on expense list page)
        if self.quick_add_helper:
            actual_month_name = self.expense_tracker.month_viewer.format_month_display(
                self.expense_tracker.current_month,
                include_archive_indicator=False
            )
            self.quick_add_helper.set_enabled(
                False,
                tooltip_text=f"Cannot add expenses in Archive mode. Switch to {actual_month_name}."
            )
    
    def _apply_normal_mode(self, version, month_display_text):
        """Apply normal mode styling to all UI elements."""
        # Window title: Normal
        self.root.title(f"LiteFinPad v{version} - Monthly Expense Tracker")
        
        # Background: Light gray (normal)
        self.root.configure(bg=config.Colors.BG_LIGHT_GRAY)
        
        # Update main_container (outer frame) to normal style
        if self.main_container:
            if isinstance(self.main_container, ctk.CTkFrame):
                self.main_container.configure(fg_color=config.Colors.BG_LIGHT_GRAY)
        
        # Switch main_frame to normal style
        if self.main_frame:
            # Check if it's a CustomTkinter widget or ttk widget
            # Use both isinstance and hasattr for robust detection
            is_ctk_frame = isinstance(self.main_frame, ctk.CTkFrame) or hasattr(self.main_frame, 'fg_color')
            if is_ctk_frame:
                # CustomTkinter: use fg_color
                try:
                    self.main_frame.configure(fg_color=config.Colors.BG_LIGHT_GRAY)
                except Exception as e:
                    from error_logger import log_error
                    log_error(f"Error configuring main_frame fg_color: {e}", e)
            else:
                # ttk widget: use style
                try:
                    self.main_frame.configure(style='TFrame')
                except Exception as e:
                    from error_logger import log_error
                    log_error(f"Error configuring main_frame style: {e}", e)
            self.apply_styles_to_widgets(self.main_frame, archive=False)
        
        # Also apply to expense list frame if it exists
        if self.expense_list_frame:
            # Check if it's a CustomTkinter widget or ttk widget
            # Use both isinstance and hasattr for robust detection
            is_ctk_frame = isinstance(self.expense_list_frame, ctk.CTkFrame) or hasattr(self.expense_list_frame, 'fg_color')
            if is_ctk_frame:
                # CustomTkinter: use fg_color
                try:
                    self.expense_list_frame.configure(fg_color=config.Colors.BG_LIGHT_GRAY)
                except Exception as e:
                    from error_logger import log_error
                    log_error(f"Error configuring expense_list_frame fg_color: {e}", e)
            else:
                # ttk widget: use style
                try:
                    self.expense_list_frame.configure(style='TFrame')
                except Exception as e:
                    from error_logger import log_error
                    log_error(f"Error configuring expense_list_frame style: {e}", e)
            self.apply_styles_to_widgets(self.expense_list_frame, archive=False)
        
        # Month title: Update text and styling for CustomTkinter widget
        if self.month_label:
            # Update month label text with formatted display
            self.month_label.configure(text=month_display_text)
            # Keep month label transparent (inherits background from parent frame)
            # The parent frame will have the normal background
        
        # Apply normal styling to CustomTkinter widgets in main frame
        if self.main_frame:
            self.apply_customtkinter_styles(self.main_frame, archive=False)
        
        # Enable "+ Add Expense" button
        if self.add_expense_btn:
            # CustomTkinter buttons use configure() not config()
            if isinstance(self.add_expense_btn, ctk.CTkButton):
                self.add_expense_btn.configure(state='normal')
            else:
                # ttk button fallback
                self.add_expense_btn.config(state='normal')
            # Remove tooltip completely (button is self-explanatory in normal mode)
            # Use tooltip_manager's destroy method if available
            if hasattr(self.tooltip_creator, '__self__') and hasattr(self.tooltip_creator.__self__, 'destroy'):
                # tooltip_creator is a method of TooltipManager, use destroy
                self.tooltip_creator.__self__.destroy(self.add_expense_btn)
            else:
                # Fallback: manually unbind and destroy
                try:
                    self.add_expense_btn.unbind("<Enter>")
                    self.add_expense_btn.unbind("<Leave>")
                except:
                    pass
                if hasattr(self.add_expense_btn, 'tooltip'):
                    try:
                        self.add_expense_btn.tooltip.destroy()
                    except:
                        pass
                    delattr(self.add_expense_btn, 'tooltip')
        
        # Enable Quick Add section (on expense list page)
        if self.quick_add_helper:
            self.quick_add_helper.set_enabled(True)
    
    def apply_styles_to_widgets(self, parent, archive=True):
        """
        Recursively apply archive or normal styles to all ttk widgets.
        
        Args:
            parent: Parent widget to start from
            archive: True to apply archive styles, False for normal styles
        """
        prefix = 'Archive.' if archive else ''
        
        for widget in parent.winfo_children():
            widget_class = widget.winfo_class()
            
            # Update ttk.Label widgets
            if widget_class == 'TLabel':
                current_style = str(widget.cget('style'))
                # Strip any existing 'Archive.' prefix
                base_style = current_style.replace('Archive.', '')
                
                if base_style:
                    # Has a specific style (Title.TLabel, etc.) - add/remove Archive prefix
                    new_style = f"{prefix}{base_style}"
                else:
                    # No specific style - use default TLabel style
                    new_style = 'Archive.TLabel' if archive else 'TLabel'
                
                widget.configure(style=new_style)
            
            # Update ttk.Frame widgets
            elif widget_class == 'TFrame':
                widget.configure(style=f'{prefix}TFrame')
                # Recursively update children
                self.apply_styles_to_widgets(widget, archive)
            
            # Update ttk.LabelFrame widgets
            elif widget_class == 'TLabelframe':
                widget.configure(style=f'{prefix}TLabelframe')
                # Recursively update children
                self.apply_styles_to_widgets(widget, archive)
            
            # Recursively check other containers
            elif widget_class in ['Frame', 'Labelframe']:
                self.apply_styles_to_widgets(widget, archive)
    
    def apply_customtkinter_styles(self, parent, archive=True):
        """
        Recursively apply archive or normal styles to all CustomTkinter widgets.
        
        Args:
            parent: Parent widget to start from
            archive: True to apply archive styles, False for normal styles
        """
        bg_color = config.Colors.BG_ARCHIVE_TINT if archive else config.Colors.BG_LIGHT_GRAY
        
        try:
            children = parent.winfo_children()
        except (tk.TclError, AttributeError):
            # Parent widget doesn't support winfo_children or is destroyed
            return
        
        for widget in children:
            try:
                # Update CTkLabel widgets
                if isinstance(widget, ctk.CTkLabel):
                    try:
                        current_fg = widget.cget('fg_color')
                        # Update labels that use standard background colors
                        # Keep transparent labels transparent (they inherit from parent)
                        if current_fg == config.Colors.BG_LIGHT_GRAY or current_fg == config.Colors.BG_ARCHIVE_TINT:
                            widget.configure(fg_color=bg_color)
                        # For transparent labels, leave them transparent (parent provides background)
                    except (tk.TclError, AttributeError, RuntimeError):
                        # Widget might be destroyed or not fully initialized
                        pass
                
                # Update CTkFrame widgets
                elif isinstance(widget, ctk.CTkFrame):
                    try:
                        current_fg = widget.cget('fg_color')
                        # Update frames that use standard background colors
                        if current_fg == config.Colors.BG_LIGHT_GRAY or current_fg == config.Colors.BG_ARCHIVE_TINT:
                            widget.configure(fg_color=bg_color)
                        # Keep transparent frames transparent
                    except (tk.TclError, AttributeError, RuntimeError):
                        # Widget might be destroyed or not fully initialized
                        pass
                
                # Recursively check all containers (including non-CustomTkinter widgets)
                try:
                    self.apply_customtkinter_styles(widget, archive)
                except (tk.TclError, AttributeError, RuntimeError):
                    # Widget doesn't support winfo_children or is destroyed
                    pass
            except (tk.TclError, AttributeError, RuntimeError):
                # Widget might be destroyed during iteration
                continue

