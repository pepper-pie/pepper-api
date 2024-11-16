from decimal import Decimal
from django.db.models.signals import post_save
from django.dispatch import receiver
from transactions.models import Transaction

def recalculate_running_balance(account):
    """
    Recalculate the running balance for all transactions of a given account.
    """
    transactions = Transaction.objects.filter(personal_account=account).order_by('date', 'id')

    running_balance: Decimal = Decimal(0)
    for transaction in transactions:
        if transaction.debit_amount:
            running_balance -= transaction.debit_amount
        if transaction.credit_amount:
            running_balance += transaction.credit_amount

        # Temporarily disconnect signal to prevent recursion
        post_save.disconnect(update_running_balance_on_save, sender=Transaction)
        transaction.running_balance = running_balance
        transaction.save(update_fields=['running_balance'])
        post_save.connect(update_running_balance_on_save, sender=Transaction)


@receiver(post_save, sender=Transaction)
def update_running_balance_on_save(sender, instance, **kwargs):
    """
    Update running balance after a transaction is saved.
    """
    recalculate_running_balance(instance.personal_account)