from django.db import models

class PersonalAccount(models.Model):
    name = models.CharField(max_length=255, unique=True)  # e.g., HDFC Bank
    account_type = models.CharField(max_length=255, null=True, blank=True)  # e.g., Credit Card, Savings Account
    description = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.name