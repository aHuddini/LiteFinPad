"""
Input Validation Module

Provides input validation functions for expense tracker.
All functions are pure (no side effects) - just validation logic.
"""

from typing import Any, Optional


class ValidationResult:
    """
    Structured validation result object.
    
    Replaces tuple returns with a rich object that includes:
    - Validation status (pass/fail)
    - Error message (if failed)
    - Sanitized value (if passed)
    - Field name (for focus management)
    
    Benefits over tuple (bool, str):
    - More readable: result.is_valid vs result[0]
    - Works in boolean context: if not result
    - Includes field name for auto-focusing on error
    - Stores cleaned value when valid
    
    Example:
        >>> result = ValidationResult.success(123.45, "amount")
        >>> if result:  # Works in boolean context
        ...     print(f"Valid: {result.sanitized_value}")
        
        >>> result = ValidationResult.error("Amount required", "amount")
        >>> if not result:
        ...     print(result.error_message)  # "Amount required"
    """
    
    def __init__(self, is_valid: bool, error_message: str = "", 
                 sanitized_value: Any = None, error_field: str = ""):
        """
        Initialize validation result.
        
        Args:
            is_valid: Whether validation passed
            error_message: Human-readable error message (if failed)
            sanitized_value: Cleaned/formatted value (if valid)
            error_field: Which field had the error (for focus management)
        """
        self.is_valid = is_valid
        self.error_message = error_message
        self.sanitized_value = sanitized_value
        self.error_field = error_field
    
    def __bool__(self):
        """Allow using result in boolean context (if result:)"""
        return self.is_valid
    
    def __repr__(self):
        """String representation for debugging"""
        if self.is_valid:
            return f"ValidationResult(valid, value={self.sanitized_value})"
        else:
            return f"ValidationResult(invalid, error='{self.error_message}', field='{self.error_field}')"
    
    @staticmethod
    def success(value: Any, field: str = ""):
        """
        Create a successful validation result.
        
        Args:
            value: The validated/sanitized value
            field: Field name (optional)
            
        Returns:
            ValidationResult with is_valid=True
        """
        return ValidationResult(True, "", value, field)
    
    @staticmethod
    def error(message: str, field: str = ""):
        """
        Create a failed validation result.
        
        Args:
            message: Error message to show user
            field: Field name that failed (for focus management)
            
        Returns:
            ValidationResult with is_valid=False
        """
        return ValidationResult(False, message, None, field)


