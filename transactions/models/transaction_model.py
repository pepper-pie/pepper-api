from django.db import models
from accounts.models import PersonalAccount


class Transaction(models.Model):
    date = models.DateField()
    narration = models.TextField()  # Narration field
    debit_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    credit_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    # Category and subcategory
    category = models.ForeignKey('Category', on_delete=models.SET_NULL, null=True, blank=True)
    sub_category = models.ForeignKey('SubCategory', on_delete=models.SET_NULL, null=True, blank=True)

    # Nominal account choices
    NOMINAL_ACCOUNT_CHOICES = [
        ('EXPENSE', 'Expense'),
        ('HOME', 'Home'),
        ('GAIN', 'Gain'),
        ('CREDIT_CARD', 'Credit Card'),
        ('SALARY', 'Salary'),
        ('INVESTMENT', 'Investment'),
        ('TRANSFER', 'Transfer'),
        ('OPENING_BALANCE', 'Opening Balance'),  # Add this choice
    ]
    nominal_account = models.CharField(
        max_length=50,
        choices=NOMINAL_ACCOUNT_CHOICES,
        default='EXPENSE'
    )

    personal_account = models.ForeignKey(PersonalAccount, on_delete=models.CASCADE)

    running_balance = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            # Allow duplicate narrations only when nominal_account is 'TRANSFER' and include the date
            models.UniqueConstraint(
                fields=['narration', 'personal_account', 'date', 'debit_amount', 'credit_amount'],
                name='unique_narration_nominal_date_except_transfer'
            )
        ]

    def __str__(self):
        return f"{self.date} - {self.narration}"