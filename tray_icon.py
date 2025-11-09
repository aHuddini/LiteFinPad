#!/usr/bin/env python3
"""
Simple and minimalist system tray icon implementation for LiteFinPad
"""

import win32gui
import win32con
import win32api
import threading
import time
import sys
import os
import ctypes
from ctypes import wintypes
from error_logger import log_error, log_info, log_debug, log_warning
from functools import wraps

# Tray icon constants
NIM_ADD = 0x00000000
NIM_DELETE = 0x00000002
NIM_MODIFY = 0x00000001
NIF_ICON = 0x00000002
NIF_MESSAGE = 0x00000001
NIF_TIP = 0x00000004
WM_LBUTTONUP = 0x0202
WM_LBUTTONDBLCLK = 0x0203
WM_RBUTTONUP = 0x0205
WM_USER = 0x0400

# Win32 menu constants for context menu
MF_STRING = 0x00000000
MF_SEPARATOR = 0x00000800
TPM_LEFTALIGN = 0x0000
TPM_RETURNCMD = 0x0100

# Menu item IDs
ID_OPEN = 1001
ID_QUICK_ADD = 1002
ID_QUIT = 1003


def win32_safe(default_return=None, operation_name=""):
    """
    Decorator for Win32 API calls that handles common Win32 exceptions.
    
    Catches Win32-specific exceptions (WindowsError, OSError, AttributeError)
    and logs them appropriately, returning a default value instead of crashing.
    
    Args:
        default_return: Value to return on error (default: None)
        operation_name: Name of operation for logging (default: function name)
    
    Example:
        @win32_safe(default_return=False, operation_name="add to tray")
        def add_to_tray(self):
            # Win32 API calls here
            return True
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except (WindowsError, OSError) as e:
                # Win32 API error - file access, system calls, permissions
                op_name = operation_name or func.__name__
                log_error(f"Win32 API error in {op_name}: {e}", e)
                return default_return
            except AttributeError as e:
                # win32gui/win32api module issue - missing function or constant
                op_name = operation_name or func.__name__
                log_error(f"Win32 module error in {op_name}: {e}", e)
                return default_return
            except Exception as e:
                # Unexpected error - log but still return default
                op_name = operation_name or func.__name__
                log_warning(f"Unexpected error in {op_name}: {e}")
                return default_return
        return wrapper
    return decorator


# Define NOTIFYICONDATA structure using ctypes
class NOTIFYICONDATA(ctypes.Structure):
    _fields_ = [
        ('cbSize', wintypes.DWORD),
        ('hWnd', wintypes.HWND),
        ('uID', wintypes.UINT),
        ('uFlags', wintypes.UINT),
        ('uCallbackMessage', wintypes.UINT),
        ('hIcon', wintypes.HICON),
        ('szTip', wintypes.WCHAR * 128),
    ]

class TrayIcon:
    """
    Simple system tray icon implementation
    - Left single-click: Toggle application window (show/hide)
    - Left double-click: Quick add expense dialog
    - Right click: Context menu with Open, Quick Add, and Quit options
    """
    
    def __init__(self, tooltip="LiteFinPad", toggle_callback=None, quick_add_callback=None, quit_callback=None):
        self.tooltip = tooltip
        self.toggle_callback = toggle_callback
        self.quick_add_callback = quick_add_callback
        self.quit_callback = quit_callback
        self.hwnd = None
        self.icon_handle = None
        self.running = False
        self.thread = None
        self.callback_message = WM_USER + 20
        
        # Track double-click to suppress the first single-click in a double-click sequence
        self.last_click_time = 0
        self.double_click_window = 0.11  # 110ms - balanced for reliability and responsiveness
        self.pending_single_click_timer = None
        self.double_click_detected = False
        
        # Create window procedure that will handle messages
        self.wndproc = self._create_window_proc()
    
    def _create_window_proc(self):
        """Create a window procedure to handle messages"""
        # Store reference to self  
        tray_instance = self
        
        # Simple window procedure
        def window_proc(hwnd, msg, wparam, lparam):
            try:
                # Only handle tray-specific messages, let everything else pass through
                if msg == tray_instance.callback_message:
                    # Log mouse movements at DEBUG level to reduce noise (0x200 = WM_MOUSEMOVE)
                    if lparam == 0x200:
                        log_debug(f"[TRAY] Mouse move: lparam={lparam:x}")
                    else:
                        log_info(f"[TRAY] Window proc: tray message! lparam={lparam:x}, timestamp={time.time():.3f}")
                    
                    if lparam == WM_LBUTTONDBLCLK:
                        log_info("[TRAY] DOUBLE-CLICK detected in window proc")
                        # NOTE: Intermittent crash reported on 2025-10-19 (not reproducible)
                        # May be related to timing, dialog init, or focus management
                        # Monitor for patterns: quick successive clicks, focus states, etc.
                        tray_instance.on_double_click()
                        return 0
                    elif lparam == WM_LBUTTONUP:
                        log_debug("[TRAY] Left-click detected")
                        tray_instance.on_left_click()
                        return 0
                    elif lparam == WM_RBUTTONUP:
                        log_info("[TRAY] RIGHT-CLICK detected in window proc")
                        tray_instance.on_right_click()
                        log_info("[TRAY] on_right_click() returned successfully")
                        return 0
                # For all other messages, use default processing
                return win32gui.DefWindowProc(hwnd, msg, wparam, lparam)
            except Exception as e:
                # CRITICAL: Window procedure called by Windows OS directly.
                # Any unhandled exception here crashes the entire application.
                # Windows can send unexpected messages during shutdown, system events,
                # or multi-monitor changes that we can't predict. This broad exception
                # is a necessary safety net to prevent crashes.
                log_error(f"[TRAY] Window proc error: {e}")
                return 0
        
        return window_proc
        
    @win32_safe(default_return=False, operation_name="create window")
    def create_window(self):
        """Create a hidden window for the tray icon"""
        log_debug("Creating tray window...")
        
        # Use the correct window class - try different approaches
        window_class = None
        
        # Try different window class constants
        try:
            # Method 1: Use a standard window class
            window_class = win32con.WC_STATIC
        except AttributeError:
            try:
                # Method 2: Use a different approach
                window_class = "STATIC"
            except:
                # Method 3: Use a custom class name
                window_class = "LiteFinPadTrayClass"
        
        # Register window class with our custom window procedure
        try:
            wc = win32gui.WNDCLASS()
            wc.lpszClassName = "LiteFinPadTrayClass"
            wc.lpfnWndProc = self.wndproc  # Use our custom window procedure
            wc.hInstance = win32api.GetModuleHandle(None)
            win32gui.RegisterClass(wc)
            window_class = "LiteFinPadTrayClass"
            log_debug("Registered custom window class with custom wndproc")
        except (WindowsError, OSError) as e:
            # Win32 API error - class already registered or system error
            log_debug(f"Could not register custom class (Win32 error): {e}")
            # Fallback to STATIC
            window_class = "STATIC"
        except AttributeError as e:
            # win32gui module issue - missing function or constant
            log_debug(f"Could not register custom class (module error): {e}")
            # Fallback to STATIC
            window_class = "STATIC"
        except Exception as e:
            # Unexpected error - fallback to STATIC
            log_warning(f"Unexpected error registering window class: {e}")
            window_class = "STATIC"
        
        # Create the window
        self.hwnd = win32gui.CreateWindow(
            window_class,
            "LiteFinPadTray",
            0,  # No style
            0, 0, 0, 0,  # No position/size
            0,  # No parent
            0,  # No menu
            win32api.GetModuleHandle(None),
            None
        )
        
        if not self.hwnd:
            raise Exception("Failed to create window")
            
        log_info(f"Tray window created successfully: {self.hwnd}")
        return True
    
    def load_icon(self):
        """Load the custom icon from icon.ico file"""
        try:
            log_debug("Loading custom icon...")
            
            # Try to load icon.ico from the project directory
            import sys
            import os
            
            # Determine icon path (works for both dev and PyInstaller)
            if hasattr(sys, '_MEIPASS'):
                # Running as PyInstaller executable
                icon_path = os.path.join(sys._MEIPASS, 'icon.ico')
            else:
                # Running as Python script
                icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'icon.ico')
            
            log_debug(f"Looking for icon at: {icon_path}")
            
            # Try to load the custom icon
            if os.path.exists(icon_path):
                try:
                    self.icon_handle = win32gui.LoadImage(
                        0,  # hinst
                        icon_path,  # name
                        win32con.IMAGE_ICON,  # type
                        0,  # cx
                        0,  # cy
                        win32con.LR_LOADFROMFILE | win32con.LR_DEFAULTSIZE
                    )
                    if self.icon_handle:
                        log_info(f"Custom icon loaded successfully: {icon_path}")
                        return True
                except (WindowsError, OSError) as e:
                    # Win32 API file access error - file doesn't exist, permission denied, or invalid format
                    log_error(f"Failed to load custom icon (file error): {e}")
                except AttributeError as e:
                    # win32gui module issue - missing function or constant
                    log_error(f"Failed to load custom icon (module error): {e}")
                except Exception as e:
                    # Unexpected error - log but continue to fallback icon
                    log_warning(f"Unexpected error loading icon: {e}")
            else:
                log_debug(f"Icon file not found at {icon_path}, using default")
            
            # Fallback to Windows default icon
            log_debug("Using Windows default icon as fallback")
            self.icon_handle = win32gui.LoadIcon(0, win32con.IDI_APPLICATION)
            if not self.icon_handle:
                self.icon_handle = win32gui.LoadIcon(0, win32con.IDI_WINLOGO)
            
            if self.icon_handle:
                log_info(f"Icon loaded successfully: {self.icon_handle}")
                return True
            else:
                log_error("Failed to load any icon")
                return False
            
        except Exception as e:
            log_error("Error loading icon", e)
            return False
    
    @win32_safe(default_return=False, operation_name="add to tray")
    def add_to_tray(self):
        """Add icon to system tray"""
        if not self.hwnd or not self.icon_handle:
            log_error("Cannot add to tray: missing hwnd or icon_handle")
            return False
            
        log_debug(f"Adding icon to system tray... hwnd={self.hwnd}, icon={self.icon_handle}")
        
        # Create NOTIFYICONDATA structure using ctypes
        nid = NOTIFYICONDATA()
        nid.cbSize = ctypes.sizeof(NOTIFYICONDATA)
        nid.hWnd = self.hwnd
        nid.uID = 1
        nid.uFlags = NIF_ICON | NIF_MESSAGE | NIF_TIP
        nid.uCallbackMessage = WM_USER + 20
        nid.hIcon = self.icon_handle
        nid.szTip = self.tooltip
        
        self.callback_message = WM_USER + 20
        
        log_debug(f"NOTIFYICONDATA: hwnd={nid.hWnd}, id={nid.uID}, flags={nid.uFlags}, msg={nid.uCallbackMessage}")
        
        # Use ctypes to call Shell_NotifyIconW
        shell32 = ctypes.windll.shell32
        result = shell32.Shell_NotifyIconW(NIM_ADD, ctypes.byref(nid))
        
        log_debug(f"Shell_NotifyIconW result: {result}")
        
        if result:
            log_info("Icon added to system tray successfully")
            return True
        else:
            # Get last error
            error_code = ctypes.get_last_error()
            log_error(f"Failed to add icon to system tray - Shell_NotifyIconW returned {result}, error code: {error_code}")
            return False
    
    @win32_safe(default_return=False, operation_name="update tooltip")
    def update_tooltip(self, new_tooltip):
        """Update the tooltip text for the tray icon"""
        if not self.hwnd or not self.icon_handle:
            log_error("Cannot update tooltip: missing hwnd or icon_handle")
            return False
        
        # Update the stored tooltip
        self.tooltip = new_tooltip
        
        # Create NOTIFYICONDATA structure for modification
        nid = NOTIFYICONDATA()
        nid.cbSize = ctypes.sizeof(NOTIFYICONDATA)
        nid.hWnd = self.hwnd
        nid.uID = 1
        nid.uFlags = NIF_TIP
        nid.szTip = new_tooltip
        
        # Use ctypes to call Shell_NotifyIconW with NIM_MODIFY
        shell32 = ctypes.windll.shell32
        result = shell32.Shell_NotifyIconW(NIM_MODIFY, ctypes.byref(nid))
        
        if result:
            log_info(f"Tooltip updated successfully: {new_tooltip}")
            return True
        else:
            log_error(f"Failed to update tooltip - Shell_NotifyIconW returned {result}")
            return False
    
    @win32_safe(default_return=None, operation_name="remove from tray")
    def remove_from_tray(self):
        """Remove icon from system tray"""
        if not self.hwnd:
            return
            
        # Create NOTIFYICONDATA structure for deletion
        nid = NOTIFYICONDATA()
        nid.cbSize = ctypes.sizeof(NOTIFYICONDATA)
        nid.hWnd = self.hwnd
        nid.uID = 1
        
        shell32 = ctypes.windll.shell32
        shell32.Shell_NotifyIconW(NIM_DELETE, ctypes.byref(nid))
        log_debug("Icon removed from system tray")
    
    def message_loop(self):
        """Main message processing loop - processes all messages to catch close events"""
        try:
            log_info("Starting tray icon message loop...")
            log_debug(f"Window handle: {self.hwnd}")
            log_debug(f"Callback message: {self.callback_message}")
            self.running = True
            
            while self.running:
                try:
                    # Use GetMessage to get ALL messages (not just for our window)
                    # This allows us to catch close events from the main window
                    result, msg = win32gui.GetMessage(None, 0, 0)
                    
                    if result == 0:  # WM_QUIT
                        log_info("Received WM_QUIT")
                        break
                    elif result == -1:  # Error
                        log_error("GetMessage returned error")
                        break
                    else:
                        # Dispatch message to our window procedure
                        win32gui.TranslateMessage(msg)
                        win32gui.DispatchMessage(msg)
                            
                except Exception as e:
                    # CRITICAL: Message loop is the core of Windows event processing.
                    # Must continue running even if individual messages fail to prevent
                    # application freeze. System events can trigger unexpected exceptions
                    # that we can't predict. This is defensive programming for system-level code.
                    log_error("Error in message loop iteration", e)
                    time.sleep(0.1)
                    
        except Exception as e:
            log_error("Error in message loop", e)
        finally:
            log_info("Message loop ended")
    
    def on_left_click(self):
        """Handle left click on tray icon - toggles window (delayed to detect double-click)"""
        import threading
        
        log_debug(f"[TRAY] Left click detected (double-click flag: {self.double_click_detected})")
        
        # If double-click was just detected, ignore this click
        if self.double_click_detected:
            log_debug("[TRAY] Left-click ignored - double-click in progress")
            self.double_click_detected = False
            return
        
        # Cancel any pending single-click
        if self.pending_single_click_timer:
            self.pending_single_click_timer.cancel()
            self.pending_single_click_timer = None
        
        # Delay the single-click action to see if a double-click follows
        def execute_single_click():
            log_info(f"[TRAY] Single-click: toggling window")
            if self.toggle_callback:
                try:
                    self.toggle_callback()
                except Exception as e:
                    log_error(f"[TRAY] ERROR in toggle callback: {e}", e)
        
        self.pending_single_click_timer = threading.Timer(self.double_click_window, execute_single_click)
        self.pending_single_click_timer.start()
    
    def create_context_menu(self):
        """
        Create Win32 popup menu with app actions.
        
        Menu structure (top to bottom):
        - Open LiteFinPad
        - Quick Add Expense
        - (separator)
        - Quit
        
        Returns:
            Handle to the created popup menu
        """
        menu = win32gui.CreatePopupMenu()
        
        # Add menu items in natural order using AppendMenu (adds to end)
        win32gui.AppendMenu(menu, MF_STRING, ID_OPEN, "Open LiteFinPad")
        win32gui.AppendMenu(menu, MF_STRING, ID_QUICK_ADD, "Quick Add Expense")
        win32gui.AppendMenu(menu, MF_SEPARATOR, 0, "")  # Separator requires empty string, not None
        win32gui.AppendMenu(menu, MF_STRING, ID_QUIT, "Quit")
        
        log_debug("[TRAY] Context menu created with 3 items + separator")
        return menu
    
    @win32_safe(default_return=None, operation_name="show context menu")
    def show_context_menu(self):
        """
        Display context menu at cursor position.
        Thread-safe: Can be called from Win32 message loop thread.
        """
        # Get current cursor position
        pos = win32gui.GetCursorPos()
        log_debug(f"[TRAY] Showing context menu at position {pos}")
        
        # Create the menu
        menu = self.create_context_menu()
        
        # Set foreground window (required for menu to dismiss properly)
        win32gui.SetForegroundWindow(self.hwnd)
        
        # Display menu and get selected command ID
        # TPM_RETURNCMD makes TrackPopupMenu return the selected command ID
        cmd = win32gui.TrackPopupMenu(
            menu,
            TPM_LEFTALIGN | TPM_RETURNCMD,
            pos[0], pos[1],
            0,
            self.hwnd,
            None
        )
        
        # Handle user selection
        if cmd == ID_OPEN:
            log_info("[TRAY MENU] Open LiteFinPad selected")
            if self.toggle_callback:
                self.toggle_callback()
        elif cmd == ID_QUICK_ADD:
            log_info("[TRAY MENU] Quick Add Expense selected")
            if self.quick_add_callback:
                self.quick_add_callback()
        elif cmd == ID_QUIT:
            log_info("[TRAY MENU] Quit selected")
            if self.quit_callback:
                self.quit_callback()
        elif cmd == 0:
            log_debug("[TRAY MENU] Menu dismissed (no selection)")
        
        # Cleanup
        win32gui.DestroyMenu(menu)
        log_debug("[TRAY] Context menu destroyed")
    
    def on_right_click(self):
        """Handle right click on tray icon - show context menu"""
        log_info("[TRAY] Right-click: showing context menu")
        # Show Win32 context menu (thread-safe)
        self.show_context_menu()
    
    def on_double_click(self):
        """Handle double click on tray icon - opens quick add dialog"""
        log_info(f"[TRAY] Double-click: opening quick add")
        
        # Cancel any pending single-click action
        if self.pending_single_click_timer:
            self.pending_single_click_timer.cancel()
            self.pending_single_click_timer = None
        
        # Mark that double-click was detected to ignore subsequent single-clicks
        self.double_click_detected = True
        
        if self.quick_add_callback:
            try:
                self.quick_add_callback()
            except Exception as e:
                log_error(f"[TRAY] ERROR in quick_add callback: {e}", e)
    
    def start(self):
        """Start the tray icon"""
        try:
            log_info("Starting tray icon...")
            
            # Create window
            if not self.create_window():
                log_error("Failed to create window")
                return False
            
            # Load icon
            if not self.load_icon():
                log_error("Failed to load icon")
                return False
            
            # Add to tray
            if not self.add_to_tray():
                log_error("Failed to add to tray")
                return False
            
            # Start message loop in separate thread
            self.thread = threading.Thread(target=self.message_loop, daemon=True)
            self.thread.start()
            
            log_info("Tray icon started successfully")
            return True
            
        except Exception as e:
            log_error("Error starting tray icon", e)
            return False
    
    def stop(self):
        """Stop the tray icon"""
        try:
            log_debug("Stopping tray icon...")
            self.running = False
            
            # Remove from tray
            self.remove_from_tray()
            
            # Destroy window
            if self.hwnd:
                win32gui.DestroyWindow(self.hwnd)
                self.hwnd = None
            
            log_debug("Tray icon stopped")
            
        except Exception as e:
            log_error("Error stopping tray icon", e)
    
    def is_running(self):
        """Check if tray icon is running"""
        return self.running and self.thread and self.thread.is_alive()


def create_simple_tray_icon(toggle_callback, quick_add_callback=None, quit_callback=None, tooltip="LiteFinPad"):
    """
    Create a simple tray icon with minimal configuration
    
    Args:
        toggle_callback: Function to call when tray icon is clicked
        quick_add_callback: Function to call when tray icon is double-clicked (optional)
        quit_callback: Function to call when quitting (optional)
        tooltip: Tooltip text for the tray icon
    
    Returns:
        TrayIcon instance
    """
    tray = TrayIcon(tooltip, toggle_callback, quick_add_callback, quit_callback)
    return tray


# Example usage
if __name__ == "__main__":
    def toggle_app():
        print("Toggle app called!")
    
    def quit_app():
        print("Quit app called!")
        sys.exit(0)
    
    # Create and start tray icon
    tray = create_simple_tray_icon(toggle_app, quit_app, "LiteFinPad Test")
    
    if tray.start():
        print("Tray icon is running. Click it to test.")
        print("Press Ctrl+C to quit.")
        
        try:
            # Keep the main thread alive
            while tray.is_running():
                time.sleep(1)
        except KeyboardInterrupt:
            print("\nShutting down...")
            tray.stop()
    else:
        print("Failed to start tray icon")
