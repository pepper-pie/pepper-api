from rest_framework import serializers
from transactions.models import Transaction

class TransactionSerializer(serializers.ModelSerializer):
    debit = serializers.DecimalField(source="debit_amount", max_digits=12, decimal_places=2, required=False)
    credit = serializers.DecimalField(source="credit_amount", max_digits=12, decimal_places=2, required=False)
    category = serializers.CharField(source="category.name", required=False)
    sub_category = serializers.CharField(source="sub_category.name", required=False)
    personal_account = serializers.CharField(source="personal_account.name", required=False)
    nominal_account = serializers.CharField(source="nominal_account.name", required=False)
    running_balance = serializers.DecimalField(source="running_balance", max_digits=12, decimal_places=2, required=False)

    class Meta:
        model = Transaction
        fields = [
            "date",
            "narration",
            "debit",
            "credit",
            "category",
            "sub_category",
            "personal_account",
            "nominal_account",
            "running_balance",
        ]