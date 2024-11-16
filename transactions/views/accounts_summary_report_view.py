from decimal import Decimal
import pandas as pd
from django.http import HttpResponse
from django.db.models import QuerySet, Sum, F, DecimalField
from django.db.models.functions import Coalesce, Cast
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.request import Request
from typing import List, Dict, Any
from transactions.models import Transaction
from accounts.models import PersonalAccount
from datetime import datetime, timedelta
from utils.excel_styling import apply_table_styles, format_currency_columns

import typing

if typing.TYPE_CHECKING:
    from django.db.models.query import ValuesQuerySet


@api_view(['GET'])
def monthly_report(request: Request) -> HttpResponse:
    """
    Generate a monthly report of transactions for each account and return it as an Excel file.

    Args:
        request (Request): The HTTP GET request containing 'month' and 'year' as query parameters.

    Returns:
        HttpResponse: An Excel file with the monthly report or an error response.
    """
    month: str = request.GET.get('month', '')
    year: str = request.GET.get('year', '')

    if not month or not year:
        return Response({"error": "Please provide both month and year in the request."}, status=400)

    try:
        month_int: int = int(month)
        year_int: int = int(year)
    except ValueError:
        return Response({"error": "Month and year should be valid integers."}, status=400)

    # Validate month and year
    if month_int < 1 or month_int > 12:
        return Response({"error": "Month should be between 1 and 12."}, status=400)

    # Get the first and last dates of the month
    first_day: datetime = datetime(year_int, month_int, 1)
    last_day: datetime = (first_day + timedelta(days=31)).replace(day=1) - timedelta(days=1)

    # Query the transactions
    # Replace QuerySet[Dict[str, Any]] with List[Dict[str, Any]]
    # Typing for .values() queries
    opening_balances: ValuesQuerySet[Transaction, dict[str, Any]] = (
       Transaction.objects.filter(date__lt=first_day)
        .values('personal_account__name')
        .annotate(
            opening_balance=Coalesce(
                Sum(
                    Cast(Coalesce(F('credit_amount'), Decimal('0.00')), output_field=DecimalField(max_digits=10, decimal_places=2))
                    - Cast(Coalesce(F('debit_amount'), Decimal('0.00')), output_field=DecimalField(max_digits=10, decimal_places=2))
                ),
                Decimal('0.00')
            )
        )
    )

    transactions_in_month: ValuesQuerySet[Transaction, Dict[str, Any]] = (
        Transaction.objects.filter(date__range=(first_day, last_day))
        .values('personal_account__name')
        .annotate(
            total_debit=Cast(
                Coalesce(Sum(Coalesce(F('debit_amount'), 0)), 0),
                output_field=DecimalField(max_digits=10, decimal_places=2)
            ),
            total_credit=Cast(
                Coalesce(Sum(Coalesce(F('credit_amount'), 0)), 0),
                output_field=DecimalField(max_digits=10, decimal_places=2)
            ),
        )
    )

    # Combine data into a final report
    report: List[Dict[str, Any]] = []
    accounts: QuerySet[PersonalAccount] = PersonalAccount.objects.all()

    for account in accounts:
        account_name: str = account.name
        opening_balance: Decimal = next(
            (item['opening_balance'] for item in opening_balances if item['personal_account__name'] == account_name), Decimal(0.0)
        )
        transaction_data: Dict[str, Any] = next(
            (item for item in transactions_in_month if item['personal_account__name'] == account_name), {}
        )
        total_debit: Decimal = transaction_data.get('total_debit', Decimal(0.0))
        total_credit: Decimal = transaction_data.get('total_credit', Decimal(0.0))
        closing_balance: Decimal = opening_balance - total_debit + total_credit

        report.append({
            'Account Summary': account_name,
            'Opening Balance': round(opening_balance, 2),
            'Debit': round(total_debit, 2),
            'Credit': round(total_credit, 2),
            'Closing Balance': round(closing_balance, 2),
        })

    # Convert the report into a Pandas DataFrame
    df: pd.DataFrame = pd.DataFrame(report)

    # Generate Excel file
    # Generate Excel file with styling
    excel_file_path: str = f"monthly_report_{month}_{year}.xlsx"
    # In the view
    with pd.ExcelWriter(excel_file_path, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Report')
        workbook = writer.book
        worksheet = writer.sheets['Report']

        # Apply styling
        apply_table_styles(worksheet, df)
        format_currency_columns(worksheet, df, currency_columns=['Opening Balance', 'Debit', 'Credit', 'Closing Balance'])

        # Return the file as a response
        with open(excel_file_path, "rb") as excel_file:
            response: HttpResponse = HttpResponse(
                excel_file.read(),
                content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
            response['Content-Disposition'] = f'attachment; filename="{excel_file_path}"'
            return response