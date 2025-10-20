"""
Expense Analytics Module

Provides calculation and analysis functions for expense data.
All functions are pure (no side effects) and accept expense data as parameters.

This module centralizes all analytics-related calculations that were
previously scattered in main.py, making the codebase more modular and maintainable.
"""

from datetime import datetime, timedelta
import calendar
import json
import os


class ExpenseAnalytics:
    """
    Pure analytics class for expense calculations.
    
    All methods are static - they don't modify state, just perform calculations
    on the data passed to them. This makes testing easier and keeps the logic clean.
    """
    
    @staticmethod
    def calculate_day_progress(current_date=None):
        """
        Get current day progress in the month.
        
        Args:
            current_date (datetime, optional): Date to calculate from. Defaults to today.
            
        Returns:
            tuple: (current_day, total_days_in_month)
            
        Example:
            >>> calculate_day_progress()
            (19, 31)  # October 19th out of 31 days
        """
        if current_date is None:
            current_date = datetime.now()
        
        current_day = current_date.day
        total_days = calendar.monthrange(current_date.year, current_date.month)[1]
        
        return current_day, total_days
    
    @staticmethod
    def calculate_week_progress(current_date=None):
        """
        Get current week progress in the month with decimal precision.
        
        Args:
            current_date (datetime, optional): Date to calculate from. Defaults to today.
            
        Returns:
            tuple: (precise_week, total_weeks)
            
        Example:
            >>> calculate_week_progress()
            (2.7, 5)  # Week 2.7 out of 5 weeks
        """
        if current_date is None:
            current_date = datetime.now()
        
        current_day = current_date.day
        
        # Base week number (1 for days 1-7, 2 for days 8-14, etc.)
        base_week = ((current_day - 1) // 7) + 1
        
        # Position within the week (0-6 for the 7 days)
        day_in_week = (current_day - 1) % 7
        
        # Decimal component (0.0 for first day, 0.1 for second, ... 0.9 for last day)
        week_decimal = day_in_week / 10.0
        
        precise_week = base_week + week_decimal
        
        # Total weeks in month (estimate based on total days)
        total_days = calendar.monthrange(current_date.year, current_date.month)[1]
        total_weeks = (total_days // 7) + (1 if total_days % 7 > 0 else 0)
        
        return precise_week, total_weeks
    
    @staticmethod
    def calculate_daily_average(expenses, current_date=None):
        """
        Calculate average spending per day.
        Formula: (month total ÷ days elapsed)
        
        Args:
            expenses (list): List of expense dictionaries
            current_date (datetime, optional): Date to calculate from. Defaults to today.
            
        Returns:
            tuple: (average_per_day, days_elapsed)
        """
        if not expenses:
            return 0.0, 0
        
        if current_date is None:
            current_date = datetime.now()
        
        # Get current month's expenses (excluding future dates)
        month_start = current_date.replace(day=1)
        month_expenses = [
            e for e in expenses 
            if datetime.strptime(e['date'], '%Y-%m-%d') >= month_start
            and datetime.strptime(e['date'], '%Y-%m-%d').date() <= current_date.date()
        ]
        
        monthly_total = sum(e['amount'] for e in month_expenses)
        days_elapsed = current_date.day
        
        # Average per day = monthly total ÷ days elapsed
        avg_per_day = monthly_total / days_elapsed if days_elapsed > 0 else 0
        
        return avg_per_day, days_elapsed
    
    @staticmethod
    def calculate_weekly_average(expenses, current_date=None):
        """
        Calculate average spending per week.
        Formula: (month total ÷ weeks elapsed in month)
        
        Args:
            expenses (list): List of expense dictionaries
            current_date (datetime, optional): Date to calculate from. Defaults to today.
            
        Returns:
            tuple: (average_per_week, weeks_elapsed)
        """
        if not expenses:
            return 0.0, 0
        
        if current_date is None:
            current_date = datetime.now()
        
        # Get current month's expenses (excluding future dates)
        month_start = current_date.replace(day=1)
        month_expenses = [
            e for e in expenses 
            if datetime.strptime(e['date'], '%Y-%m-%d') >= month_start
            and datetime.strptime(e['date'], '%Y-%m-%d').date() <= current_date.date()
        ]
        
        monthly_total = sum(e['amount'] for e in month_expenses)
        
        # Calculate weeks elapsed: (current day - 1) ÷ 7 + 1
        # This gives us the week number we're in (1, 2, 3, 4, etc.)
        current_day = current_date.day
        weeks_elapsed = ((current_day - 1) // 7) + 1
        
        # Average per week = monthly total ÷ weeks elapsed
        avg_per_week = monthly_total / weeks_elapsed if weeks_elapsed > 0 else 0
        
        return avg_per_week, weeks_elapsed
    
    @staticmethod
    def calculate_weekly_pace(expenses, current_date=None):
        """
        Calculate current week's spending pace.
        Formula: (this week's total ÷ days elapsed this week)
        
        Args:
            expenses (list): List of expense dictionaries
            current_date (datetime, optional): Date to calculate from. Defaults to today.
            
        Returns:
            tuple: (pace_per_day, days_elapsed_this_week)
        """
        if not expenses:
            return 0.0, 0
        
        if current_date is None:
            current_date = datetime.now()
        
        # Get current week's expenses (Monday to today, excluding future dates)
        week_start = current_date - timedelta(days=current_date.weekday())  # Monday of current week
        week_expenses = [
            e for e in expenses 
            if datetime.strptime(e['date'], '%Y-%m-%d').date() >= week_start.date()
            and datetime.strptime(e['date'], '%Y-%m-%d').date() <= current_date.date()
        ]
        
        weekly_total = sum(e['amount'] for e in week_expenses)
        days_elapsed = (current_date - week_start).days + 1  # Days from Monday to today (inclusive)
        
        # Pace = weekly total ÷ days elapsed in current week
        pace_per_day = weekly_total / days_elapsed if days_elapsed > 0 else 0
        
        # Return pace and days for context
        return pace_per_day, days_elapsed
    
    @staticmethod
    def calculate_monthly_trend(prev_month_data_folder):
        """
        Get previous month's total and name for comparison.
        
        Args:
            prev_month_data_folder (str): Folder path for previous month's data
            
        Returns:
            tuple: (prev_total_formatted, prev_month_name)
            
        Example:
            >>> calculate_monthly_trend("data_2025-09")
            ("$4,523.50", "September 2025")
        """
        # Get previous month date and name
        prev_month_date = datetime.now().replace(day=1) - timedelta(days=1)
        prev_month_key = prev_month_date.strftime('%Y-%m')
        prev_month_name = prev_month_date.strftime('%B %Y')  # e.g., "September 2025"
        
        # Check if we have previous month data file
        prev_expenses_file = os.path.join(prev_month_data_folder, 'expenses.json')
        
        if os.path.exists(prev_expenses_file):
            try:
                with open(prev_expenses_file, 'r') as f:
                    data = json.load(f)
                    # Handle both old format (list) and new format (dict with 'expenses' key)
                    if isinstance(data, list):
                        prev_expenses = data
                    elif isinstance(data, dict):
                        prev_expenses = data.get('expenses', [])
                    else:
                        prev_expenses = []
                    
                    prev_total = sum(e['amount'] for e in prev_expenses)
                    return f"${prev_total:.2f}", prev_month_name
            except Exception:
                # If error reading file, return $0.00
                return "$0.00", prev_month_name
        else:
            return "$0.00", prev_month_name
    
    @staticmethod
    def calculate_median_expense(expenses, current_date=None):
        """
        Calculate median expense amount (typical expense size).
        
        Args:
            expenses (list): List of expense dictionaries
            current_date (datetime, optional): Date to calculate from. Defaults to today.
            
        Returns:
            tuple: (median_amount, count)
        """
        if current_date is None:
            current_date = datetime.now()
        
        # Filter out future expenses
        past_expenses = [
            e for e in expenses 
            if datetime.strptime(e['date'], '%Y-%m-%d').date() <= current_date.date()
        ]
        
        if not past_expenses:
            return 0.0, 0
        
        # Get all expense amounts and sort them
        amounts = sorted([e['amount'] for e in past_expenses])
        count = len(amounts)
        
        # Calculate median
        if count % 2 == 0:
            # Even number: average of two middle values
            median = (amounts[count // 2 - 1] + amounts[count // 2]) / 2
        else:
            # Odd number: middle value
            median = amounts[count // 2]
        
        return median, count
    
    @staticmethod
    def calculate_largest_expense(expenses, current_date=None):
        """
        Get the largest expense amount and description.
        
        Args:
            expenses (list): List of expense dictionaries
            current_date (datetime, optional): Date to calculate from. Defaults to today.
            
        Returns:
            tuple: (amount, description)
        """
        if current_date is None:
            current_date = datetime.now()
        
        # Filter out future expenses
        past_expenses = [
            e for e in expenses 
            if datetime.strptime(e['date'], '%Y-%m-%d').date() <= current_date.date()
        ]
        
        if not past_expenses:
            return 0.0, "No expenses"
        
        # Find the largest expense
        largest = max(past_expenses, key=lambda e: e['amount'])
        
        return largest['amount'], largest['description']

