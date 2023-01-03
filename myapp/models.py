from django.db import models
from django.utils import timezone

# Create your models here.

class User(models.Model):
    fname=models.CharField(max_length=100)
    lname=models.CharField(max_length=100)
    mobile=models.PositiveBigIntegerField()
    email=models.EmailField()
    profile_pic=models.ImageField(upload_to='profile_pic/')
    address=models.CharField(max_length=200)
    password=models.CharField(max_length=100)
    usertype=models.CharField(max_length=100,default='user')

    def __str__(self):
        return self.fname+" "+self.lname+" - "+str(self.mobile)

class Product(models.Model):
    seller=models.ForeignKey(User,on_delete=models.CASCADE)
    product_category=models.CharField(max_length=100)
    product_company=models.CharField(max_length=100)
    product_name=models.CharField(max_length=100)
    product_price=models.PositiveBigIntegerField()
    product_size=models.CharField(max_length=100)
    product_image=models.ImageField(upload_to='Product_Image/',default="")
    discount=models.PositiveIntegerField(default=0)
    shipping_cost=models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.seller.fname+" - "+self.product_name

class Wishlist(models.Model):
    user=models.ForeignKey(User,on_delete=models.CASCADE)
    product=models.ForeignKey(Product,on_delete=models.CASCADE)
    date=models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.user.fname+" - "+self.product.product_name

class Cart(models.Model):
    user=models.ForeignKey(User,on_delete=models.CASCADE)
    product=models.ForeignKey(Product,on_delete=models.CASCADE)
    date=models.DateTimeField(default=timezone.now)
    product_price=models.PositiveIntegerField()
    product_qty=models.PositiveIntegerField(default=1)
    total_price=models.PositiveBigIntegerField()
    payment_status=models.BooleanField(default=False)
    order_status=models.BooleanField(default=False)
    
    def __str__(self):
        return self.user.fname+" - "+self.product.product_name

class Coupon(models.Model):
    coupon_code=models.CharField(max_length=20)
    password=models.CharField(max_length=20)
    coupon_disc=models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.coupon_code

class Transaction(models.Model):
    made_by = models.ForeignKey(User, related_name='transactions', 
                                on_delete=models.CASCADE)
    made_on = models.DateTimeField(auto_now_add=True)
    amount = models.IntegerField()
    order_id = models.CharField(unique=True, max_length=100, null=True, blank=True)
    checksum = models.CharField(max_length=100, null=True, blank=True)

    def save(self, *args, **kwargs):
        if self.order_id is None and self.made_on and self.id:
            self.order_id = self.made_on.strftime('PAY2ME%Y%m%dODR') + str(self.id)
        return super().save(*args, **kwargs)

class Contact(models.Model):
    name=models.CharField(max_length=100)
    email=models.EmailField()
    subject=models.CharField(max_length=150)
    message=models.TextField()

    def __str__(self):
        return self.name+' - '+self.email

class Order(models.Model):
    user=models.ForeignKey(User,on_delete=models.CASCADE)
    fname=models.CharField(max_length=100)
    lname=models.CharField(max_length=100)
    mobile=models.BigIntegerField()
    email=models.EmailField()
    state=models.CharField(max_length=100)
    district=models.CharField(max_length=100)
    taluka=models.CharField(max_length=100)
    city=models.CharField(max_length=100)
    address=models.CharField(max_length=150)
    sub_total=models.FloatField()
    discount=models.FloatField(default=0)
    coupon_discount=models.FloatField(default=0)
    tax=models.FloatField(default=0)
    shipping_cost=models.FloatField(default=0)
    grand_total=models.FloatField()
    date=models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.user.email

class Adress(models.Model):
    user=models.ForeignKey(User,on_delete=models.CASCADE)
    fname=models.CharField(max_length=100)
    lname=models.CharField(max_length=100)
    mobile=models.BigIntegerField()
    email=models.EmailField()
    state=models.CharField(max_length=100)
    district=models.CharField(max_length=100)
    taluka=models.CharField(max_length=100)
    city=models.CharField(max_length=100)
    address=models.CharField(max_length=150)

    def __str__(self):
        return self.fname+' '+self.lname