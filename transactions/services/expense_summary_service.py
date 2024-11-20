
import pandas as pd
from typing import List, Dict, Any
from django.db.models import Sum, F
from pandas import DataFrame
from transactions.models import Transaction

def expense_summary_data(month: int, year: int) -> List[Dict[str, Any]]:

    expense_data = (
        Transaction.objects.filter(nominal_account="EXPENSE").values("personal_account__name")
        .annotate(
            debit=Sum("debit_amount", default=0),
            credit=Sum("credit_amount", default=0),
            total=Sum(F("debit_amount") - F("credit_amount"), default=0),
        )
        .filter(date__year=year, date__month=month)
        .order_by("personal_account__name")
    )

    data = [
        {
            "account_name": row["personal_account__name"],
            "debit": row["debit"],
            "credit": row["credit"],
            "total": row["total"],
        }
        for row in expense_data
    ]
    
    return data


def expense_summary_report(month: int, year: int) -> DataFrame:
    data = expense_summary_data(month, year)
    formatted_data = [
        {
            "Account Name": row['account_name'],
            "Debit": row['debit'],
            "Credit": row['credit'],
            "Total": row['total']
        }
        for row in data
    ]
    formatted_data.append({
            "Account Name": "Total",
            "Debit": sum(x["Debit"] for x in formatted_data),
            "Credit": sum(x["Credit"] for x in formatted_data),
            "Total": sum(x["Debit"] for x in formatted_data) - sum(x["Credit"] for x in formatted_data)
        })
    return pd.DataFrame(formatted_data)