class InputValidation:
    """
    Pure validation class for user input.
    All methods are static - they don't modify state, just validate input.
    This centralizes validation logic for reuse across all dialogs and forms.
    """
    
    @staticmethod
    def validate_amount(new_value):
        """
        Validate currency amount input in real-time.
        
        Used for tkinter Entry validation (validatecommand).
        Allows user to type valid currency amounts only.
        
        Rules:
        - Only digits and one decimal point allowed
        - Maximum 2 decimal places
        - No upper limit on value
        - Can be empty (user hasn't typed yet)
        - Prevents invalid characters from being typed
        
        Args:
            new_value (str): The proposed new value for the Entry field
            
        Returns:
            bool: True if input is valid, False if it should be rejected
            
        Examples:
            >>> InputValidation.validate_amount("")
            True  # Allow empty field
            
            >>> InputValidation.validate_amount("123")
            True  # Valid whole number
            
            >>> InputValidation.validate_amount("123.45")
            True  # Valid with 2 decimals
            
            >>> InputValidation.validate_amount("123.456")
            False  # Too many decimals
            
            >>> InputValidation.validate_amount("abc")
            False  # Invalid characters
            
            >>> InputValidation.validate_amount("12.34.56")
            False  # Multiple decimal points
            
        Usage in tkinter:
            amount_var = tk.StringVar()
            validate_cmd = root.register(InputValidation.validate_amount)
            entry = ttk.Entry(
                parent,
                textvariable=amount_var,
                validate='key',
                validatecommand=(validate_cmd, '%P')
            )
        """
        # Allow empty field (user hasn't typed anything yet)
        if new_value == "":
            return True
        
        # Check if it only contains digits and at most one decimal point
        if not all(c.isdigit() or c == '.' for c in new_value):
            return False
        
        # Check for only one decimal point
        if new_value.count('.') > 1:
            return False
        
        # Check decimal places (maximum 2)
        if '.' in new_value:
            parts = new_value.split('.')
            # Check if there's a decimal part and if it's too long
            if len(parts) > 1 and len(parts[1]) > 2:
                return False
        
        # Check if it's a valid number format (handles edge cases)
        try:
            # Don't validate lone decimal point (user is still typing)
            if new_value != '.':
                float(new_value)
        except ValueError:
            return False
        
        return True
    
    @staticmethod
    def validate_final_amount(value_str):
        """
        Validate a final amount value before submission.
        
        Used when validating form submission (not real-time).
        More strict than validate_amount() - requires complete, valid number.
        
        Rules:
        - Must not be empty
        - Must be a valid float
        - Must be positive
        - Must be within reasonable range
        - Rounds to 2 decimal places
        
        Args:
            value_str (str): The amount string to validate
            
        Returns:
            ValidationResult: Result object with validation status
                - If valid: result.sanitized_value contains the cleaned float
                - If invalid: result.error_message contains user-friendly error
                - result.error_field is set to "amount" for focus management
            
        Examples:
            >>> result = InputValidation.validate_final_amount("123.45")
            >>> result.is_valid
            True
            >>> result.sanitized_value
            123.45
            
            >>> result = InputValidation.validate_final_amount("")
            >>> result.is_valid
            False
            >>> result.error_message
            'Amount is required'
            
            >>> result = InputValidation.validate_final_amount("0")
            >>> result.error_message
            'Amount must be greater than 0'
            
        Usage:
            result = InputValidation.validate_final_amount(amount_var.get())
            if not result:
                show_error(result.error_message)
                focus_on(result.error_field)  # Auto-focus amount field
                return
            amount = result.sanitized_value  # Get cleaned value
        """
        # Check if empty
        if not value_str or value_str.strip() == "":
            return ValidationResult.error("Amount is required", "amount")
        
        # Check if valid number
        try:
            amount = float(value_str.strip())
        except ValueError:
            return ValidationResult.error("Amount must be a valid number", "amount")
        
        # Check if positive
        if amount <= 0:
            return ValidationResult.error("Amount must be greater than 0", "amount")
        
        # Check if within reasonable range (less than 10 million)
        if amount >= 10000000:
            return ValidationResult.error("Amount is too large (max: $9,999,999.99)", "amount")
        
        # Round to 2 decimal places for currency
        amount_rounded = round(amount, 2)
        
        return ValidationResult.success(amount_rounded, "amount")
    
    @staticmethod
    def validate_description(value_str, max_length=100):
        """
        Validate expense description.
        
        Used when validating form submission.
        Ensures description meets minimum requirements.
        
        Rules:
        - Must not be empty or whitespace only
        - Must not exceed maximum length
        - Strips leading/trailing whitespace
        - Can contain any characters (no restriction)
        
        Args:
            value_str (str): The description string to validate
            max_length (int): Maximum allowed length (default: 100)
            
        Returns:
            ValidationResult: Result object with validation status
                - If valid: result.sanitized_value contains stripped description
                - If invalid: result.error_message contains user-friendly error
                - result.error_field is set to "description" for focus management
            
        Examples:
            >>> result = InputValidation.validate_description("Groceries")
            >>> result.is_valid
            True
            >>> result.sanitized_value
            'Groceries'
            
            >>> result = InputValidation.validate_description("")
            >>> result.error_message
            'Description is required'
            
            >>> result = InputValidation.validate_description("   ")
            >>> result.error_message
            'Description is required'
            
            >>> result = InputValidation.validate_description("a" * 101)
            >>> result.error_message
            'Description is too long (max 100 characters)'
            
        Usage:
            result = InputValidation.validate_description(desc_var.get())
            if not result:
                show_error(result.error_message)
                focus_on(result.error_field)  # Auto-focus description field
                return
            description = result.sanitized_value  # Get stripped description
        """
        # Check if empty or whitespace only
        if not value_str or value_str.strip() == "":
            return ValidationResult.error("Description is required", "description")
        
        # Strip whitespace for checking length
        desc_stripped = value_str.strip()
        
        # Check length
        if len(desc_stripped) > max_length:
            return ValidationResult.error(
                f"Description is too long (max {max_length} characters)", 
                "description"
            )
        
        return ValidationResult.success(desc_stripped, "description")
    
    @staticmethod
    def parse_amount(value_str):
        """
        Parse amount string to float, handling various formats.
        
        Converts user input string to a float value.
        Handles edge cases like trailing/leading whitespace.
        
        Args:
            value_str (str): The amount string to parse
            
        Returns:
            float or None: Parsed amount, or None if parsing fails
            
        Examples:
            >>> InputValidation.parse_amount("123.45")
            123.45
            
            >>> InputValidation.parse_amount("  100  ")
            100.0
            
            >>> InputValidation.parse_amount("invalid")
            None
        """
        try:
            return float(value_str.strip())
        except (ValueError, AttributeError):
            return None
    
    @staticmethod
    def format_amount(amount):
        """
        Format amount for display with 2 decimal places.
        
        Converts float to string with consistent formatting.
        Used for displaying amounts in UI and reports.
        
        Args:
            amount (float): The amount to format
            
        Returns:
            str: Formatted amount string
            
        Examples:
            >>> InputValidation.format_amount(123.4)
            '123.40'
            
            >>> InputValidation.format_amount(1000)
            '1000.00'
            
            >>> InputValidation.format_amount(123.456)
            '123.46'
        """
        return f"{amount:.2f}"
    
    @staticmethod
    def validate_expense_form(amount_str, description_str, date_str=None):
        """
        Validate complete expense form with all fields.
        
        Validates all fields and returns first error encountered,
        or success with a dict of all sanitized values.
        
        This eliminates the need for multiple validation calls!
        
        Args:
            amount_str (str): Amount string to validate
            description_str (str): Description string to validate
            date_str (str, optional): Date string to validate (uses today if None)
            
        Returns:
            ValidationResult: Combined validation result
                - If valid: result.sanitized_value contains dict with keys:
                    {'amount': float, 'description': str, 'date': str}
                - If invalid: result.error_field indicates which field failed
                
        Examples:
            >>> result = InputValidation.validate_expense_form("100", "Groceries")
            >>> result.is_valid
            True
            >>> result.sanitized_value
            {'amount': 100.0, 'description': 'Groceries', 'date': '2025-10-19'}
            
            >>> result = InputValidation.validate_expense_form("", "Groceries")
            >>> result.error_field
            'amount'
            >>> result.error_message
            'Amount is required'
            
            >>> result = InputValidation.validate_expense_form("100", "")
            >>> result.error_field
            'description'
            
        Usage (replaces 60+ lines of validation code!):
            result = InputValidation.validate_expense_form(
                amount_var.get(),
                desc_var.get()
            )
            if not result:
                show_error(result.error_message)
                focus_on(result.error_field)
                return
            
            # All validated! Use the data:
            data = result.sanitized_value
            expense = {
                'amount': data['amount'],
                'description': data['description'],
                'date': data['date']
            }
        """
        from datetime import datetime
        
        # Validate amount first
        amount_result = InputValidation.validate_final_amount(amount_str)
        if not amount_result:
            return amount_result  # Return the error
        
        # Validate description
        desc_result = InputValidation.validate_description(description_str)
        if not desc_result:
            return desc_result  # Return the error
        
        # Use today's date if not provided
        if date_str is None or date_str.strip() == "":
            date_value = datetime.now().strftime("%Y-%m-%d")
        else:
            # Could add date validation here in future
            date_value = date_str.strip()
        
        # All valid! Return combined data
        sanitized_data = {
            'amount': amount_result.sanitized_value,
            'description': desc_result.sanitized_value,
            'date': date_value
        }
        
        return ValidationResult.success(sanitized_data, "form")


