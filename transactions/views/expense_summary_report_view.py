from django.http import JsonResponse
from transactions.models import Transaction
from django.db.models import Sum, F
from rest_framework.decorators import api_view


@api_view(["GET"])
def expense_summary(request):
    """
    API to return the expense summary for each account.
    Returns account name, total debit, total credit, and the net total (debit - credit).
    """
    month = request.GET.get("month")
    year = request.GET.get("year")

    if not month or not year:
        return JsonResponse({"error": "Please provide both month and year."}, status=400)

    try:
        month = int(month)
        year = int(year)
    except ValueError:
        return JsonResponse({"error": "Month and year must be integers."}, status=400)

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

    formatted_data = [
        {
            "account_name": row["personal_account__name"],
            "debit": row["debit"],
            "credit": row["credit"],
            "total": row["total"],
        }
        for row in expense_data
    ]

    return JsonResponse(formatted_data, safe=False)