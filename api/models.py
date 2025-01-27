from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db.models.signals import post_save
from django.contrib.auth.models import BaseUserManager
import random

class SellerManager(BaseUserManager):

    def get_by_natural_key(self, email):
        return self.get(email= email)
    

    
    def create_user(self, email, username, password=None, **extra_fields):

        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        extra_fields.setdefault('is_active', True) 
        user = self.model(email=email, username=username, **extra_fields)
        user.set_password(password) 
        user.save(using=self._db)
        return user

    def create_superuser(self, email, username, password=None, **extra_fields):
            """
            Create and return a superuser with the given email and password.
            """
            extra_fields.setdefault('is_staff', True)  # Required for superuser
            extra_fields.setdefault('is_superuser', True)  # Required for superuser

            if extra_fields.get('is_staff') is not True:
                raise ValueError("Superuser must have is_staff=True.")
            if extra_fields.get('is_superuser') is not True:
                raise ValueError("Superuser must have is_superuser=True.")

            return self.create_user(email, username, password, **extra_fields)


class BaseModel(models.Model):

    created_date = models.DateTimeField(auto_now_add= True)
    update_date = models.DateTimeField(auto_now_add= True)
    is_active = models.BooleanField(default = True)


class SellerCategory(BaseModel):

    seller_catname = models.CharField(max_length = 200)



class Seller(BaseModel, AbstractUser):

    objects = SellerManager()
    seller_category_choices = (
        ("Hotel","Hotel"),
        ("Hospital Canteen","Hospital Canteen"),
        ("College Canteen","College Canteen")
    )
    pin = models.CharField(max_length=6, unique=True, blank=True, null=True)
    seller_category = models.CharField(max_length=200,choices=seller_category_choices,
                            default="Hotel"
                            )
    
    def save(self, *args, **kwargs):
        if not self.pin:
            self.pin = self.generate_unique_pin()
        super().save(*args, **kwargs)

    def generate_unique_pin(self):
        return str(random.randint(100000, 999999))
    
    # def __str__(self):
    #     return self.user.username


class SellerAccount(BaseModel):
    
    username = models.CharField(max_length=200)
    bio = models.CharField(max_length = 200, null = True)
    profile_picture = models.ImageField(upload_to = "profilepictures", null = True)
    address = models.TextField(null = True)
    owner = models.OneToOneField(Seller, on_delete= models.CASCADE, related_name = "profile")
    phone_number = models.CharField(max_length = 10)
    description = models.TextField(null = True)


def create_profile(sender, instance, created, **kwargs):
    if created:
        SellerAccount.objects.create(owner = instance)  
post_save.connect(create_profile,Seller)



class FoodCategory(BaseModel):

    food_category_name = models.CharField(max_length = 200)
    description = models.CharField(max_length = 200)
    category_image = models.ImageField(upload_to='category_images', null = True)
    owner = models.ForeignKey(Seller, on_delete=models.CASCADE)
    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['owner', 'food_category_name'], name='unique_category')
        ]

class Food(BaseModel):

    food_name = models.CharField(max_length= 200)
    description = models.CharField(max_length= 200)
    food_image = models.ImageField(upload_to ='food_images', null= True)
    food_category_obj = models.ForeignKey(FoodCategory, on_delete=models.CASCADE)
    owner = models.ForeignKey(Seller, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places= 2)
    is_available = models.BooleanField(default = True)
    time_taken = models.PositiveIntegerField()


    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['owner', 'food_name'], name='unique_food')
        ]


class Table(models.Model):
    owner = models.ForeignKey(Seller, related_name='tables', on_delete=models.CASCADE)
    table_number = models.IntegerField(unique=True)
    is_occupied = models.BooleanField(default=False)

    # def __str__(self):
    #     return f"Table {self.table_number} at {self.restaurant.name}"


class Cart(models.Model):
    id = models.AutoField(primary_key=True)
    food_category = models.ForeignKey(FoodCategory,on_delete=models.CASCADE, null=True)
    food = models.ForeignKey(Food,on_delete=models.CASCADE, null=True)
    food_price = models.ForeignKey(Food,on_delete=models.CASCADE,null=True, related_name='food_price')
    table_number = models.ForeignKey(Table,on_delete=models.CASCADE, null=True)
    quantity = models.IntegerField(null=True,blank=True)
    prep_time = models.ForeignKey(Food,on_delete=models.CASCADE,null=True,related_name='preparation_time')
    status = models.CharField(max_length=50,choices=[('pending','Pending'),('delivered','Delivered')],null=True)


# class Checkout(models.Model):
#     table_number = models.ForeignKey(Cart,on_delete=models.CASCADE, null=True)
#     total_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
#     payment_status = models.CharField(
#         max_length=50,
#         choices=[('pending', 'Pending'), ('completed', 'Completed'), ('failed', 'Failed')],
#         default='pending'
#     )
#     transaction_id = models.CharField(max_length=100, null=True, blank=True)
#     payment_date = models.DateTimeField(auto_now_add=True)














