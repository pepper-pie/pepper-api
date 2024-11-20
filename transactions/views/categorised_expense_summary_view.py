from django.http import JsonResponse
from rest_framework.decorators import api_view

from transactions.services import categorised_expense_summary_data


@api_view(["GET"])
def categorised_expense_summary(request):
    """
    API to return the expense summary with category and subcategory breakdown.
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
    
    data = categorised_expense_summary_data(month, year)

   

    return JsonResponse(data, safe=False)