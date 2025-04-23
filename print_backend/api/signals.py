from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import *

@receiver([post_save, post_delete], sender=OrderItem)
def update_order_status(sender, instance, **kwargs):
    order = instance.order
    items = order.items.all()

    if not items.exists():
        order.status = "pending"
    elif all(item.status == "printed" for item in items):
        if order.status != "completed":
            order.status = "completed"
    else:
        # Optional: set to something else if not all items are completed
        if order.status == "completed":
            order.status = "printing"

    order.save()
