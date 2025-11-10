"""
Export Data Module for LiteFinPad v2.7 - Optimized
=================================================

Lightweight export implementation using:
- xlsxwriter for Excel (70% smaller than openpyxl)
- fpdf2 for PDF (87% smaller than reportlab)

This module handles exporting expense data to:
- Excel (.xlsx) - Simple table format with optional analytics
- PDF (.pdf) - Formatted "pretty" version for viewing/printing
"""

import os
import sys
import json
import hashlib
import stat
from datetime import datetime
from typing import List, Dict, Optional
from tkinter import messagebox, filedialog
from error_logger import log_export_attempt, log_export_success, log_export_error, log_library_check, log_info, log_error, log_warning, log_debug
import config
from dialog_helpers import DialogHelper
from date_utils import DateUtils
from settings_manager import get_settings_manager


class DataExporterV2:
    """Optimized data exporter with smaller library footprint"""
    
    def __init__(self, expenses: List[Dict], current_month: str, status_callback=None, theme_manager=None):
        """
        Initialize the exporter with expense data
        
        Args:
            expenses: List of expense dictionaries
            current_month: Current month string (YYYY-MM format)
            status_callback: Optional callback function for status updates (icon, message)
            theme_manager: Optional ThemeManager for theme-aware colors
        """
        self.expenses = expenses
        self.current_month = current_month
        self.month_name = datetime.strptime(current_month, "%Y-%m").strftime("%B %Y")
        self.status_callback = status_callback
        self.theme_manager = theme_manager
        self.export_location = self._load_export_location()
    
    def generate_data_checksum(self, data: Dict) -> str:
        """
        Generate SHA-256 checksum for backup data integrity
        
        Args:
            data: Dictionary to hash
            
        Returns:
            str: Hex string of SHA-256 hash
        """
        # Convert to stable JSON string (sorted keys for consistency)
        json_str = json.dumps(data, sort_keys=True)
        return hashlib.sha256(json_str.encode()).hexdigest()
    
    def _load_export_location(self) -> str:
        """Load the default export location from settings"""
        import sys
        
        settings = get_settings_manager()
        location = settings.get('Export', 'default_save_location', default='')
        
        # Validate that location exists
        if location and os.path.exists(location):
            return location
        
        # Default to application directory (where .exe or main.py is located)
        if getattr(sys, 'frozen', False):
            # Running as compiled executable
            app_dir = os.path.dirname(sys.executable)
        else:
            # Running as Python script
            app_dir = os.path.abspath('.')
        
        return app_dir
    
    def _save_export_location(self, location: str):
        """Save the export location to settings"""
        settings = get_settings_manager()
        if not settings.set('Export', 'default_save_location', location):
            log_error("Failed to save export location", None)
    
    def _get_shortened_path(self, path: str) -> str:
        """
        Smart path truncation: show drive + first folder + ... + last 2 folders
        Example: C:\\Users\\...\\OneDrive\\Documents
        """
        # Truncate if path is longer than 45 characters and has more than 3 parts
        if len(path) <= 45:
            return path
        
        # Use forward slashes to split (works on Windows too)
        if '\\' in path:
            parts = path.split('\\')
            sep = '\\'
        else:
            parts = path.split('/')
            sep = '/'
        
        # Filter out empty parts
        parts = [p for p in parts if p]
        
        # If path is simple (like "C:" or "C:\\Users"), don't truncate
        if len(parts) <= 3:
            return path
        
        # Get components: drive, first folder, last 2 folders
        drive = parts[0]  # e.g., "C:"
        first_folder = parts[1] if len(parts) > 1 else ""  # e.g., "Users"
        second_last = parts[-2] if len(parts) > 1 else ""  # e.g., "OneDrive"
        last_folder = parts[-1]  # e.g., "Documents"
        
        # Build shortened path: C:\\Users\\...\\OneDrive\\Documents
        shortened = f"{drive}{sep}{first_folder}{sep}...{sep}{second_last}{sep}{last_folder}"
        return shortened
        
    def export_to_excel(self, filename: Optional[str] = None) -> bool:
        """
        Export expenses to Excel (.xlsx) format - Simple table with optional analytics
        
        Args:
            filename: Optional custom filename. If None, auto-generates one.
            
        Returns:
            bool: True if export successful, False otherwise
        """
        log_export_attempt("Excel", len(self.expenses))
        
        try:
            # Import Excel library
            try:
                import xlsxwriter
                log_library_check("xlsxwriter", True)
            except ImportError as e:
                log_library_check("xlsxwriter", False)
                log_export_error("Excel", e, "library_import")
                
                messagebox.showerror(
                    "Missing Dependency",
                    "Excel export requires 'xlsxwriter' library.\n"
                    "Please install it: pip install xlsxwriter\n\n"
                    "If running from executable, the library may not be bundled.\n"
                    "Check logs/error_log.txt for details."
                )
                return False
            
            # Generate filename if not provided
            if not filename:
                # Format: LF_October_2025_Expenses.xlsx
                filename = f"{config.Files.EXPORT_EXCEL_PREFIX}_{self.month_name.replace(' ', '_')}_Expenses{config.Files.EXCEL_EXT}"
            
            # Use the saved export location
            save_path = os.path.join(self.export_location, filename)
            
            # Create workbook and worksheet
            workbook = xlsxwriter.Workbook(save_path)
            worksheet = workbook.add_worksheet('Expenses')
            
            # Define formats
            header_format = workbook.add_format({
                'bold': True,
                'font_color': 'white',
                'bg_color': '#0078D4',
                'align': 'center',
                'valign': 'vcenter',
                'border': 1
            })
            
            cell_format = workbook.add_format({
                'align': 'left',
                'valign': 'vcenter',
                'border': 1
            })
            
            amount_format = workbook.add_format({
                'align': 'right',
                'valign': 'vcenter',
                'border': 1,
                'num_format': '$#,##0.00'
            })
            
            total_format = workbook.add_format({
                'bold': True,
                'bg_color': '#E7E6E6',
                'align': 'right',
                'valign': 'vcenter',
                'border': 1,
                'num_format': '$#,##0.00'
            })
            
            total_label_format = workbook.add_format({
                'bold': True,
                'bg_color': '#E7E6E6',
                'align': 'right',
                'valign': 'vcenter',
                'border': 1
            })
            
            # Set column widths
            worksheet.set_column('A:A', 12)  # Date
            worksheet.set_column('B:B', 40)  # Description
            worksheet.set_column('C:C', 15)  # Amount
            worksheet.set_column('D:D', 15)  # Category
            
            # Write headers (row 0)
            headers = ['Date', 'Description', 'Amount', 'Category']
            for col, header in enumerate(headers):
                worksheet.write(0, col, header, header_format)
            
            # Sort expenses by date (most recent first)
            sorted_expenses = sorted(self.expenses, key=lambda x: x['date'], reverse=True)
            
            # Write expense data
            total_amount = 0.0
            row = 1
            
            for expense in sorted_expenses:
                # Format date
                date_obj = DateUtils.parse_date(expense['date'])
                if date_obj:
                    formatted_date = date_obj.strftime("%m/%d/%Y")
                else:
                    formatted_date = expense['date']
                
                # Write row data
                worksheet.write(row, 0, formatted_date, cell_format)
                worksheet.write(row, 1, expense['description'], cell_format)
                worksheet.write(row, 2, expense['amount'], amount_format)
                worksheet.write(row, 3, expense.get('category', ''), cell_format)
                
                total_amount += expense['amount']
                row += 1
            
            # Add total row
            total_row = row
            worksheet.write(total_row, 1, 'TOTAL:', total_label_format)
            worksheet.write(total_row, 2, total_amount, total_format)
            
            # Add analytics summary below table (optional section)
            summary_row = total_row + 2
            
            summary_header_format = workbook.add_format({
                'bold': True,
                'font_size': 12
            })
            
            worksheet.write(summary_row, 0, 'Summary:', summary_header_format)
            worksheet.write(summary_row + 1, 0, f'{config.Messages.LABEL_TOTAL_EXPENSES} {len(self.expenses)}')
            worksheet.write(summary_row + 2, 0, f'{config.Messages.LABEL_TOTAL_AMOUNT} ${total_amount:.2f}')
            
            if len(self.expenses) > 0:
                avg_expense = total_amount / len(self.expenses)
                worksheet.write(summary_row + 3, 0, f'Average Expense: ${avg_expense:.2f}')
            
            # Close workbook
            workbook.close()
            log_export_success("Excel", save_path, len(self.expenses))
            
            messagebox.showinfo(
                config.Messages.TITLE_EXPORT_SUCCESS,
                f"Expenses exported successfully!\n\n"
                f"File: {os.path.basename(save_path)}\n"
                f"Location: {os.path.dirname(save_path)}\n"
                f"{config.Messages.LABEL_TOTAL_EXPENSES} {len(self.expenses)}\n"
                f"{config.Messages.LABEL_TOTAL_AMOUNT} ${total_amount:.2f}"
            )
            
            # Update status bar if callback provided
            if self.status_callback:
                self.status_callback(f"Exported to Excel: {os.path.basename(save_path)}", config.StatusBar.SUCCESS_ICON)
            
            return True
            
        except Exception as e:
            log_export_error("Excel", e, "general_error")
            messagebox.showerror(
                config.Messages.TITLE_EXPORT_ERROR,
                f"Failed to export to Excel:\n{str(e)}\n\n"
                "Check logs/error_log.txt for details."
            )
            return False
    
    def export_to_pdf(self, filename: Optional[str] = None) -> bool:
        """
        Export expenses to PDF format - Formatted "pretty" version
        
        Args:
            filename: Optional custom filename. If None, auto-generates one.
            
        Returns:
            bool: True if export successful, False otherwise
        """
        log_export_attempt("PDF", len(self.expenses))
        
        try:
            # Import PDF library
            try:
                from fpdf import FPDF
                log_library_check("fpdf2", True)
            except ImportError as e:
                log_library_check("fpdf2", False)
                log_export_error("PDF", e, "library_import")
                
                messagebox.showerror(
                    "Missing Dependency",
                    "PDF export requires 'fpdf2' library.\n"
                    "Please install it: pip install fpdf2\n\n"
                    "If running from executable, the library may not be bundled.\n"
                    "Check logs/error_log.txt for details."
                )
                return False
            
            # Generate filename if not provided
            if not filename:
                # Format: LF_October_2025_Expenses.pdf
                filename = f"{config.Files.EXPORT_PDF_PREFIX}_{self.month_name.replace(' ', '_')}_Expenses{config.Files.PDF_EXT}"
            
            # Use the saved export location
            save_path = os.path.join(self.export_location, filename)
            
            # Create PDF
            pdf = FPDF()
            pdf.add_page()
            
            # Title
            pdf.set_font('Helvetica', 'B', 20)
            pdf.set_text_color(0, 120, 212)  # #0078D4
            pdf.cell(0, 10, f'LiteFinPad - Expense Report', 0, 1, 'C')
            pdf.cell(0, 8, f'{self.month_name}', 0, 1, 'C')
            
            # Timestamp
            pdf.set_font('Helvetica', 'I', 9)
            pdf.set_text_color(128, 128, 128)  # Grey
            timestamp_text = f"Exported on: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}"
            pdf.cell(0, 6, timestamp_text, 0, 1, 'C')
            
            pdf.ln(5)  # Line break
            
            # Reset text color
            pdf.set_text_color(0, 0, 0)
            
            # Sort expenses by date (most recent first)
            sorted_expenses = sorted(self.expenses, key=lambda x: x['date'], reverse=True)
            
            # Table header
            pdf.set_font('Helvetica', 'B', 11)
            pdf.set_fill_color(0, 120, 212)  # #0078D4
            pdf.set_text_color(255, 255, 255)  # White
            
            col_widths = [30, 80, 30, 30]  # Date, Description, Amount, Category
            headers = ['Date', 'Description', 'Amount', 'Category']
            
            for i, header in enumerate(headers):
                pdf.cell(col_widths[i], 10, header, 1, 0, 'C', 1)
            pdf.ln()
            
            # Table data
            pdf.set_font('Helvetica', '', 10)
            pdf.set_text_color(0, 0, 0)
            
            total_amount = 0.0
            fill = False  # Alternating row colors
            
            for expense in sorted_expenses:
                # Format date
                date_obj = DateUtils.parse_date(expense['date'])
                if date_obj:
                    formatted_date = date_obj.strftime("%m/%d/%Y")
                else:
                    formatted_date = expense['date']
                
                # Truncate description if too long
                description = expense['description']
                if len(description) > 40:
                    description = description[:37] + '...'
                
                # Set alternating row background
                if fill:
                    pdf.set_fill_color(245, 245, 245)  # Light grey
                else:
                    pdf.set_fill_color(255, 255, 255)  # White
                
                # Write row
                pdf.cell(col_widths[0], 8, formatted_date, 1, 0, 'C', 1)
                pdf.cell(col_widths[1], 8, description, 1, 0, 'L', 1)
                pdf.cell(col_widths[2], 8, f'${expense["amount"]:.2f}', 1, 0, 'R', 1)
                pdf.cell(col_widths[3], 8, expense.get('category', ''), 1, 0, 'C', 1)
                pdf.ln()
                
                total_amount += expense['amount']
                fill = not fill
            
            # Total row
            pdf.set_font('Helvetica', 'B', 11)
            pdf.set_fill_color(231, 230, 230)  # #E7E6E6
            pdf.cell(col_widths[0], 10, '', 1, 0, 'C', 1)
            pdf.cell(col_widths[1], 10, 'TOTAL:', 1, 0, 'R', 1)
            pdf.cell(col_widths[2], 10, f'${total_amount:.2f}', 1, 0, 'R', 1)
            pdf.cell(col_widths[3], 10, '', 1, 0, 'C', 1)
            pdf.ln(15)
            
            # Summary section
            pdf.set_font('Helvetica', 'B', 12)
            pdf.cell(0, 8, 'Summary', 0, 1, 'L')
            
            pdf.set_font('Helvetica', '', 10)
            pdf.cell(0, 6, f'{config.Messages.LABEL_TOTAL_EXPENSES} {len(self.expenses)}', 0, 1, 'L')
            pdf.cell(0, 6, f'{config.Messages.LABEL_TOTAL_AMOUNT} ${total_amount:.2f}', 0, 1, 'L')
            
            if len(self.expenses) > 0:
                avg_expense = total_amount / len(self.expenses)
                pdf.cell(0, 6, f'Average Expense: ${avg_expense:.2f}', 0, 1, 'L')
            
            # Save PDF
            pdf.output(save_path)
            log_export_success("PDF", save_path, len(self.expenses))
            
            messagebox.showinfo(
                config.Messages.TITLE_EXPORT_SUCCESS,
                f"Expenses exported to PDF successfully!\n\n"
                f"File: {os.path.basename(save_path)}\n"
                f"Location: {os.path.dirname(save_path)}\n"
                f"{config.Messages.LABEL_TOTAL_EXPENSES} {len(self.expenses)}\n"
                f"{config.Messages.LABEL_TOTAL_AMOUNT} ${total_amount:.2f}"
            )
            
            # Update status bar if callback provided
            if self.status_callback:
                self.status_callback(f"Exported to PDF: {os.path.basename(save_path)}", config.StatusBar.SUCCESS_ICON)
            
            return True
            
        except Exception as e:
            log_export_error("PDF", e, "general_error")
            messagebox.showerror(
                config.Messages.TITLE_EXPORT_ERROR,
                f"Failed to export to PDF:\n{str(e)}\n\n"
                "Check logs/error_log.txt for details."
            )
            return False
    
    def export_to_json_backup(self) -> bool:
        """
        Export all expense data to JSON backup file
        Scans all data_* folders and creates comprehensive backup
        
        Returns:
            bool: True if export successful, False otherwise
        """
        log_export_attempt("JSON Backup", len(self.expenses))
        
        try:
            import json
            from tkinter import filedialog
            
            # Scan for all data_* folders
            log_debug("Scanning for data folders...")
            data_folders = []
            for item in os.listdir('.'):
                if os.path.isdir(item) and item.startswith('data_'):
                    data_folders.append(item)
            
            data_folders.sort()  # Sort chronologically
            log_debug(f"Found {len(data_folders)} data folders: {data_folders}")
            
            # Build comprehensive backup structure
            backup_data = {
                "app_version": "3.3",
                "backup_date": datetime.now().isoformat(),
                "backup_type": "full",
                "total_months": len(data_folders),
                "months": {},
                "total_expenses": 0,
                "grand_total": 0.0
            }
            
            # Load data from each month
            for folder in data_folders:
                expenses_file = os.path.join(folder, config.Files.EXPENSES_FILENAME)
                
                if os.path.exists(expenses_file):
                    try:
                        with open(expenses_file, 'r') as f:
                            month_data = json.load(f)
                            
                        expenses_list = month_data.get('expenses', [])
                        
                        # Calculate actual total by summing all expense amounts
                        # (Don't use saved monthly_total as it excludes future expenses)
                        actual_total = sum(expense.get('amount', 0.0) for expense in expenses_list)
                        
                        # Extract month from folder name (e.g., data_2025-10 -> 2025-10)
                        month_key = folder.replace('data_', '')
                        
                        backup_data["months"][month_key] = {
                            "expenses": expenses_list,
                            "monthly_total": actual_total,
                            "expense_count": len(expenses_list)
                        }
                        
                        backup_data["total_expenses"] += len(expenses_list)
                        backup_data["grand_total"] += actual_total
                        
                        log_debug(f"Loaded {len(expenses_list)} expenses from {folder}")
                        
                    except Exception as e:
                        log_error(f"Error loading {expenses_file}", e)
                        # Continue with other folders
                else:
                    log_warning(f"Expenses file not found: {expenses_file}")
            
            if backup_data["total_expenses"] == 0:
                messagebox.showwarning(
                    "No Data",
                    "No expense data found to backup.\n\n"
                    "Make sure you have expenses in data_* folders."
                )
                return False
            
            # Generate filename: LiteFinPad_Backup_2025-10-19_002600.json
            timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
            filename = config.Files.get_backup_filename(timestamp)
            
            # Use the saved export location
            save_path = os.path.join(self.export_location, filename)
            
            # Add security signature and data integrity checksum
            backup_data["app_signature"] = "LiteFinPad-Official"
            
            # Generate checksum of months data for integrity verification
            months_checksum = self.generate_data_checksum(backup_data["months"])
            backup_data["data_integrity"] = {
                "algorithm": "SHA256",
                "checksum": months_checksum,
                "generated_by": f"LiteFinPad v{backup_data['app_version']}"
            }
            
            log_info(f"Generated data integrity checksum: {months_checksum[:16]}...")
            
            # Save backup file
            with open(save_path, 'w') as f:
                json.dump(backup_data, f, indent=2)
            
            # Set file to read-only to prevent accidental modification
            try:
                os.chmod(save_path, stat.S_IREAD | stat.S_IRGRP | stat.S_IROTH)
                log_info(f"Backup file set to read-only: {save_path}")
            except Exception as chmod_error:
                log_warning(f"Could not set read-only attribute: {chmod_error}")
                # Don't fail the export if we can't set read-only
            
            log_export_success("JSON Backup", save_path, backup_data["total_expenses"])
            
            # Summary message
            month_summary = ", ".join(backup_data["months"].keys())
            messagebox.showinfo(
                config.Messages.TITLE_SUCCESS,
                f"Expense data backed up successfully!\n\n"
                f"File: {os.path.basename(save_path)}\n"
                f"Location: {os.path.dirname(save_path)}\n\n"
                f"Backup Contents:\n"
                f"• Total Months: {backup_data['total_months']}\n"
                f"• Total Expenses: {backup_data['total_expenses']}\n"
                f"• Grand Total: ${backup_data['grand_total']:.2f}\n\n"
                f"Months: {month_summary}"
            )
            
            # Update status bar if callback provided
            if self.status_callback:
                self.status_callback(f"JSON backup created: {backup_data['total_months']} months backed up", config.StatusBar.SUCCESS_ICON)
            
            return True
            
        except Exception as e:
            log_export_error("JSON Backup", e, "export_process")
            print(f"Error creating backup: {e}")
            messagebox.showerror(
                config.Messages.TITLE_ERROR,
                f"Failed to create backup file.\n\n"
                f"Error: {str(e)}\n\n"
                f"Check logs/error_log.txt for details."
            )
            return False
    
    def show_export_dialog(self, theme_manager=None):
        """Show enhanced dialog for selecting export format with default save location"""
        import tkinter as tk
        from tkinter import ttk, filedialog
        
        # Get theme-aware colors
        colors = theme_manager.get_colors() if theme_manager else config.Colors
        
        # Get main window reference
        main_window = tk._default_root
        
        # Create dialog using DialogHelper with theme-aware colors
        dialog = DialogHelper.create_dialog(
            main_window,
            "Export Expenses",
            config.Dialog.EXPORT_WIDTH,
            config.Dialog.EXPORT_HEIGHT,
            colors=colors
        )
        
        # Create main content frame with reduced padding
        main_frame = DialogHelper.create_content_frame(dialog, padding="15")
        
        # Title
        title_label = ttk.Label(
            main_frame,
            text="Export Expense Data",
            font=('Segoe UI', 15, 'bold')
        )
        title_label.pack(pady=(0, 5))
        
        # Subtitle with underlined labels and vertical separator
        subtitle_frame = ttk.Frame(main_frame)
        subtitle_frame.pack(pady=(0, 8))
        
        month_label = ttk.Label(subtitle_frame, text="Month:", font=('Segoe UI', 10, 'underline'), foreground='#1a1a1a')
        month_label.pack(side=tk.LEFT)
        
        month_value = ttk.Label(subtitle_frame, text=f" {self.month_name}", font=('Segoe UI', 10), foreground='#1a1a1a')
        month_value.pack(side=tk.LEFT, padx=(0, 10))
        
        # Vertical separator
        vsep = ttk.Separator(subtitle_frame, orient='vertical')
        vsep.pack(side=tk.LEFT, fill=tk.Y, padx=10)
        
        expenses_label = ttk.Label(subtitle_frame, text=config.Messages.LABEL_TOTAL_EXPENSES, font=('Segoe UI', 10, 'underline'), foreground='#1a1a1a')
        expenses_label.pack(side=tk.LEFT)
        
        expenses_value = ttk.Label(subtitle_frame, text=f" {len(self.expenses)}", font=('Segoe UI', 10), foreground='#1a1a1a')
        expenses_value.pack(side=tk.LEFT)
        
        # Separator line
        sep1 = ttk.Separator(main_frame, orient='horizontal')
        sep1.pack(fill=tk.X, pady=(0, 10))
        
        # Export options frame
        options_frame = ttk.Frame(main_frame)
        options_frame.pack(fill=tk.BOTH, expand=True)
        
        # Configure button style with padding for height
        style = ttk.Style()
        style.configure('Export.TButton', padding=(10, 6))
        
        # Excel button
        excel_btn = ttk.Button(
            options_frame,
            text="📊 Export to Excel",
            command=lambda: [self.export_to_excel(), dialog.destroy()],
            width=22,
            style='Export.TButton'
        )
        excel_btn.pack(pady=5)
        excel_desc = ttk.Label(options_frame, text="Simple table format with optional analytics", font=('Segoe UI', 9), foreground='#666666')
        excel_desc.pack(pady=(0, 5))
        
        # PDF button
        pdf_btn = ttk.Button(
            options_frame,
            text="📄 Export to PDF",
            command=lambda: [self.export_to_pdf(), dialog.destroy()],
            width=22,
            style='Export.TButton'
        )
        pdf_btn.pack(pady=5)
        pdf_desc = ttk.Label(options_frame, text="Formatted 'pretty' version for viewing/printing", font=('Segoe UI', 9), foreground='#666666')
        pdf_desc.pack(pady=(0, 5))
        
        # JSON button
        backup_btn = ttk.Button(
            options_frame,
            text="💾 Backup (JSON)",
            command=lambda: [self.export_to_json_backup(), dialog.destroy()],
            width=22,
            style='Export.TButton'
        )
        backup_btn.pack(pady=5)
        backup_desc = ttk.Label(options_frame, text="Complete backup of all months for data migration/restore", font=('Segoe UI', 9), foreground='#666666')
        backup_desc.pack(pady=(0, 3))
        
        # Separator line
        sep2 = ttk.Separator(main_frame, orient='horizontal')
        sep2.pack(fill=tk.X, pady=(0, 5))
        
        # === DEFAULT SAVE LOCATION AT BOTTOM ===
        location_frame = ttk.LabelFrame(main_frame, text="Default Save Location", padding=8)
        location_frame.pack(fill=tk.X, pady=(5, 0))
        
        # Variable to store and display location
        location_var = tk.StringVar(value=self.export_location)
        display_var = tk.StringVar()
        
        def update_display():
            display_var.set(self._get_shortened_path(location_var.get()))
        
        update_display()
        
        # Location field (reduced width)
        location_entry = ttk.Entry(location_frame, textvariable=display_var, state='readonly', font=('Segoe UI', 9), width=26)
        location_entry.pack(fill=tk.X, pady=(0, 6))
        
        # Change button below (aligned to left)
        def change_location():
            new_loc = filedialog.askdirectory(title="Select Save Location", initialdir=location_var.get())
            if new_loc:
                location_var.set(new_loc)
                self.export_location = new_loc
                self._save_export_location(new_loc)
                update_display()
        
        change_btn = ttk.Button(location_frame, text="Change...", command=change_location, width=15)
        change_btn.pack(anchor='w')
        
        # Position dialog to the right of main window with intelligent fallbacks
        DialogHelper.position_right_of_parent(
            dialog,
            main_window,
            config.Dialog.EXPORT_WIDTH,
            config.Dialog.EXPORT_HEIGHT,
            config.Dialog.EXPORT_GAP
        )
        
        # Bind Escape key to close dialog
        DialogHelper.bind_escape_to_close(dialog)
        
        # Show the dialog
        DialogHelper.show_dialog(dialog)


def export_expenses(expenses: List[Dict], current_month: str, status_callback=None, theme_manager=None):
    """
    Convenience function to show export dialog
    
    Args:
        expenses: List of expense dictionaries
        current_month: Current month string (YYYY-MM format)
        status_callback: Optional callback function for status updates (message, icon)
        theme_manager: Optional ThemeManager for theme-aware colors
    """
    exporter = DataExporterV2(expenses, current_month, status_callback, theme_manager=theme_manager)
    exporter.show_export_dialog(theme_manager=theme_manager)
