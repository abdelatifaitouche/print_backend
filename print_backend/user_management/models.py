from django.db import models
from django.contrib.auth.models import AbstractUser
# Create your models here.


class Company(models.Model):

    company_name = models.CharField(max_length=100 , null=True , blank=True)
    contact_email = models.EmailField()
    company_phone = models.IntegerField()
    address = models.CharField(max_length=20) #later add wiliaya from that github
    date_joined = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.company_name




class CustomUser(AbstractUser):

    ROLES = (
        ('admin' , 'admin') , ('client' , 'client') , ('operator' , 'operator')
    )
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=150)
    phone_number = models.IntegerField(null=True , blank=True)
    role = models.CharField(max_length=20 , choices=ROLES , null=True , blank=True)
    company = models.ForeignKey(Company , on_delete=models.CASCADE , null=True , blank=True)
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username" , 'first_name' , 'last_name']


    def __str__(self):
        return self.username
