from transactions.models import Transaction
from django.db.models import Sum

def categorised_expense_summary_data(month: int, year: int):
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
    
    return {"data": formatted_data, "grand_total": grand_total}