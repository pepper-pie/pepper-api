import pandas as pd
from transactions.models import Transaction
from utils.excel_styling import sentence_case


def transaction_report(month: int, year: int) -> pd.DataFrame:
    transactions = Transaction.objects.filter(
        date__year=year,
        date__month=month
    ).order_by('date')
    formatted_data = [
        {
            "Date": row.date,
            "Narration": row.narration,
            "Debit Amount": row.debit_amount if row.debit_amount != 0 else '',
            "Credit Amount": row.credit_amount if row.credit_amount != 0 else '',
            "Category": row.category,
            "Sub Category": getattr(row.sub_category, 'name', ''),
            "Personal Account": row.personal_account.name,
            "Nominal Account": sentence_case(row.nominal_account),
            "Running Balance": row.running_balance,
        }
        for row in transactions
    ]
    # Generate an Excel file
    return pd.DataFrame(formatted_data)
    