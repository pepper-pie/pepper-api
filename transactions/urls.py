from django.urls import path

from .views import upload_transactions, account_summary_report,  \
monthly_transactions, expense_summary, categorised_expense_summary, \
monthly_reports_excel

urlpatterns = [
    path('api/upload-transactions/', upload_transactions, name='upload-transactions'),
    path('api/account-summary-report/', account_summary_report, name='monthly-report'),
    path('api/expense-summary/', expense_summary, name='expense-summary'),
    path('api/categorised-expense-summary/', categorised_expense_summary, name='categorised-expense-summary'),
    path('api/transactions/', monthly_transactions, name='monthly_transactions'),
    path('api/monthly-reports/', monthly_reports_excel, name='monthly-reports-excel'),
]