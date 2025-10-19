"""
Window Animation Module for LiteFinPad
Handles smooth slide-in and slide-out animations for the main window
"""

import tkinter as tk
import time


class WindowAnimator:
    """Handles window slide animations with proper rendering timing"""
    
    def __init__(self, root_window):
        self.root = root_window
        self.is_animating = False
        
    def slide_in(self, target_x, target_y, width, height, duration=200):
        """
        Show window with anti-flicker techniques (standard Windows behavior)
        
        Args:
            target_x: Final X position
            target_y: Final Y position  
            width: Window width
            height: Window height
            duration: Animation duration in milliseconds (unused - no animation)
        """
        if self.is_animating:
            return
            
        try:
            self.is_animating = True
            
            # Set final position directly
            self.root.geometry(f"{width}x{height}+{target_x}+{target_y}")
            
            # Anti-flicker technique: Start with transparent window
            self.root.attributes('-alpha', 0.0)
            
            # Show window (invisible initially)
            self.root.deiconify()
            self.root.lift()
            self.root.focus_force()
            
            # Force complete rendering while transparent
            self.root.update_idletasks()
            self.root.update()
            
            # Additional rendering passes to ensure all UI elements are ready
            for _ in range(3):
                self.root.update_idletasks()
                self.root.update()
            
            # Fade in to prevent white flash
            def fade_in():
                try:
                    # Gradually increase opacity to prevent white flash (5 steps, 50ms total)
                    for alpha in [0.2, 0.4, 0.6, 0.8, 1.0]:
                        self.root.attributes('-alpha', alpha)
                        self.root.update_idletasks()
                        self.root.after(10)  # 10ms delay between steps = 50ms total
                    self.is_animating = False
                except Exception as e:
                    print(f"Error in fade-in: {e}")
                    self.root.attributes('-alpha', 1.0)
                    self.is_animating = False
            
            # Start fade-in after a brief delay
            self.root.after(20, fade_in)
            
        except Exception as e:
            print(f"Error showing window: {e}")
            # Fallback: just position the window normally
            self.root.geometry(f"{width}x{height}+{target_x}+{target_y}")
            self.root.attributes('-alpha', 1.0)
            self.is_animating = False
    
    def slide_out(self, start_x, start_y, duration=200):
        """
        Animate window sliding out to the right (original direction)
        
        Args:
            start_x: Current X position
            start_y: Current Y position
            duration: Animation duration in milliseconds
        """
        if self.is_animating:
            return
            
        try:
            self.is_animating = True
            
            # Get screen dimensions
            screen_width = self.root.winfo_screenwidth()
            
            # End position (off-screen to the right)
            end_x = screen_width + 50
            
            # Calculate animation parameters (horizontal movement)
            total_distance = end_x - start_x
            
            # Time-based animation (not frame-based) - more reliable on Windows
            import time
            start_time = time.perf_counter()
            
            # === EASING FUNCTIONS ===
            # Try different ones by changing which function is used below
            
            # Ease-out-quad AGGRESSIVE (faster throughout, especially middle/end)
            # Modified to move more distance earlier and finish faster
            def ease_out_quad(t):
                # Apply stronger easing by using a power of 1.3 instead of 2
                # Lower power = less deceleration = more aggressive middle/end
                return 1 - pow(1 - t, 1.3)
            
            # Ease-out-cubic (VERY smooth, more gradual than quad)
            def ease_out_cubic(t):
                return 1 - (1 - t) ** 3
            
            # Ease-in-out-quad (balanced - smooth start and end)
            def ease_in_out_quad(t):
                if t < 0.5:
                    return 2 * t * t
                else:
                    return 1 - pow(-2 * t + 2, 2) / 2
            
            # Custom aggressive ease-in-out (faster acceleration, smooth deceleration)
            def ease_custom_aggressive(t):
                if t < 0.4:
                    # First 40%: Very aggressive cubic acceleration
                    return 3.125 * t * t * t
                else:
                    # Last 60%: Smooth quadratic deceleration
                    t_adjusted = (t - 0.4) / 0.6
                    return 0.5 + 0.5 * (1 - (1 - t_adjusted) * (1 - t_adjusted))
            
            # Linear (no easing - constant speed)
            def ease_linear(t):
                return t
            
            # Get current window size once
            current_geometry = self.root.geometry()
            size_part = current_geometry.split('+')[0]
            
            # Animation tracking
            frame_count = 0
            last_frame_time = start_time
            last_x = start_x
            
            # Import logger
            from error_logger import log_info
            log_info(f"[ANIMATION START] Duration={duration}ms, Distance={total_distance}px, Start X={start_x}px Y={start_y}px, End X={end_x}px")
            
            def animate_step():
                nonlocal frame_count, last_frame_time, last_x
                
                if not self.is_animating:
                    return
                
                # Calculate elapsed time
                current_time = time.perf_counter()
                elapsed = (current_time - start_time) * 1000  # Convert to ms
                frame_delta = (current_time - last_frame_time) * 1000  # Time since last frame
                last_frame_time = current_time
                
                # Calculate progress (0 to 1)
                progress = min(elapsed / duration, 1.0)
                
                if progress < 1.0:
                    # Apply easing (but ensure first frame starts at exact position)
                    if frame_count == 0:
                        # First frame: ensure we start at the exact starting position
                        eased_progress = 0.0
                        current_x = start_x
                    else:
                        eased_progress = ease_out_quad(progress)  # Try: ease_out_quad, ease_out_cubic, ease_in_out_quad, ease_custom_aggressive, ease_linear
                        current_x = start_x + (total_distance * eased_progress)
                    pixel_delta = current_x - last_x
                    
                    # Calculate fade-out opacity (fade during last 40% of animation)
                    # Starts fading at 60% progress, fully transparent at 100%
                    if progress > 0.6:
                        fade_progress = (progress - 0.6) / 0.4  # 0 to 1 over last 40%
                        opacity = 1.0 - (fade_progress * 0.7)  # Fade from 1.0 to 0.3
                    else:
                        opacity = 1.0
                    
                    # Log frame details
                    fps = 1000 / frame_delta if frame_delta > 0 else 0
                    log_info(f"[FRAME {frame_count:3d}] Elapsed={elapsed:6.2f}ms | Delta={frame_delta:5.2f}ms | FPS={fps:5.1f} | Progress={progress*100:5.1f}% | Eased={eased_progress*100:5.1f}% | X={int(current_x):4d}px Y={start_y}px | ΔX={pixel_delta:+.1f}px | Opacity={opacity:.2f}")
                    
                    # Update window position and opacity
                    self.root.geometry(f"{size_part}+{int(current_x)}+{start_y}")
                    self.root.attributes('-alpha', opacity)
                    
                    last_x = current_x
                    frame_count += 1
                    
                    # Schedule next frame with minimal delay for smooth pacing
                    # 1ms provides better frame timing than 0ms (which can cause batching)
                    self.root.after(1, animate_step)
                else:
                    # Animation complete, hide the window
                    total_time = (current_time - start_time) * 1000
                    avg_fps = frame_count / (total_time / 1000) if total_time > 0 else 0
                    log_info(f"[ANIMATION END] Total={total_time:.2f}ms | Frames={frame_count} | Avg FPS={avg_fps:.1f}")
                    self.root.withdraw()
                    self.is_animating = False
            
            # Start animation
            animate_step()
            
        except Exception as e:
            print(f"Error in slide-out animation: {e}")
            # Fallback: just hide the window
            self.root.withdraw()
            self.is_animating = False
    
    def stop_animation(self):
        """Stop any ongoing animation"""
        self.is_animating = False
    
    def is_animation_running(self):
        """Check if animation is currently running"""
        return self.is_animating


def create_window_animator(root_window):
    """
    Factory function to create a WindowAnimator instance
    
    Args:
        root_window: The Tkinter root window
        
    Returns:
        WindowAnimator instance
    """
    return WindowAnimator(root_window)
