import pandas as pd
from django.http import HttpResponse
from rest_framework.decorators import api_view
from rest_framework.request import Request
from rest_framework.response import Response

from transactions.services import (
    get_account_summary_report,
    categorised_expense_summary_data,
    transaction_report,
)

from transactions.services.expense_summary_service import expense_summary_report


@api_view(["GET"])
def monthly_reports_excel(request: Request) -> HttpResponse:
    """
    Generates a single Excel file containing:
    - Transactions list (A-I)
    - Expense Summary (K-N)
    - Expense Pivot Summary (below Expense Summary in K)
    - Account Summary (P-T)
    """
    month = request.GET.get("month")
    year = request.GET.get("year")

    # Validate inputs
    try:
        month_int = int(month)
        year_int = int(year)
    except ValueError:
        return Response({"error": "Invalid month or year provided"}, status=400)

    if month_int < 1 or month_int > 12:
        return Response({"error": "Month should be between 1 and 12"}, status=400)

    # Fetch data for all reports
    transactions_df = transaction_report(month, year)
    transactions_df["Date"] = pd.to_datetime(transactions_df["Date"]).dt.strftime("%d-%m-%Y")  # Format dates
    expense_summary_df = expense_summary_report(month, year)
    expense_pivot = categorised_expense_summary_data(month=month_int, year=year_int)
    account_summary_df = get_account_summary_report(month=month_int, year=year_int)

    # Create Excel writer
    file_name = f"monthly_reports_{year}_{month}.xlsx"
    writer = pd.ExcelWriter(file_name, engine="xlsxwriter", engine_kwargs={'options': {'strings_to_numbers': True}})

    # Write data to the workbook
    transactions_df.to_excel(writer, sheet_name="Report", index=False, startrow=0, startcol=0)
    expense_summary_df.to_excel(writer, sheet_name="Report", index=False, startrow=4, startcol=10)
    expense_pivot_data = []
    for category, data in expense_pivot["data"].items():
        expense_pivot_data.append(
            {"Category": category, "Credit": data["credit"], "Debit": data["debit"]}
        )
        for sub_category in data["sub_categories"]:
            expense_pivot_data.append(
                {"Category": f"  {sub_category['sub_category']}", "Credit": sub_category["credit"], "Debit": sub_category["debit"]}
            )
    expense_pivot_data.append(
        {"Category": "Grand Total", "Credit": expense_pivot["grand_total"]["credit"], "Debit": expense_pivot["grand_total"]["debit"]}
    )
    expense_pivot_df = pd.DataFrame(expense_pivot_data)
    expense_pivot_start_row = len(expense_summary_df) + 4 + 5  # Add padding of 5 rows
    expense_pivot_df.to_excel(writer, sheet_name="Report", index=False, startrow=expense_pivot_start_row, startcol=10)
    account_summary_df.to_excel(writer, sheet_name="Report", index=False, startrow=4, startcol=15)

    # Access the workbook and worksheet objects
    workbook = writer.book
    
    
    worksheet = writer.sheets["Report"]
    worksheet.set_zoom(117)

    currency_format = workbook.add_format({"num_format": '₹ #,##0.00', "align":  "right"})  # type: ignore
    # Define a right-aligned format for the Date column
    date_format = workbook.add_format({ # type: ignore
        "align": "right",  # Align text to the right
        "num_format": "dd-mm-yyyy",  # Ensure date is formatted correctly
        "border": 1  # Add borders to match table style
    })
    header_format = workbook.add_format({  # type: ignore
        "bold": True,
        "align": "left",
        "text_wrap": True,
        "valign": "middle",
        "fg_color": "#4472C4",  # Latest blue shade
        "border": 1,
        "font_color": "#FFFFFF",  # White text
    })

    
    currency_cols = ['Debit Amount', 'Credit Amount', 'Running Balance', 'Opening Balance', 'Debit', 'Credit', 'Total', 'Closing Balance']
    
    # Define a helper function to format tables
    def add_table_with_style(df, startrow, startcol, table_name):
        """
        Add a table with a built-in style to the worksheet.

        Args:
            df (pd.DataFrame): The DataFrame containing data.
            startrow (int): The starting row for the table.
            startcol (int): The starting column for the table.
            table_name (str): Unique name for the table.
        """
        
        isTxnTable = table_name == "TransactionsTable"
        endrow = startrow + len(df)
        endcol = startcol + len(df.columns) - 1
        table_range = f"{chr(65 + startcol)}{startrow + 1}:{chr(65 + endcol)}{endrow}"  # Convert to Excel-style range
        worksheet.add_table(
            table_range,
            {
                "name": table_name,
                "columns": [
                    {
                        "header": col,
                        # 'total_string': 'Totals' if (isExpenseSummaryTable and col == 'Account Name') else None,
                        # 'total_function': 'sum' if (isExpenseSummaryTable and col in currency_cols) else None
                    } 
                    for col in df.columns
                ],
                "total_row": False,
                "style": "Table Style" + ("Light 9" if isTxnTable else "Medium 16"),
                # 'total_row': isExpenseSummaryTable
            },
        )
        
        # Apply currency formatting to specific columns
        for col_index, col_name in enumerate(df.columns):
            if col_name in currency_cols:  # Apply formatting only to currency columns
                worksheet.set_column(startcol + col_index, startcol + col_index, 18, currency_format)
                
         # Overwrite headers with left alignment
        for col_index, col_name in enumerate(df.columns):
            worksheet.write(startrow, startcol + col_index, col_name, header_format)       

    # Add tables with styles
    add_table_with_style(transactions_df, startrow=0, startcol=0, table_name="TransactionsTable")
    add_table_with_style(expense_summary_df, startrow=4, startcol=10, table_name="ExpenseSummaryTable")
    add_table_with_style(expense_pivot_df, startrow=expense_pivot_start_row, startcol=10, table_name="ExpensePivotTable")
    add_table_with_style(account_summary_df, startrow=4, startcol=15, table_name="AccountSummaryTable")
    
    worksheet.set_column("A:A", 12, date_format)
    worksheet.set_column("B:B", 100)
    worksheet.set_column("E:H", 18)
    worksheet.set_column("J:J", 20)
    worksheet.set_column("K:K", 16)
    worksheet.set_column("P:P", 18)

    # Close the writer and save the file
    writer.close()
    

    # Return the file as response
    with open(file_name, "rb") as f:
        response = HttpResponse(
            f.read(),
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
        response["Content-Disposition"] = f'attachment; filename="{file_name}"'
        return response