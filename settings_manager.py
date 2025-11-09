"""
Settings Manager Module for LiteFinPad

Provides centralized, thread-safe settings management with validation
and atomic write operations to prevent corruption.

All settings operations should go through this module to ensure:
- Consistent access patterns
- Validation before writing
- Atomic file operations (no partial writes)
- Thread-safe operations
- Easy debugging and logging
"""

import configparser
import os
import tempfile
import shutil
from typing import Any, Optional, Dict, List
from threading import Lock
from error_logger import log_info, log_warning, log_error


class SettingsManager:
    """
    Thread-safe settings manager with validation and atomic writes.
    
    Features:
    - Centralized settings access
    - Atomic file operations (write to temp, then rename)
    - Thread-safe with lock protection
    - Validation before writes
    - Default value support
    - Auto-creates missing sections
    """
    
    def __init__(self, settings_file: str = "settings.ini"):
        """
        Initialize settings manager.
        
        Args:
            settings_file: Path to settings INI file (default: settings.ini)
        """
        self.settings_file = settings_file
        self.config = configparser.ConfigParser()
        self._lock = Lock()  # Thread safety
        self._loaded = False
        
        # Load existing settings
        self.load()
    
    def load(self) -> bool:
        """
        Load settings from file.
        
        Returns:
            bool: True if loaded successfully, False otherwise
        """
        with self._lock:
            try:
                if os.path.exists(self.settings_file):
                    self.config.read(self.settings_file)
                    log_info(f"Settings loaded from {self.settings_file}")
                    self._loaded = True
                    return True
                else:
                    log_info(f"Settings file not found, will create on first save: {self.settings_file}")
                    self._loaded = True
                    return True
            except Exception as e:
                log_error(f"Failed to load settings from {self.settings_file}", e)
                # Initialize empty config on error
                self.config = configparser.ConfigParser()
                self._loaded = True
                return False
    
    def _save_unlocked(self) -> bool:
        """
        Internal save method without lock (assumes caller has lock).
        
        Returns:
            bool: True if saved successfully, False otherwise
        """
        try:
            # Create temp file in same directory as settings file
            settings_dir = os.path.dirname(self.settings_file) or '.'
            temp_fd, temp_path = tempfile.mkstemp(
                suffix='.tmp',
                prefix='settings_',
                dir=settings_dir,
                text=True
            )
            
            try:
                # Write to temp file
                with os.fdopen(temp_fd, 'w') as temp_file:
                    self.config.write(temp_file)
                
                # Verify temp file was written
                if not os.path.exists(temp_path):
                    raise IOError("Temp file was not created")
                
                # Atomic replace: rename temp file to actual settings file
                # On Windows, need to remove target first
                if os.path.exists(self.settings_file):
                    os.replace(temp_path, self.settings_file)
                else:
                    shutil.move(temp_path, self.settings_file)
                
                log_info(f"Settings saved atomically to {self.settings_file}")
                return True
                
            except Exception as e:
                # Clean up temp file on error
                if os.path.exists(temp_path):
                    os.remove(temp_path)
                raise e
                
        except Exception as e:
            log_error(f"Failed to save settings to {self.settings_file}", e)
            return False
    
    def save(self) -> bool:
        """
        Save settings to file using atomic write operation.
        
        Atomic write process:
        1. Write to temporary file
        2. Verify write succeeded
        3. Replace original file with temp file
        
        This ensures we never have a corrupted/partial settings file.
        
        Returns:
            bool: True if saved successfully, False otherwise
        """
        with self._lock:
            return self._save_unlocked()
    
    def get(self, section: str, key: str, default: Any = None, 
            value_type: type = str) -> Any:
        """
        Get a setting value with type conversion and default support.
        
        Args:
            section: Section name (e.g., "Export", "Logging")
            key: Key name (e.g., "default_location")
            default: Default value if key doesn't exist
            value_type: Type to convert to (str, int, float, bool)
            
        Returns:
            Setting value converted to specified type, or default if not found
            
        Example:
            >>> manager.get("Logging", "debug_mode", default=False, value_type=bool)
            False
        """
        with self._lock:
            try:
                if not self.config.has_section(section):
                    return default
                
                if not self.config.has_option(section, key):
                    return default
                
                value = self.config.get(section, key)
                
                # Type conversion
                if value_type == bool:
                    return value.lower() in ('true', '1', 'yes', 'on')
                elif value_type == int:
                    return int(value)
                elif value_type == float:
                    return float(value)
                else:
                    return value
                    
            except Exception as e:
                log_warning(f"Error reading setting [{section}].{key}: {e}")
                return default
    
    def set(self, section: str, key: str, value: Any, 
            auto_save: bool = True) -> bool:
        """
        Set a setting value with validation.
        
        Args:
            section: Section name
            key: Key name
            value: Value to set (will be converted to string)
            auto_save: Whether to save immediately (default: True)
            
        Returns:
            bool: True if set successfully
            
        Example:
            >>> manager.set("Export", "default_location", "C:\\Users\\Documents")
            True
        """
        with self._lock:
            try:
                # Validate inputs
                if not section or not key:
                    log_warning("Cannot set setting with empty section or key")
                    return False
                
                # Create section if it doesn't exist
                if not self.config.has_section(section):
                    self.config.add_section(section)
                
                # Convert value to string
                str_value = str(value).strip()
                
                # Set the value
                self.config.set(section, key, str_value)
                
                # Auto-save if requested (use unlocked version since we already have the lock)
                if auto_save:
                    return self._save_unlocked()
                
                return True
                
            except Exception as e:
                log_error(f"Failed to set [{section}].{key} = {value}", e)
                return False
    
    def delete(self, section: str, key: Optional[str] = None, 
               auto_save: bool = True) -> bool:
        """
        Delete a setting or entire section.
        
        Args:
            section: Section name
            key: Key name (if None, deletes entire section)
            auto_save: Whether to save immediately (default: True)
            
        Returns:
            bool: True if deleted successfully
            
        Example:
            >>> manager.delete("Export", "old_setting")  # Delete one key
            >>> manager.delete("OldSection")  # Delete entire section
        """
        with self._lock:
            try:
                if key is None:
                    # Delete entire section
                    if self.config.has_section(section):
                        self.config.remove_section(section)
                        log_info(f"Deleted section: [{section}]")
                else:
                    # Delete specific key
                    if self.config.has_section(section) and self.config.has_option(section, key):
                        self.config.remove_option(section, key)
                        log_info(f"Deleted setting: [{section}].{key}")
                
                # Auto-save if requested (use unlocked version since we already have the lock)
                if auto_save:
                    return self._save_unlocked()
                
                return True
                
            except Exception as e:
                log_error(f"Failed to delete [{section}].{key if key else '*'}", e)
                return False
    
    def get_section(self, section: str) -> Dict[str, str]:
        """
        Get all key-value pairs in a section.
        
        Args:
            section: Section name
            
        Returns:
            Dictionary of key-value pairs, empty dict if section doesn't exist
            
        Example:
            >>> export_settings = manager.get_section("Export")
            >>> print(export_settings)
            {'default_location': 'C:\\Users\\Documents', 'format': 'xlsx'}
        """
        with self._lock:
            try:
                if self.config.has_section(section):
                    return dict(self.config.items(section))
                return {}
            except Exception as e:
                log_warning(f"Error reading section [{section}]: {e}")
                return {}
    
    def get_all_sections(self) -> List[str]:
        """
        Get list of all section names.
        
        Returns:
            List of section names
        """
        with self._lock:
            return self.config.sections()
    
    def has_section(self, section: str) -> bool:
        """
        Check if a section exists.
        
        Args:
            section: Section name
            
        Returns:
            bool: True if section exists
        """
        with self._lock:
            return self.config.has_section(section)
    
    def has_key(self, section: str, key: str) -> bool:
        """
        Check if a key exists in a section.
        
        Args:
            section: Section name
            key: Key name
            
        Returns:
            bool: True if key exists
        """
        with self._lock:
            return (self.config.has_section(section) and 
                   self.config.has_option(section, key))
    
    def clear_all(self, auto_save: bool = True) -> bool:
        """
        Clear all settings (useful for reset/testing).
        
        Args:
            auto_save: Whether to save immediately (default: True)
            
        Returns:
            bool: True if cleared successfully
        """
        with self._lock:
            try:
                self.config = configparser.ConfigParser()
                log_info("All settings cleared")
                
                if auto_save:
                    return self.save()
                
                return True
                
            except Exception as e:
                log_error("Failed to clear settings", e)
                return False


# Singleton instance for global access
_settings_instance: Optional[SettingsManager] = None


def get_settings_manager(settings_file: str = "settings.ini") -> SettingsManager:
    """
    Get singleton instance of SettingsManager.
    
    Args:
        settings_file: Path to settings file (default: settings.ini)
        
    Returns:
        SettingsManager instance
        
    Example:
        >>> settings = get_settings_manager()
        >>> debug_mode = settings.get("Logging", "debug_mode", default=False, value_type=bool)
    """
    global _settings_instance
    
    if _settings_instance is None:
        _settings_instance = SettingsManager(settings_file)
    
    return _settings_instance

