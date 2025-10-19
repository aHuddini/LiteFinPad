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
from error_logger import log_export_attempt, log_export_success, log_export_error, log_library_check, log_info, log_error, log_warning


class DataExporterV2:
    """Optimized data exporter with smaller library footprint"""
    
    def __init__(self, expenses: List[Dict], current_month: str):
        """
        Initialize the exporter with expense data
        
        Args:
            expenses: List of expense dictionaries
            current_month: Current month string (YYYY-MM format)
        """
        self.expenses = expenses
        self.current_month = current_month
        self.month_name = datetime.strptime(current_month, "%Y-%m").strftime("%B %Y")
    
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
                filename = f"LF_{self.month_name.replace(' ', '_')}_Expenses.xlsx"
            
            # Ask user where to save
            save_path = filedialog.asksaveasfilename(
                defaultextension=".xlsx",
                filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")],
                initialfile=filename,
                title="Save Excel Export"
            )
            
            if not save_path:
                return False  # User cancelled
            
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
                try:
                    date_obj = datetime.strptime(expense['date'], "%Y-%m-%d")
                    formatted_date = date_obj.strftime("%m/%d/%Y")
                except:
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
            worksheet.write(summary_row + 1, 0, f'Total Expenses: {len(self.expenses)}')
            worksheet.write(summary_row + 2, 0, f'Total Amount: ${total_amount:.2f}')
            
            if len(self.expenses) > 0:
                avg_expense = total_amount / len(self.expenses)
                worksheet.write(summary_row + 3, 0, f'Average Expense: ${avg_expense:.2f}')
            
            # Close workbook
            workbook.close()
            log_export_success("Excel", save_path, len(self.expenses))
            
            messagebox.showinfo(
                "Export Successful",
                f"Expenses exported successfully!\n\n"
                f"File: {os.path.basename(save_path)}\n"
                f"Location: {os.path.dirname(save_path)}\n"
                f"Total Expenses: {len(self.expenses)}\n"
                f"Total Amount: ${total_amount:.2f}"
            )
            
            return True
            
        except Exception as e:
            log_export_error("Excel", e, "general_error")
            messagebox.showerror(
                "Export Error",
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
                filename = f"LF_{self.month_name.replace(' ', '_')}_Expenses.pdf"
            
            # Ask user where to save
            save_path = filedialog.asksaveasfilename(
                defaultextension=".pdf",
                filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")],
                initialfile=filename,
                title="Save PDF Export"
            )
            
            if not save_path:
                return False  # User cancelled
            
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
                try:
                    date_obj = datetime.strptime(expense['date'], "%Y-%m-%d")
                    formatted_date = date_obj.strftime("%m/%d/%Y")
                except:
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
            pdf.cell(0, 6, f'Total Expenses: {len(self.expenses)}', 0, 1, 'L')
            pdf.cell(0, 6, f'Total Amount: ${total_amount:.2f}', 0, 1, 'L')
            
            if len(self.expenses) > 0:
                avg_expense = total_amount / len(self.expenses)
                pdf.cell(0, 6, f'Average Expense: ${avg_expense:.2f}', 0, 1, 'L')
            
            # Save PDF
            pdf.output(save_path)
            log_export_success("PDF", save_path, len(self.expenses))
            
            messagebox.showinfo(
                "Export Successful",
                f"Expenses exported to PDF successfully!\n\n"
                f"File: {os.path.basename(save_path)}\n"
                f"Location: {os.path.dirname(save_path)}\n"
                f"Total Expenses: {len(self.expenses)}\n"
                f"Total Amount: ${total_amount:.2f}"
            )
            
            return True
            
        except Exception as e:
            log_export_error("PDF", e, "general_error")
            messagebox.showerror(
                "Export Error",
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
            log_info("Scanning for data folders...")
            data_folders = []
            for item in os.listdir('.'):
                if os.path.isdir(item) and item.startswith('data_'):
                    data_folders.append(item)
            
            data_folders.sort()  # Sort chronologically
            log_info(f"Found {len(data_folders)} data folders: {data_folders}")
            
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
                expenses_file = os.path.join(folder, "expenses.json")
                
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
                        
                        log_info(f"Loaded {len(expenses_list)} expenses from {folder}")
                        
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
            filename = f"LiteFinPad_Backup_{timestamp}.json"
            
            # Ask user where to save
            save_path = filedialog.asksaveasfilename(
                defaultextension=".json",
                filetypes=[("JSON Backup", "*.json"), ("All files", "*.*")],
                initialfile=filename,
                title="Save Backup File"
            )
            
            if not save_path:
                return False  # User cancelled
            
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
                "Backup Successful",
                f"Expense data backed up successfully!\n\n"
                f"File: {os.path.basename(save_path)}\n"
                f"Location: {os.path.dirname(save_path)}\n\n"
                f"Backup Contents:\n"
                f"• Total Months: {backup_data['total_months']}\n"
                f"• Total Expenses: {backup_data['total_expenses']}\n"
                f"• Grand Total: ${backup_data['grand_total']:.2f}\n\n"
                f"Months: {month_summary}"
            )
            
            return True
            
        except Exception as e:
            log_export_error("JSON Backup", e, "export_process")
            print(f"Error creating backup: {e}")
            messagebox.showerror(
                "Backup Error",
                f"Failed to create backup file.\n\n"
                f"Error: {str(e)}\n\n"
                f"Check logs/error_log.txt for details."
            )
            return False
    
    def show_export_dialog(self):
        """Show dialog for selecting export format"""
        import tkinter as tk
        from tkinter import ttk
        
        # Create dialog window
        dialog = tk.Toplevel()
        dialog.title("Export Expenses")
        dialog.resizable(False, False)
        dialog.transient()
        
        # IMPORTANT: Withdraw immediately to prevent flash at top-left corner
        dialog.withdraw()
        
        # Main frame
        main_frame = ttk.Frame(dialog, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = ttk.Label(
            main_frame,
            text="Export Expense Data",
            font=('Segoe UI', 18, 'bold')
        )
        title_label.pack(pady=(0, 12))
        
        # Subtitle
        subtitle_label = ttk.Label(
            main_frame,
            text=f"Month: {self.month_name} | Total Expenses: {len(self.expenses)}",
            font=('Segoe UI', 11),
            foreground='#1a1a1a'  # Dark black instead of grey
        )
        subtitle_label.pack(pady=(0, 25))
        
        # Export options frame
        options_frame = ttk.Frame(main_frame)
        options_frame.pack(fill=tk.BOTH, expand=True)
        
        # Configure button styles
        style = ttk.Style()
        style.configure('Large.TButton', font=('Segoe UI', 14, 'bold'), padding=(20, 10))
        
        # Excel button
        excel_btn = ttk.Button(
            options_frame,
            text="📊 Export to Excel",
            command=lambda: [self.export_to_excel(), dialog.destroy()],
            width=45,
            style='Large.TButton'
        )
        excel_btn.pack(pady=15)
        
        excel_desc = ttk.Label(
            options_frame,
            text="Simple table format with optional analytics",
            font=('Segoe UI', 9),
            foreground='#666666'  # Lighter grey for descriptions
        )
        excel_desc.pack(pady=(0, 5))
        
        # PDF button
        pdf_btn = ttk.Button(
            options_frame,
            text="📄 Export to PDF",
            command=lambda: [self.export_to_pdf(), dialog.destroy()],
            width=45,
            style='Large.TButton'
        )
        pdf_btn.pack(pady=15)
        
        pdf_desc = ttk.Label(
            options_frame,
            text="Formatted 'pretty' version for viewing/printing",
            font=('Segoe UI', 9),
            foreground='#666666'  # Lighter grey for descriptions
        )
        pdf_desc.pack(pady=(0, 5))
        
        # JSON Backup button
        backup_btn = ttk.Button(
            options_frame,
            text="💾 Backup (JSON)",
            command=lambda: [self.export_to_json_backup(), dialog.destroy()],
            width=45,
            style='Large.TButton'
        )
        backup_btn.pack(pady=15)
        
        backup_desc = ttk.Label(
            options_frame,
            text="Complete backup of all months for data migration/restore",
            font=('Segoe UI', 9),
            foreground='#666666'  # Lighter grey for descriptions
        )
        backup_desc.pack(pady=(0, 5))
        
        # Cancel button
        cancel_btn = ttk.Button(
            options_frame,
            text="Cancel",
            command=dialog.destroy,
            width=30,
            style='Large.TButton'
        )
        cancel_btn.pack(pady=20)
        
        # Bind Escape key to close dialog
        dialog.bind('<Escape>', lambda e: dialog.destroy())
        
        # Position dialog next to main window (snap to right side)
        dialog.update_idletasks()
        
        # Get main window position and size
        main_window = dialog.master  # The main application window
        main_x = main_window.winfo_x()
        main_y = main_window.winfo_y()
        main_width = main_window.winfo_width()
        main_height = main_window.winfo_height()
        
        # Position dialog to the right of main window with small gap
        dialog_width = 520
        dialog_height = 540
        gap = 10  # Small gap between windows
        
        x = main_x + main_width + gap
        y = main_y  # Align with top of main window
        
        # Ensure dialog doesn't go off-screen
        screen_width = dialog.winfo_screenwidth()
        if x + dialog_width > screen_width:
            # If it would go off-screen, position to the left of main window
            x = main_x - dialog_width - gap
            if x < 0:
                # If still off-screen, center it
                x = (screen_width - dialog_width) // 2
                y = (dialog.winfo_screenheight() - dialog_height) // 2
        
        dialog.geometry(f"{dialog_width}x{dialog_height}+{x}+{y}")
        
        # Show the dialog now that it's fully configured and positioned
        dialog.deiconify()
        dialog.grab_set()


def export_expenses(expenses: List[Dict], current_month: str):
    """
    Convenience function to show export dialog
    
    Args:
        expenses: List of expense dictionaries
        current_month: Current month string (YYYY-MM format)
    """
    exporter = DataExporterV2(expenses, current_month)
    exporter.show_export_dialog()
