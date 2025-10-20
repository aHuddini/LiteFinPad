"""
Data Manager Module

Handles all expense data persistence operations (loading/saving).
All functions are pure data operations with no UI dependencies.
"""

import json
import os
from datetime import datetime
from error_logger import log_error, log_info, log_warning, log_data_load


class ExpenseDataManager:
    """
    Pure data manager class for expense persistence.
    All methods are static - they don't modify state, just handle file I/O
    and data transformation. This separates data persistence from UI logic.
    """
    
    @staticmethod
    def load_expenses(expenses_file, data_folder, current_month):
        """
        Load expense data from JSON file.
        
        Args:
            expenses_file (str): Path to expenses JSON file
            data_folder (str): Path to data folder
            current_month (str): Current month string (YYYY-MM)
            
        Returns:
            tuple: (expenses_list, monthly_total)
                - expenses_list: List of expense dictionaries
                - monthly_total: Float, sum of non-future expenses
                
        Example:
            expenses, total = ExpenseDataManager.load_expenses(
                "data_2025-10/expenses.json",
                "data_2025-10",
                "2025-10"
            )
        """
        log_info(f"Loading data from: {expenses_file}")
        log_info(f"Data folder: {data_folder}")
        log_info(f"Current month: {current_month}")
        
        if os.path.exists(expenses_file):
            try:
                with open(expenses_file, 'r') as f:
                    data = json.load(f)
                    expenses = data.get('expenses', [])
                    
                    # Calculate monthly_total from expenses (excluding future dates)
                    monthly_total = ExpenseDataManager.calculate_monthly_total(expenses)
                    
                    log_data_load("expenses", len(expenses), expenses_file)
                    log_info(f"Monthly total calculated: ${monthly_total:.2f}")
                    
                    return expenses, monthly_total
                    
            except Exception as e:
                log_error(f"Error loading data from {expenses_file}", e)
                print(f"Error loading data: {e}")
                return [], 0.0
        else:
            log_warning(f"Expenses file not found: {expenses_file}")
            log_info(f"Current working directory: {os.getcwd()}")
            log_info(f"Files in current directory: {os.listdir('.')[:10]}")
            return [], 0.0
    
    @staticmethod
    def save_expenses(data_folder, expenses_file, expenses, monthly_total):
        """
        Save expense data to JSON file.
        
        Args:
            data_folder (str): Path to data folder
            expenses_file (str): Path to expenses JSON file
            expenses (list): List of expense dictionaries
            monthly_total (float): Current monthly total
            
        Returns:
            bool: True if save succeeded, False otherwise
            
        Example:
            success = ExpenseDataManager.save_expenses(
                "data_2025-10",
                "data_2025-10/expenses.json",
                [{"date": "2025-10-19", "amount": 100.0, "description": "Test"}],
                100.0
            )
        """
        # Create data folder if it doesn't exist
        os.makedirs(data_folder, exist_ok=True)
        
        # Prepare data structure
        data = {
            'expenses': expenses,
            'monthly_total': monthly_total
        }
        
        try:
            with open(expenses_file, 'w') as f:
                json.dump(data, f, indent=2)
            log_info(f"Data saved: {len(expenses)} expenses to {expenses_file}")
            return True
            
        except Exception as e:
            log_error(f"Error saving data to {expenses_file}", e)
            print(f"Error saving data: {e}")
            return False
    
    @staticmethod
    def calculate_monthly_total(expenses):
        """
        Calculate monthly total from expenses, excluding future expenses.
        
        This is useful when you want to show accurate totals that don't include
        pre-logged future expenses. For example, if today is Oct 19 and you have
        an expense logged for Oct 25, it won't be counted in the total yet.
        
        Args:
            expenses (list): List of expense dictionaries with 'date' and 'amount' keys
            
        Returns:
            float: Sum of all non-future expense amounts
            
        Example:
            expenses = [
                {"date": "2025-10-15", "amount": 100.0},  # Past - counted
                {"date": "2025-10-25", "amount": 50.0}    # Future - not counted
            ]
            total = ExpenseDataManager.calculate_monthly_total(expenses)
            # Returns: 100.0 (only past expenses)
        """
        today = datetime.now().date()
        
        total = sum(
            expense['amount'] for expense in expenses
            if datetime.strptime(expense['date'], '%Y-%m-%d').date() <= today
        )
        
        return total

