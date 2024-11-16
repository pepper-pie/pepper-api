from openpyxl.styles import Font, Alignment, PatternFill, Border, Side
from openpyxl.worksheet.worksheet import Worksheet
import pandas as pd


def apply_table_styles(worksheet: Worksheet, df: pd.DataFrame) -> None:
    """
    Apply table styles to the Excel worksheet.

    Args:
        worksheet (Worksheet): The worksheet object to style.
        df (pd.DataFrame): The DataFrame used to calculate dimensions and apply styling.
    """
    # Header Styling
    header_font = Font(bold=True, color="FFFFFF")
    header_fill = PatternFill(start_color="4472C4", end_color="4472C4", fill_type="solid")  # RGB(54, 91, 183)
    header_border = Border(
        top=Side(border_style="medium", color="000000"),
        bottom=Side(border_style="medium", color="000000"),
    )

    for col_num, column in enumerate(df.columns, start=1):
        cell = worksheet.cell(row=1, column=col_num)
        cell.font = header_font
        cell.fill = header_fill
        cell.border = header_border
        cell.alignment = Alignment(horizontal="center", vertical="center")

    # Alternate Row Colors
    light_gray_fill = PatternFill(start_color="D7D7D7", end_color="D7D7D7", fill_type="solid")  # RGB(208, 208, 208)
    for row in range(2, len(df) + 2):  # Skip header row
        row_fill = light_gray_fill if row % 2 == 0 else None  # Alternate rows
        for col_num in range(1, len(df.columns) + 1):
            cell = worksheet.cell(row=row, column=col_num)
            if row_fill:
                cell.fill = row_fill


def format_currency_columns(worksheet: Worksheet, df: pd.DataFrame, currency_columns: list) -> None:
    """
    Format specified columns as currency.

    Args:
        worksheet (Worksheet): The worksheet object to style.
        df (pd.DataFrame): The DataFrame containing data.
        currency_columns (list): List of column names to format as currency.
    """
    currency_format = '₹ #,##0.00'  # INR currency format
    for row in range(2, len(df) + 2):  # Skip header row
        for col_num, column in enumerate(df.columns, start=1):
            if column in currency_columns:
                cell = worksheet.cell(row=row, column=col_num)
                if isinstance(df[column].iloc[row - 2], (int, float)):
                    cell.value = float(df[column].iloc[row - 2])  # Ensure it's numeric
                cell.number_format = currency_format


def apply_bottom_border(worksheet: Worksheet, df: pd.DataFrame) -> None:
    """
    Apply a thick bottom border to the last row of the table.

    Args:
        worksheet (Worksheet): The worksheet object to style.
        df (pd.DataFrame): The DataFrame used to calculate dimensions.
    """
    bottom_row = len(df) + 1
    bottom_border = Border(
        bottom=Side(border_style="medium", color="000000"),
    )
    for col_num in range(1, len(df.columns) + 1):
        cell = worksheet.cell(row=bottom_row, column=col_num)
        cell.border = bottom_border