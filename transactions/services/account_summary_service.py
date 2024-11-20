from decimal import Decimal
from typing import List, Dict, Any
from django.db.models import Sum, F, DecimalField, QuerySet
from django.db.models.functions import Coalesce
from accounts.models import PersonalAccount
from transactions.models import Transaction
from datetime import datetime, timedelta
import pandas as pd


def get_monthly_report_data(month: int, year: int) -> List[Dict[str, Any]]:
    """
    Generate a monthly report of transactions for each account.

    Args:
        month (int): The month for the report.
        year (int): The year for the report.

    Returns:
        List[Dict[str, Any]]: List of account summaries.
    """
    first_day: datetime = datetime(year, month, 1)
    last_day: datetime = (first_day + timedelta(days=31)).replace(day=1) - timedelta(days=1)

    # Query for opening balances
    opening_balances = Transaction.objects.filter(date__lt=first_day).values(
        "personal_account__name"
    ).annotate(
        opening_balance=Coalesce(
            Sum(
                F("credit_amount") - F("debit_amount"),
                output_field=DecimalField(max_digits=10, decimal_places=2),
            ),
            Decimal("0.00"),
        )
    )

    # Query for transactions within the month
    transactions_in_month = Transaction.objects.filter(date__range=(first_day, last_day)).values(
        "personal_account__name"
    ).annotate(
        total_debit=Coalesce(
            Sum(F("debit_amount")), Decimal("0.00"), output_field=DecimalField(max_digits=10, decimal_places=2)
        ),
        total_credit=Coalesce(
            Sum(F("credit_amount")), Decimal("0.00"), output_field=DecimalField(max_digits=10, decimal_places=2)
        ),
    )

    # Generate report
    report: List[Dict[str, Any]] = []
    accounts: QuerySet[PersonalAccount] = PersonalAccount.objects.all().order_by("name")

    for account in accounts:
        account_name: str = account.name
        opening_balance: Decimal = next(
            (item["opening_balance"] for item in opening_balances if item["personal_account__name"] == account_name),
            Decimal("0.00"),
        )
        transaction_data: Dict[str, Any] = next(
            (item for item in transactions_in_month if item["personal_account__name"] == account_name), {}
        )
        total_debit: Decimal = transaction_data.get("total_debit", Decimal("0.00"))
        total_credit: Decimal = transaction_data.get("total_credit", Decimal("0.00"))
        closing_balance: Decimal = opening_balance + total_credit - total_debit

        report.append({
            "account_name": account_name,
            "opening_balance": round(opening_balance, 2),
            "debit": round(total_debit, 2),
            "credit": round(total_credit, 2),
            "closing_balance": round(closing_balance, 2),
        })

    return report


def get_account_summary_report(month: int, year: int) -> pd.DataFrame:
    report_data = get_monthly_report_data(month, year)
    
    formatted_data = [
        {
            "Account Summary": row["account_name"],
            "Opening Balance": round(row["opening_balance"], 2),
            "Debit": round(row["debit"], 2),
            "Credit": round(row["credit"], 2),
            "Closing Balance": round(row["closing_balance"], 2),
        }
        for row in report_data
    ]
    formatted_data.append({
        "Account Summary": "Total",
        "Opening Balance": "",
        "Debit": "",
        "Credit": "",
        "Closing Balance": sum(x["Closing Balance"] for x in formatted_data),
    })
    return pd.DataFrame(formatted_data)