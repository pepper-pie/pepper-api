from django.db import models
from accounts.models import PersonalAccount

class Transaction(models.Model):
    # Date of the transaction
    date = models.DateField()
    
    # Narration (details of the transaction)
    narration = models.TextField()
    
    # Amounts (optional to allow null for debit/credit)
    debit_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    credit_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    running_balance = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)  # New Field
    
    # Category and subcategory
    category = models.CharField(max_length=255)
    subcategory = models.CharField(max_length=255, null=True, blank=True)
    
    # Personal account (e.g., HDFC Bank)
    personal_account = models.ForeignKey(PersonalAccount, on_delete=models.CASCADE)
    
    # Nominal account (e.g., Expense)
    nominal_account = models.CharField(max_length=255)
    
    # Additional metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.date} - {self.narration}"