from django.contrib import admin
from .models import *


# Register your models here.

admin.site.register(BaseModel)
admin.site.register(SellerCategory)
admin.site.register(Seller)
admin.site.register(SellerAccount)
admin.site.register(FoodCategory)
admin.site.register(Food)
admin.site.register(Table)