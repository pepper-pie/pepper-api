from decimal import Decimal
from typing import List, Dict, Any
from django.db.models import Sum, F, DecimalField, QuerySet
from django.db.models.functions import Coalesce
from accounts.models import PersonalAccount
from transactions.models import Transaction
from datetime import datetime, timedelta
import pandas as pd

year = 2024
month = 9

first_day: datetime = datetime(year, month, 1)
last_day: datetime = (first_day + timedelta(days=31)).replace(day=1) - timedelta(days=1)

# Query for opening balances
opening_balances = Transaction.objects.filter(date__lt=first_day, personal_account_id=54).values(
    "personal_account__name"
).annotate(
    opening_balance=Coalesce(
            Sum(F("credit_amount"), output_field=DecimalField(max_digits=10, decimal_places=2)) 
            - Sum(F("debit_amount"), output_field=DecimalField(max_digits=10, decimal_places=2)),
        Decimal("0.00"),
    )
)

print(opening_balances)