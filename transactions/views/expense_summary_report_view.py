from django.http import JsonResponse
from rest_framework.decorators import api_view

from transactions.services.expense_summary_service import expense_summary_data


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

    expense_data = expense_summary_data(month, year)

    return JsonResponse(expense_data, safe=False)