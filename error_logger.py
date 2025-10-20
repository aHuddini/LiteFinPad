#!/usr/bin/env python3
"""
Error logging system for LiteFinPad
"""

import logging
import os
from datetime import datetime
import configparser

class ErrorLogger:
    """Centralized error logging for LiteFinPad"""
    
    def __init__(self, log_file="error_log.txt"):
        self.log_file = log_file
        self.setup_logger()
    
    def _load_debug_setting(self):
        """
        Load debug mode setting from settings.ini
        
        Returns:
            logging level (INFO or DEBUG) based on settings.ini
        """
        config = configparser.ConfigParser()
        settings_file = 'settings.ini'
        
        # Default to INFO level
        log_level = logging.INFO
        
        if os.path.exists(settings_file):
            try:
                config.read(settings_file)
                debug_mode = config.getboolean('Logging', 'debug_mode', fallback=False)
                if debug_mode:
                    log_level = logging.DEBUG
            except Exception:
                # Silently fall back to INFO level if config reading fails
                pass
        
        return log_level
    
    def setup_logger(self):
        """Setup the logging configuration"""
        # Create logs directory if it doesn't exist
        os.makedirs("logs", exist_ok=True)
        log_path = os.path.join("logs", self.log_file)
        
        # Determine log level from settings.ini
        log_level = self._load_debug_setting()
        
        # Configure logging
        logging.basicConfig(
            level=log_level,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_path, mode='a', encoding='utf-8'),
                logging.StreamHandler()  # Also print to console
            ]
        )
        
        self.logger = logging.getLogger('LiteFinPad')
        
        # Set the logger and handlers to use the configured level
        self.logger.setLevel(log_level)
        for handler in self.logger.handlers:
            handler.setLevel(log_level)
        
        self.logger.info("=" * 50)
        self.logger.info("LiteFinPad Error Logger Started")
        if log_level == logging.DEBUG:
            self.logger.info("Debug mode ENABLED (via settings.ini)")
        else:
            self.logger.info("Normal logging mode (INFO level)")
        self.logger.info("=" * 50)
    
    def log_error(self, message, exception=None):
        """Log an error with optional exception details"""
        if exception:
            self.logger.error(f"{message}: {str(exception)}", exc_info=True)
        else:
            self.logger.error(message)
    
    def log_warning(self, message):
        """Log a warning"""
        self.logger.warning(message)
    
    def log_info(self, message):
        """Log an info message"""
        self.logger.info(message)
    
    def log_debug(self, message):
        """Log a debug message"""
        self.logger.debug(message)
    
    def log_tray_icon_error(self, step, error):
        """Log specific tray icon errors"""
        self.logger.error(f"Tray Icon Error in {step}: {str(error)}", exc_info=True)
    
    def log_application_start(self):
        """Log application startup"""
        self.logger.info("LiteFinPad Application Starting...")
    
    def log_encoding_error(self, error_details):
        """Log encoding-related errors with detailed diagnostics"""
        self.logger.error("=" * 50)
        self.logger.error("ENCODING ERROR DETECTED")
        self.logger.error("=" * 50)
        self.logger.error(f"Error: {error_details}")
        self.logger.error("This usually indicates missing Python modules in the build")
        self.logger.error("Check if _tcl_data folder exists in _internal directory")
        self.logger.error("=" * 50)
    
    def log_application_end(self):
        """Log application shutdown"""
        self.logger.info("LiteFinPad Application Shutting Down...")
    
    def log_export_attempt(self, format_type, expense_count):
        """Log export attempt"""
        self.logger.info(f"Export attempt started: Format={format_type}, Expenses={expense_count}")
    
    def log_export_success(self, format_type, filepath, expense_count):
        """Log successful export"""
        self.logger.info(f"Export successful: Format={format_type}, File={filepath}, Expenses={expense_count}")
    
    def log_export_error(self, format_type, error, step="unknown"):
        """Log export error with detailed information"""
        self.logger.error(f"Export failed at step '{step}': Format={format_type}, Error={str(error)}", exc_info=True)
    
    def log_library_check(self, library_name, available):
        """Log library availability check"""
        status = "AVAILABLE" if available else "MISSING"
        self.logger.debug(f"Library check: {library_name} = {status}")
    
    def log_data_load(self, data_type, count, source):
        """Log data loading"""
        self.logger.info(f"Data loaded: Type={data_type}, Count={count}, Source={source}")

# Global error logger instance
error_logger = ErrorLogger()

def log_error(message, exception=None):
    """Convenience function to log errors"""
    error_logger.log_error(message, exception)

def log_warning(message):
    """Convenience function to log warnings"""
    error_logger.log_warning(message)

def log_info(message):
    """Convenience function to log info"""
    error_logger.log_info(message)

def log_debug(message):
    """Convenience function to log debug"""
    error_logger.log_debug(message)

def log_export_attempt(format_type, expense_count):
    """Convenience function for export attempts"""
    error_logger.log_export_attempt(format_type, expense_count)

def log_export_success(format_type, filepath, expense_count):
    """Convenience function for export success"""
    error_logger.log_export_success(format_type, filepath, expense_count)

def log_export_error(format_type, error, step="unknown"):
    """Convenience function for export errors"""
    error_logger.log_export_error(format_type, error, step)

def log_library_check(library_name, available):
    """Convenience function for library checks"""
    error_logger.log_library_check(library_name, available)

def log_data_load(data_type, count, source):
    """Convenience function for data loading"""
    error_logger.log_data_load(data_type, count, source)
