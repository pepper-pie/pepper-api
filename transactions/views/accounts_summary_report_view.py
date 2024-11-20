from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.http import HttpResponse
from ..services.account_summary_service import get_account_summary_report, get_monthly_report_data
import pandas as pd
import io


@api_view(["GET"])
def monthly_report(request):
    """
    Generate a monthly report of transactions for each account.
    Returns the report in JSON, Excel, or CSV format based on the 'format' query parameter.
    """
    # Get query parameters
    month = request.GET.get("month")
    year = request.GET.get("year")
    output_format = request.GET.get("format", "json").lower()  # Default to JSON

    if not month or not year:
        return Response({"error": "Please provide both month and year."}, status=400)

    try:
        month_int = int(month)
        year_int = int(year)
    except ValueError:
        return Response({"error": "Month and year must be integers."}, status=400)

    if output_format == "json":
        # Fetch the data
        report_data = get_monthly_report_data(month_int, year_int)

        if not report_data:
            return Response({"error": "No data available for the given month and year."}, status=404)
            # Return raw keys for JSON
        return Response(report_data, status=200)

    if output_format == "excel":
        # Generate an Excel file
        df = get_account_summary_report(month, year)
        with io.BytesIO() as buffer:
            with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
                df.to_excel(writer, index=False, sheet_name="Report")
            buffer.seek(0)
            response = HttpResponse(
                buffer,
                content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )
            response["Content-Disposition"] = f'attachment; filename="monthly_report_{month}_{year}.xlsx"'
            return response

    elif output_format == "csv":
        # Generate a CSV file
        df = get_account_summary_report(month, year)
        with io.StringIO() as buffer:
            df.to_csv(buffer, index=False)
            buffer.seek(0)
            response = HttpResponse(
                buffer,
                content_type="text/csv",
            )
            response["Content-Disposition"] = f'attachment; filename="monthly_report_{month}_{year}.csv"'
            return response

    else:
        return Response({"error": "Unsupported format. Use 'json', 'excel', or 'csv'."}, status=400)