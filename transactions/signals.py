from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Transaction

def recalculate_running_balance(account):
    """
    Recalculate running balance for all transactions of a given account.
    """
    transactions = Transaction.objects.filter(
        personal_account=account
    ).order_by('date', 'id')

    running_balance = 0
    for transaction in transactions:
        if transaction.debit_amount:
            running_balance -= transaction.debit_amount
        if transaction.credit_amount:
            running_balance += transaction.credit_amount

        transaction.running_balance = running_balance
        transaction.save(update_fields=['running_balance'])


@receiver(post_save, sender=Transaction)
def update_running_balance_on_save(sender, instance, **kwargs):
    """Update running balance after a transaction is saved."""
    recalculate_running_balance(instance.personal_account)


@receiver(post_delete, sender=Transaction)
def update_running_balance_on_delete(sender, instance, **kwargs):
    """Recalculate running balance after a transaction is deleted."""
    recalculate_running_balance(instance.personal_account)