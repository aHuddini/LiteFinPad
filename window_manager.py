"""
Window Manager Module
Handles main window lifecycle, positioning, animations, and event handling.
"""

import tkinter as tk
from error_logger import log_info, log_debug, log_error
import config
from window_animation import create_window_animator


class WindowManager:
    """
    Manages main window lifecycle, positioning, and animation.
    
    Responsibilities:
    - Show/hide window with animations
    - Position window on screen
    - Handle window events (unmap, map, destroy)
    - Manage stay-on-top functionality
    - Track window visibility state
    """
    
    def __init__(self, root, animator, gui, close_dialogs_callback, quit_callback):
        """
        Initialize the window manager.
        
        Args:
            root: Tkinter root window
            animator: WindowAnimator instance for slide animations
            gui: GUI instance for accessing stay_on_top_var and update methods
            close_dialogs_callback: Callback to close all open dialogs
            quit_callback: Callback to quit the application
        """
        self.root = root
        self.animator = animator
        self.gui = gui
        self.close_dialogs_callback = close_dialogs_callback
        self.quit_callback = quit_callback
        self.is_hidden = True  # Track if window is intentionally hidden
        
        # Cache screen dimensions and pre-calculate position (performance optimization)
        self._cached_screen_width = None
        self._cached_screen_height = None
        self._cached_window_x = None
        self._cached_window_y = None
        self._cache_screen_info()
        
        # Bind window events
        self._setup_event_handlers()
    
    def _cache_screen_info(self):
        """
        Cache screen dimensions and pre-calculate window position.
        Call this at init and when screen configuration changes.
        """
        try:
            # Cache screen dimensions (avoid repeated Tkinter queries)
            self._cached_screen_width = self.root.winfo_screenwidth()
            self._cached_screen_height = self.root.winfo_screenheight()
            
            # Pre-calculate window position (ready for instant show)
            window_width = config.Window.WIDTH
            window_height = config.Window.COMPACT_HEIGHT
            self._cached_window_x = self._cached_screen_width - window_width - config.Animation.SCREEN_MARGIN
            self._cached_window_y = self._cached_screen_height - window_height - 450
            
            log_debug(f"[WINDOW] Screen info cached: {self._cached_screen_width}x{self._cached_screen_height}, Position: ({self._cached_window_x}, {self._cached_window_y})")
        except (tk.TclError, AttributeError) as e:
            # Tkinter workaround: Screen dimension queries can fail on multi-monitor setups,
            # during display configuration changes, or when window is not yet fully initialized.
            # TclError: Tkinter window not yet initialized or destroyed
            # AttributeError: root object missing attributes
            log_error(f"[WINDOW] ERROR caching screen info (Tkinter error): {e}", e)
        except Exception as e:
            # Unexpected error - ensure window positioning doesn't crash
            log_error(f"[WINDOW] ERROR caching screen info (unexpected): {e}", e)
    
    def _setup_event_handlers(self):
        """Set up window event handlers"""
        self.root.bind("<Unmap>", self.on_window_unmap)
        self.root.bind("<Map>", self.on_window_map)
        self.root.bind("<Destroy>", self.on_window_destroy)
    
    def show_window(self):
        """Show the main window positioned near taskbar with slide animation"""
        try:
            log_info(f"[WINDOW] Showing window")
            log_debug(f"[WINDOW] Hidden state: {self.is_hidden}")
            
            # Use pre-calculated position (cached for instant response)
            window_width = config.Window.WIDTH
            window_height = config.Window.COMPACT_HEIGHT
            x = self._cached_window_x
            y = self._cached_window_y
            
            # Use the animator for smooth slide-in (IMMEDIATE - no delay)
            self.animator.slide_in(x, y, window_width, window_height)
            self.is_hidden = False
            
            # Refresh display AFTER animation starts (prevents startup delay)
            def update_display_async():
                try:
                    self.gui.update_recent_expenses()
                    self.gui.update_display()
                except (tk.TclError, AttributeError) as e:
                    # Tkinter workaround: GUI updates can fail if window is destroyed during
                    # animation, if widgets are not yet initialized, or during shutdown.
                    # TclError: Tkinter widgets destroyed
                    # AttributeError: Widget objects missing attributes
                    log_error(f"[WINDOW] ERROR updating display (Tkinter error): {e}", e)
                except RuntimeError as e:
                    # Tkinter main loop ended or window destroyed
                    log_error(f"[WINDOW] ERROR updating display (runtime error): {e}", e)
                except Exception as e:
                    # Unexpected error - prevent animation from crashing
                    log_error(f"[WINDOW] ERROR updating display (unexpected): {e}", e)
            
            # Schedule display update after animation begins (30ms delay)
            self.root.after(30, update_display_async)
            
            # Bring to front
            self.root.lift()
            self.root.focus_force()
            
            # Set topmost attribute based on stay_on_top setting
            self._apply_topmost_setting()
                
        except (tk.TclError, AttributeError) as e:
            # Tkinter workaround: Window operations can fail during shutdown, if window
            # is already destroyed, or during display configuration changes.
            # TclError: Tkinter window destroyed or not initialized
            # AttributeError: Window object missing attributes
            log_error(f"[WINDOW] ERROR in show_window (Tkinter error): {e}", e)
            print(f"Error showing window: {e}")
            # Fallback: just show the window
            self.root.deiconify()
        except RuntimeError as e:
            # Tkinter main loop ended
            log_error(f"[WINDOW] ERROR in show_window (runtime error): {e}", e)
            print(f"Error showing window: {e}")
            # Fallback: just show the window
            self.root.deiconify()
        except Exception as e:
            # Unexpected error - ensure window can still be shown
            log_error(f"[WINDOW] ERROR in show_window (unexpected): {e}", e)
            print(f"Error showing window: {e}")
            # Fallback: just show the window
            self.root.deiconify()
    
    def hide_window(self):
        """Hide window to system tray with slide animation"""
        try:
            log_info(f"[WINDOW] Hiding window")
            log_debug(f"[WINDOW] Hidden state: {self.is_hidden}")
            
            self.is_hidden = True
            
            # Refresh cached position while hiding (ready for next show)
            self._cache_screen_info()
            
            # Close all open dialogs first to prevent focus issues
            self.close_dialogs_callback()
            
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
            log_debug("[WINDOW] Using fallback withdraw()")
            self.root.withdraw()
            
        except (tk.TclError, AttributeError) as e:
            # Tkinter workaround: Window operations can fail during shutdown, if window
            # is already destroyed, or during display configuration changes.
            # TclError: Tkinter window destroyed or not initialized
            # AttributeError: Window object missing attributes
            log_error(f"[WINDOW] ERROR in hide_window (Tkinter error): {e}", e)
            print(f"Error in hide animation: {e}")
            # Fallback: just hide
            self.root.withdraw()
        except RuntimeError as e:
            # Tkinter main loop ended
            log_error(f"[WINDOW] ERROR in hide_window (runtime error): {e}", e)
            print(f"Error in hide animation: {e}")
            # Fallback: just hide
            self.root.withdraw()
        except Exception as e:
            # Unexpected error - ensure window can still be hidden
            log_error(f"[WINDOW] ERROR in hide_window (unexpected): {e}", e)
            print(f"Error in hide animation: {e}")
            # Fallback: just hide
            self.root.withdraw()
    
    def force_hide_window(self):
        """Force hide window without animation (for testing)"""
        self.close_dialogs_callback()
        self.root.withdraw()
    
    def recalculate_screen_info(self):
        """
        Recalculate screen info and position (call when screen config changes).
        Useful for multi-monitor setups or resolution changes.
        """
        log_info("[WINDOW] Recalculating screen info...")
        self._cache_screen_info()
    
    def toggle_stay_on_top(self):
        """
        Toggle stay on top functionality.
        Note: stay_on_top_var is guaranteed to exist after GUI initialization completes.
        """
        if self.gui.stay_on_top_var.get():
            self.root.attributes('-topmost', True)
        else:
            self.root.attributes('-topmost', False)
    
    def _apply_topmost_setting(self):
        """
        Apply topmost setting based on GUI preference.
        Note: stay_on_top_var is guaranteed to exist after GUI initialization completes.
        """
        if self.gui.stay_on_top_var.get():
            # Stay on top is enabled - keep window on top permanently
            log_debug("[WINDOW] Stay on top enabled")
            self.root.attributes('-topmost', True)
        else:
            # Stay on top is disabled - use temporary topmost to bring to front
            log_debug("[WINDOW] Using temporary topmost")
            self.root.attributes('-topmost', True)
            self.root.update()  # Force update to apply topmost
            self.root.attributes('-topmost', False)
    
    # Event Handlers
    
    def on_window_unmap(self, event):
        """Handle window unmapping (minimize or close)"""
        # Intentionally empty - protocol and toggle_window handle these
        pass
    
    def on_window_map(self, event):
        """Handle window mapping (restore from minimize)"""
        # Intentionally empty - for debugging if needed
        pass
    
    def on_window_destroy(self, event):
        """Handle window destroy event"""
        # Only trigger quit if the root window is being destroyed
        if event.widget == self.root:
            self.quit_callback()

