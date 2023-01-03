from django.contrib import admin
from .models import User,Product,Wishlist,Cart,Coupon,Transaction,Contact,Order,Adress

# Register your models here.

admin.site.register(User)
admin.site.register(Product)
admin.site.register(Wishlist)
admin.site.register(Cart)
admin.site.register(Coupon)
admin.site.register(Transaction)
admin.site.register(Contact)
admin.site.register(Order)
admin.site.register(Adress)