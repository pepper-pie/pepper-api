from django.contrib import admin
from .models import Transaction

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('date', 'narration', 'debit_amount', 'credit_amount', 'running_balance', 'personal_account')
    search_fields = ('narration', 'personal_account__name')
    list_filter = ('personal_account', 'date', 'category')