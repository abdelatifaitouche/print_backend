from django.db import models

# Create your models here.
class Order(models.Model):
    STATUS_ENUM = [
        ("pending", "Pending"),
        ("approved", "Approved"),
        ("printing", "Printing"),
        ("completed", "Completed"),
        ("cancelled", "Cancelled"),
    ]

    user = models.ForeignKey(
        "user_management.CustomUser",
        on_delete=models.CASCADE,
        related_name="orders"
    )
    company = models.ForeignKey(
        "user_management.Company",
        on_delete=models.CASCADE,
        related_name="orders"
    )
    status = models.CharField(
        max_length=20, 
        choices=STATUS_ENUM, 
        default="pending"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order {self.id} by {self.user.username}"



class OrderItem(models.Model):

    STATUS_ENUM = (
        ('pending','pending') , 
        ('in_progress' , 'in_progress') , 
        ('printed' , 'printed') , 
        ('cancelled' , 'cancelled')
    )


    order = models.ForeignKey(Order, related_name="items", on_delete=models.CASCADE , null=True,blank=True)
    item_name = models.CharField(null=True , blank=True , max_length=255)
    status = models.CharField(max_length=20, choices=STATUS_ENUM, default="pending")
    #created_at = models.DateTimeField(auto_now_add=True)
    #file_path

    def __str__(self):
        return f"Item: {self.item_name} (x{self.order.order_id})"
