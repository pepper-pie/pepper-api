from django.http import JsonResponse
from transactions.models import Transaction
from django.db.models import Sum, F
from rest_framework.decorators import api_view


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

    # Fetch grouped data by category and subcategory
    expense_data = (
        Transaction.objects.filter(nominal_account="EXPENSE")
        .values("category__name", "sub_category__name")
        .annotate(
            debit=Sum("debit_amount", default=0),
            credit=Sum("credit_amount", default=0),
        )
        .filter(date__year=year, date__month=month)
        .order_by("category__name", "sub_category__name")
    )

    # Format the response for easy front-end consumption
    formatted_data = {}
    for row in expense_data:
        category = row["category__name"] or "(blank)"
        sub_category = row["sub_category__name"] or "(blank)"
        if category not in formatted_data:
            formatted_data[category] = {
                "debit": 0,
                "credit": 0,
                "sub_categories": [],
            }
        formatted_data[category]["debit"] += row["debit"]
        formatted_data[category]["credit"] += row["credit"]
        formatted_data[category]["sub_categories"].append({
            "sub_category": sub_category,
            "debit": row["debit"],
            "credit": row["credit"],
        })

    # Add grand total
    grand_total = {
        "debit": sum(row["debit"] for row in expense_data),
        "credit": sum(row["credit"] for row in expense_data),
    }

    return JsonResponse({"data": formatted_data, "grand_total": grand_total}, safe=False)