class ValidationPresets:
    """
    Pre-configured validation patterns for common scenarios.
    
    Makes validation even simpler by providing named presets
    for each dialog/form type in the application.
    
    Benefits:
    - One-line validation for common forms
    - Consistent validation rules across app
    - Easy to update validation for all forms at once
    - Self-documenting code (preset names describe intent)
    
    Example:
        # Instead of:
        amount_result = InputValidation.validate_final_amount(amount)
        if not amount_result: return
        desc_result = InputValidation.validate_description(desc)
        if not desc_result: return
        # ... etc (15+ lines)
        
        # Just do:
        result = ValidationPresets.quick_add_expense(amount, desc)
        if not result: return
        data = result.sanitized_value  # Done!
    """
    
    @staticmethod
    def quick_add_expense(amount_str, description_str):
        """
        Validate Quick Add expense form (today's date assumed).
        
        Use this for the Quick Add dialog from system tray.
        
        Args:
            amount_str: Amount input
            description_str: Description input
            
        Returns:
            ValidationResult with dict containing:
                {'amount': float, 'description': str, 'date': str}
                
        Example:
            result = ValidationPresets.quick_add_expense(
                amount_var.get(),
                desc_var.get()
            )
            if not result:
                show_error(result.error_message)
                focus_widget[result.error_field].focus_set()
                return
            
            expense_data = result.sanitized_value
            # expense_data = {'amount': 100.0, 'description': '...', 'date': '...'}
        """
        return InputValidation.validate_expense_form(
            amount_str, 
            description_str, 
            None  # Uses today's date
        )
    
    @staticmethod
    def manual_add_expense(amount_str, description_str, date_str):
        """
        Validate manual Add Expense form (custom date provided).
        
        Use this for the full Add Expense dialog with date picker.
        
        Args:
            amount_str: Amount input
            description_str: Description input
            date_str: Date input (YYYY-MM-DD format)
            
        Returns:
            ValidationResult with dict containing:
                {'amount': float, 'description': str, 'date': str}
                
        Example:
            result = ValidationPresets.manual_add_expense(
                amount_var.get(),
                desc_var.get(),
                date_var.get()
            )
            if not result:
                show_error(result.error_message)
                focus_widget[result.error_field].focus_set()
                return
            
            expense_data = result.sanitized_value
        """
        return InputValidation.validate_expense_form(
            amount_str, 
            description_str, 
            date_str
        )
    
    @staticmethod
    def edit_expense(amount_str, description_str, date_str):
        """
        Validate Edit Expense form (all fields required).
        
        Same as manual_add but explicitly named for clarity.
        Use this when editing an existing expense.
        
        Args:
            amount_str: Amount input
            description_str: Description input
            date_str: Date input (YYYY-MM-DD format)
            
        Returns:
            ValidationResult with dict containing:
                {'amount': float, 'description': str, 'date': str}
                
        Example:
            result = ValidationPresets.edit_expense(
                amount_var.get(),
                desc_var.get(),
                date_var.get()
            )
            if not result:
                show_error(result.error_message)
                return
            
            updated_expense = result.sanitized_value
        """
        return InputValidation.validate_expense_form(
            amount_str, 
            description_str, 
            date_str
        )

