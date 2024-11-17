from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from transactions.models import Transaction
from transactions.serializers import TransactionSerializer

@api_view(["GET"])
def monthly_transactions(request):
    """
    API to fetch transactions for a given month and year.
    Returns columns: Date, Narration, Debit Amount, Credit Amount, Category,
    Sub Category, Personal Account, Nominal Account, and Running Balance.
    """
    # Extract month and year from query parameters
    month = request.GET.get('month')
    year = request.GET.get('year')

    if not month or not year:
        return Response({"error": "Both 'month' and 'year' query parameters are required."}, status=status.HTTP_400_BAD_REQUEST)

    try:
        month = int(month)
        year = int(year)
    except ValueError:
        return Response({"error": "'month' and 'year' must be valid integers."}, status=status.HTTP_400_BAD_REQUEST)

    # Query transactions for the given month and year
    transactions = Transaction.objects.filter(
        date__year=year,
        date__month=month
    )

    # Serialize the data
    serializer = TransactionSerializer(transactions, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)