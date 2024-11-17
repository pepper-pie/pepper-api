import pandas as pd
from rest_framework import serializers
from transactions.models import Category, SubCategory
from accounts.models import PersonalAccount


from rest_framework import serializers
from transactions.models import Category, SubCategory
from accounts.models import PersonalAccount


from transactions.models import Transaction
from utils import datetime_utils

class TransactionSerializer(serializers.Serializer):
    date = serializers.DateField(input_formats=["%d-%m-%Y"])
    narration = serializers.CharField(max_length=255)
    debit_amount = serializers.DecimalField(max_digits=10, decimal_places=2, required=False, allow_null=True)
    credit_amount = serializers.DecimalField(max_digits=10, decimal_places=2, required=False, allow_null=True)
    running_balance = serializers.DecimalField(max_digits=10, decimal_places=2, required=False, allow_null=True)
    category = serializers.SlugRelatedField(
        queryset=Category.objects.all(),
        slug_field="name",  # Match by 'name'
        required=False,
        allow_null=True
    )
    sub_category = serializers.SlugRelatedField(
        queryset=SubCategory.objects.all(),
        slug_field="name",  # Match by 'name'
        required=False,
        allow_null=True
    )
    personal_account = serializers.SlugRelatedField(
        queryset=PersonalAccount.objects.all(),
        slug_field="name",  # Match by 'name'
        required=True  # Assume this field is mandatory
    )
    nominal_account = serializers.CharField()

    def validate_nominal_account(self, value):
        """Normalize nominal_account to match the database choices."""
        # Dynamically generate the map from NOMINAL_ACCOUNT_CHOICES
        nominal_account_map = {display.lower(): internal for internal, display in Transaction.NOMINAL_ACCOUNT_CHOICES}

        # Normalize input: strip whitespace and convert to lowercase
        normalized_value = value.strip().lower()

        # Resolve the value from the map
        resolved_value = nominal_account_map.get(normalized_value)

        if not resolved_value:
            raise serializers.ValidationError(f"Invalid nominal account: {value}.")
        
        return resolved_value

    def validate(self, data):
        """Custom validation for fields."""
        debit = data.get("debit_amount")
        credit = data.get("credit_amount")

        # Validate that only one of debit/credit is provided
        if debit and credit:
            raise serializers.ValidationError("Only one of Debit Amount or Credit Amount should have a value.")
        if not debit and not credit:
            raise serializers.ValidationError("Either Debit Amount or Credit Amount must have a value.")
        if debit and debit <= 0:
            raise serializers.ValidationError("Debit Amount must be positive.")
        if credit and credit <= 0:
            raise serializers.ValidationError("Credit Amount must be positive.")

        return data
    
    def to_internal_value(self, data):
        
        data['credit_amount'] = round(data['credit_amount'], 2) if isinstance(data['credit_amount'], (int, float)) else None
        data['debit_amount'] = round(data['debit_amount'], 2) if isinstance(data['debit_amount'], (int, float)) else None
        data['date'] = data['date'].strftime(datetime_utils.DEFAULT_DATE_FORMAT)
        return super().to_internal_value(data)