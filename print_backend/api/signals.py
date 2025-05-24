from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.core.exceptions import ObjectDoesNotExist
from .models import OrderItem

@receiver([post_save, post_delete], sender=OrderItem)
def update_order_status(sender, instance, **kwargs):
    try:
        order = instance.order
    except ObjectDoesNotExist:
        return  # The order was already deleted, do nothing

    items = order.items.all()

    if not items.exists():
        order.status = "pending"
    elif all(item.status == "printed" for item in items):
        if order.status != "completed":
            order.status = "completed"
    else:
        if order.status == "completed":
            order.status = "printing"

    order.save()
