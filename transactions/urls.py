from django.urls import path

from .views import upload_transactions, monthly_report,  \
monthly_transactions, expense_summary, categorised_expense_summary

urlpatterns = [
    path('api/upload-transactions/', upload_transactions, name='upload-transactions'),
    path('api/monthly-report/', monthly_report, name='monthly-report'),
    path('api/expense-summary/', expense_summary, name='expense-summary'),
    path('api/categorised-expense-summary/', categorised_expense_summary, name='categorised-expense-summary'),
    path('api/transactions/', monthly_transactions, name='monthly_transactions'),
]