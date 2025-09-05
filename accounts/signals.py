from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Commission, CashoutRequest


@receiver(post_save, sender=Commission)
def update_user_commission_balance(sender, instance, created, **kwargs):
    user = instance.user

    if created and instance.status == "pending":
        # Add commission on creation
        user.commission_balance += instance.amount
        user.save()

    elif not created:
        # If status was changed in admin
        if instance.status == "cancelled":
            # If commission is cancelled, remove it from balance
            user.commission_balance -= instance.amount
            user.save()


@receiver(post_save, sender=CashoutRequest)
def handle_cashout_approval(sender, instance, created, **kwargs):
    user = instance.user

    # Only act when status is approved AND not already processed
    if not created and instance.status == "approved" and not instance.processed:
        # Deduct from commission balance
        if user.commission_balance >= instance.requested_amount:
            user.commission_balance -= instance.requested_amount
            user.save()

            # Mark this request as processed so it won't run again
            instance.processed = True
            instance.save(update_fields=["processed"])

