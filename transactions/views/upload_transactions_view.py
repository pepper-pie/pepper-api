import traceback
from django.http import HttpResponse
import re
import pandas as pd
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from transactions.models import Transaction
from django.db import transaction  # Import Django's transaction module

from ..serializers import TransactionSerializer
import os
from django.core.files.storage import FileSystemStorage


@api_view(["POST"])
def upload_transactions(request):
    """
    API to upload transactions from a CSV/Excel file.
    Validates the data using serializers, creates transactions, or returns file with errors.
    """
    if 'file' not in request.FILES:
        return Response({"error": "No file provided."}, status=status.HTTP_400_BAD_REQUEST)

    # Save the file temporarily
    file = request.FILES['file']
    fs = FileSystemStorage()
    file_path = fs.save(file.name, file)
    full_path = fs.path(file_path)

    try:
        # Load the file using pandas
        if file.name.endswith(".csv"):
            df = pd.read_csv(full_path)
        elif file.name.endswith(".xlsx"):
            df = pd.read_excel(full_path)
        else:
            return Response({"error": "Unsupported file format. Use CSV or Excel."}, status=status.HTTP_400_BAD_REQUEST)

        # Validate rows using the serializer
        errors = []
        valid_rows = []

        def to_snake_case(key):
            """Convert keys to snake_case."""
            key = key.strip().lower().replace(" ", "_")
            return re.sub(r'[^a-z0-9_]', '', key)
        
        def nan_safe(value):
            return None if pd.isna(value) else value
        
        # Add an Error column to the DataFrame
        df['Error'] = None

        for idx, row in df.iterrows():
            cleaned_row = {
                to_snake_case(key): value.strip() if isinstance(value, str) else nan_safe(value)
                for key, value in row.to_dict().items()
            }

            # Use the serializer for validation and resolution
            serializer = TransactionSerializer(data=cleaned_row)
            if serializer.is_valid():
                validated_data = serializer.validated_data
                valid_rows.append(validated_data)
            else:
                # Add errors to the DataFrame for generating the error file
                df.at[idx, 'Error'] = str(serializer.errors)
                errors.append({"row": cleaned_row, "errors": serializer.errors})

        if errors:
            # Return the file with errors as a response
            df['Error'] = df.get('Error', None)
            error_file_path = generate_error_file(df, file.name)
            with open(error_file_path, "rb") as f:
                response = HttpResponse(f.read(), content_type="application/octet-stream")
                response['Content-Disposition'] = f'attachment; filename="{os.path.basename(error_file_path)}"'
                return response

        # Save valid rows to the database
        with transaction.atomic():
            for data in valid_rows:
                Transaction.objects.create(
                    date=data['date'],
                    narration=data['narration'],
                    debit_amount=data['debit_amount'] or 0.0,
                    credit_amount=data['credit_amount'] or 0.0,
                    category=data['category'],  # Resolved by the serializer
                    sub_category=data['sub_category'],  # Resolved by the serializer
                    personal_account=data['personal_account'],  # Resolved by the serializer
                    nominal_account=data['nominal_account'],
                    running_balance=0.00  # Default, signals can update this later
                )

        return Response({"message": "Transactions uploaded successfully."}, status=status.HTTP_201_CREATED)

    except Exception as e:
        return Response({
            "error": str(e),
            "traceback": traceback.format_exc()
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    finally:
        # Clean up temporary file
        if os.path.exists(full_path):
            os.remove(full_path)


def generate_error_file(df, original_file_name):
    """
    Generates a new file with errors included and returns the file path.
    """
    error_file_name = f"errors_{original_file_name}"
    error_file_path = os.path.join("media", error_file_name)
    if original_file_name.endswith(".xlsx"):
        df.to_excel(error_file_path, index=False)
    else:
        df.to_csv(error_file_path, index=False)
    return error_file_path