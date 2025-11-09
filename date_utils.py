"""
Date Utilities Module for LiteFinPad

Provides centralized date handling functions to eliminate duplication
and ensure consistent date formatting across the application.

All dates use ISO 8601 format (YYYY-MM-DD) internally.
"""

from datetime import datetime, timedelta
from calendar import monthrange
from typing import Optional, Tuple


class DateUtils:
    """Static utility methods for date operations"""
    
    # Standard date format used throughout the application
    DATE_FORMAT = "%Y-%m-%d"
    MONTH_FORMAT = "%Y-%m"
    DISPLAY_FORMAT = "%B %Y"  # e.g., "October 2025"
    
    @staticmethod
    def parse_date(date_str: str) -> Optional[datetime]:
        """
        Parse a date string into a datetime object.
        
        Args:
            date_str: Date string in YYYY-MM-DD format
            
        Returns:
            datetime object if valid, None if invalid
            
        Example:
            >>> DateUtils.parse_date("2025-10-27")
            datetime(2025, 10, 27)
        """
        try:
            return datetime.strptime(date_str, DateUtils.DATE_FORMAT)
        except (ValueError, TypeError):
            return None
    
    @staticmethod
    def is_valid_date(date_str: str) -> bool:
        """
        Check if a date string is valid.
        
        Args:
            date_str: Date string to validate
            
        Returns:
            True if valid, False otherwise
            
        Example:
            >>> DateUtils.is_valid_date("2025-10-27")
            True
            >>> DateUtils.is_valid_date("2025-13-01")
            False
        """
        return DateUtils.parse_date(date_str) is not None
    
    @staticmethod
    def format_date(dt: datetime) -> str:
        """
        Format a datetime object as YYYY-MM-DD string.
        
        Args:
            dt: datetime object to format
            
        Returns:
            Date string in YYYY-MM-DD format
            
        Example:
            >>> DateUtils.format_date(datetime(2025, 10, 27))
            "2025-10-27"
        """
        return dt.strftime(DateUtils.DATE_FORMAT)
    
    @staticmethod
    def get_current_date_str() -> str:
        """
        Get current date as YYYY-MM-DD string.
        
        Returns:
            Current date string
            
        Example:
            >>> DateUtils.get_current_date_str()
            "2025-10-27"
        """
        return datetime.now().strftime(DateUtils.DATE_FORMAT)
    
    @staticmethod
    def get_current_month_str() -> str:
        """
        Get current month as YYYY-MM string.
        
        Returns:
            Current month string
            
        Example:
            >>> DateUtils.get_current_month_str()
            "2025-10"
        """
        return datetime.now().strftime(DateUtils.MONTH_FORMAT)
    
    @staticmethod
    def get_month_folder_name(dt: datetime) -> str:
        """
        Get the data folder name for a given date.
        
        Args:
            dt: datetime object
            
        Returns:
            Folder name in format "data_YYYY-MM"
            
        Example:
            >>> DateUtils.get_month_folder_name(datetime(2025, 10, 27))
            "data_2025-10"
        """
        return f"data_{dt.strftime(DateUtils.MONTH_FORMAT)}"
    
    @staticmethod
    def get_month_folder_from_string(date_str: str) -> Optional[str]:
        """
        Get the data folder name from a date string.
        
        Args:
            date_str: Date string in YYYY-MM-DD format
            
        Returns:
            Folder name if valid date, None otherwise
            
        Example:
            >>> DateUtils.get_month_folder_from_string("2025-10-27")
            "data_2025-10"
        """
        dt = DateUtils.parse_date(date_str)
        if dt:
            return DateUtils.get_month_folder_name(dt)
        return None
    
    @staticmethod
    def parse_month_folder_name(folder_name: str) -> Optional[Tuple[int, int]]:
        """
        Parse a month folder name into (year, month) tuple.
        
        Args:
            folder_name: Folder name in format "data_YYYY-MM"
            
        Returns:
            (year, month) tuple if valid, None otherwise
            
        Example:
            >>> DateUtils.parse_month_folder_name("data_2025-10")
            (2025, 10)
        """
        try:
            if folder_name.startswith("data_"):
                month_str = folder_name[5:]  # Remove "data_" prefix
                year, month = map(int, month_str.split('-'))
                if 1 <= month <= 12:
                    return (year, month)
        except (ValueError, AttributeError):
            pass
        return None
    
    @staticmethod
    def get_previous_month(dt: datetime) -> datetime:
        """
        Get the previous month from a given date.
        
        Args:
            dt: datetime object
            
        Returns:
            datetime object for the first day of previous month
            
        Example:
            >>> DateUtils.get_previous_month(datetime(2025, 10, 27))
            datetime(2025, 9, 1)
            >>> DateUtils.get_previous_month(datetime(2025, 1, 15))
            datetime(2024, 12, 1)
        """
        # Go to first day of current month, then subtract one day
        first_of_month = dt.replace(day=1)
        last_of_prev_month = first_of_month - timedelta(days=1)
        return last_of_prev_month.replace(day=1)
    
    @staticmethod
    def get_next_month(dt: datetime) -> datetime:
        """
        Get the next month from a given date.
        
        Args:
            dt: datetime object
            
        Returns:
            datetime object for the first day of next month
            
        Example:
            >>> DateUtils.get_next_month(datetime(2025, 10, 27))
            datetime(2025, 11, 1)
            >>> DateUtils.get_next_month(datetime(2025, 12, 15))
            datetime(2026, 1, 1)
        """
        # Get the last day of current month, then add one day
        last_day = monthrange(dt.year, dt.month)[1]
        last_of_month = dt.replace(day=last_day)
        first_of_next = last_of_month + timedelta(days=1)
        return first_of_next
    
    @staticmethod
    def format_month_display(dt: datetime) -> str:
        """
        Format a datetime as a display-friendly month name.
        
        Args:
            dt: datetime object
            
        Returns:
            Month string in format "October 2025"
            
        Example:
            >>> DateUtils.format_month_display(datetime(2025, 10, 27))
            "October 2025"
        """
        return dt.strftime(DateUtils.DISPLAY_FORMAT)
    
    @staticmethod
    def get_month_name(month: int) -> str:
        """
        Get the full name of a month from its number.
        
        Args:
            month: Month number (1-12)
            
        Returns:
            Month name (e.g., "January", "February")
            
        Example:
            >>> DateUtils.get_month_name(10)
            "October"
        """
        try:
            dt = datetime(2000, month, 1)  # Use year 2000 as dummy
            return dt.strftime("%B")
        except ValueError:
            return ""
    
    @staticmethod
    def get_first_day_of_month(year: int, month: int) -> str:
        """
        Get the first day of a given month as a date string.
        
        Args:
            year: Year
            month: Month (1-12)
            
        Returns:
            Date string for first day of month
            
        Example:
            >>> DateUtils.get_first_day_of_month(2025, 10)
            "2025-10-01"
        """
        dt = datetime(year, month, 1)
        return DateUtils.format_date(dt)
    
    @staticmethod
    def get_last_day_of_month(year: int, month: int) -> str:
        """
        Get the last day of a given month as a date string.
        
        Args:
            year: Year
            month: Month (1-12)
            
        Returns:
            Date string for last day of month
            
        Example:
            >>> DateUtils.get_last_day_of_month(2025, 10)
            "2025-10-31"
            >>> DateUtils.get_last_day_of_month(2025, 2)
            "2025-02-28"
        """
        last_day = monthrange(year, month)[1]
        dt = datetime(year, month, last_day)
        return DateUtils.format_date(dt)
    
    @staticmethod
    def extract_year_month(date_str: str) -> Optional[Tuple[int, int]]:
        """
        Extract (year, month) tuple from a date string.
        
        Args:
            date_str: Date string in YYYY-MM-DD format
            
        Returns:
            (year, month) tuple if valid, None otherwise
            
        Example:
            >>> DateUtils.extract_year_month("2025-10-27")
            (2025, 10)
        """
        dt = DateUtils.parse_date(date_str)
        if dt:
            return (dt.year, dt.month)
        return None

