from django.shortcuts import render,redirect
from .models import User,Product,Wishlist,Cart,Coupon,Transaction,Contact,Order,Adress
from django.conf import settings
from .paytm import generate_checksum, verify_checksum
from django.views.decorators.csrf import csrf_exempt
from django.core.mail import send_mail
import random
from django.http import JsonResponse

# Create your views here.

def validate_email(request):
    email=request.GET.get('email')
    data={
        'is_taken':User.objects.filter(email__iexact=email).exists()
    }
    return JsonResponse(data)

def validate_emaill(request):
    emaill=request.GET.get('emaill')
    data={
        'is_taken':User.objects.filter(email__iexact=emaill).exists()
    }
    return JsonResponse(data)


def initiate_payment(request):
    user=User.objects.get(email=request.session['email'])
    try:
        amount=int(request.POST['amount'])
    except:
        return render(request, 'pay.html', context={'error': 'Wrong Accound Details or amount'})

    transaction = Transaction.objects.create(made_by=user,amount=amount)
    transaction.save()
    merchant_key = settings.PAYTM_SECRET_KEY

    params = (
        ('MID', settings.PAYTM_MERCHANT_ID),
        ('ORDER_ID', str(transaction.order_id)),
        ('CUST_ID', str(transaction.made_by.email)),
        ('TXN_AMOUNT', str(transaction.amount)),
        ('CHANNEL_ID', settings.PAYTM_CHANNEL_ID),
        ('WEBSITE', settings.PAYTM_WEBSITE),
        # ('EMAIL', request.user.email),
        # ('MOBILE_N0', '9911223388'),
        ('INDUSTRY_TYPE_ID', settings.PAYTM_INDUSTRY_TYPE_ID),
        ('CALLBACK_URL', 'http://127.0.0.1:8000/callback/'),
        # ('PAYMENT_MODE_ONLY', 'NO'),
    )

    paytm_params = dict(params)
    checksum = generate_checksum(paytm_params,merchant_key)

    transaction.checksum = checksum
    transaction.save()

    email=request.session['email']
    user=User.objects.get(email=email)
    carts=Cart.objects.filter(user=user,payment_status=False)

    for a in carts:
        a.payment_status=True
        a.save()
    carts=Cart.objects.filter(user=user,payment_status=False)
    request.session['cart_count']=len(carts)

    Order.objects.create(
        user=user,
        fname=request.POST['fname'],
        lname=request.POST['lname'],
        mobile=request.POST['mobile'],
        email=request.POST['email'],
        state=request.POST['state'],
        district=request.POST['district'],
        taluka=request.POST['taluka'],
        city=request.POST['city'],
        address=request.POST['address'],
        sub_total=request.POST['sub_total'],
        discount=request.POST['discount'],
        coupon_discount=request.POST['coupon_discount'],
        tax=request.POST['tax'],
        shipping_cost=request.POST['shipping_cost'],
        grand_total=request.POST['amount'],
    )
    
    paytm_params['CHECKSUMHASH'] = checksum
    print('SENT: ', checksum)
    email=request.session['email']
    return render(request, 'redirect.html',context=paytm_params)


@csrf_exempt
def callback(request):
    if request.method == 'POST':
        received_data = dict(request.POST)
        paytm_params = {}
        paytm_checksum = received_data['CHECKSUMHASH'][0]
        for key, value in received_data.items():
            if key == 'CHECKSUMHASH':
                paytm_checksum = value[0]
            else:
                paytm_params[key] = str(value[0])
        # Verify checksum
        is_valid_checksum = verify_checksum(paytm_params,settings.PAYTM_SECRET_KEY,str(paytm_checksum))
        if is_valid_checksum:
            received_data['message'] = "Checksum Matched"
            return render(request, 'callback.html',context=received_data)
        else:
            received_data['message'] = "Checksum Mismatched"
            return render(request, 'callback.html',context=received_data)

def index(request):
    try:
        user=User.objects.get(email=request.session['email'])
        if user.usertype=='user':
            product=Product.objects.all()

            wishlists=Wishlist.objects.filter(user=user)
            pw=[]
            for w in wishlists:
                pw.append(w.product)

            carts=Cart.objects.filter(user=user,payment_status=False)
            pc=[]
            for c in carts:
                pc.append(c.product)

            sub_total=0
            for w in carts:
                sub_total=sub_total+w.total_price
            request.session['sub_total']=int(sub_total)
            return render(request,'index.html',{'product':product,'pc':pc,'pw':pw,'carts':carts})
        else:
            product=Product.objects.all()
            return render(request,'seller_index.html',{'product':product})
    except:
        product=Product.objects.all()
        return render(request,'index.html',{'product':product})

def seller_index(request):
    product=Product.objects.all()
    return render(request,'seller_index.html',{'product':product})

def my_account(request):
    return render(request,'my-account.html')

def our_location(request):
    return render(request,'our_location.html')
    
def contact_us(request):
    if request.method=='POST':
        Contact.objects.create(
            name=request.POST['name'],
            email=request.POST['email'],
            subject=request.POST['subject'],
            message=request.POST['message']
        )
        msg="Your message is successfully submiited"
        return render(request,'contact-us.html',{'msg':msg})
    else:
        return render(request,'contact-us.html')

def about(request):
    return render(request,'about.html')

def shop(request):
    try:
        user=User.objects.get(email=request.session['email'])
        product=Product.objects.all()

        wishlists=Wishlist.objects.filter(user=user)
        pw=[]
        for w in wishlists:
            pw.append(w.product)

        carts=Cart.objects.filter(user=user,payment_status=False)
        pc=[]
        for c in carts:
            pc.append(c.product)

        return render(request,'shop.html',{'pc':pc,'pw':pw,'product':product})

    except:
        product=Product.objects.all()
        return render(request,'shop.html',{'product':product})

def checkout(request):
    if request.method=="POST":
        try:
            user=User.objects.get(email=request.session['email'])
            ads=Adress.objects.get(user=user)  
            sub_total=request.POST['sub_total']
            discount=request.POST['discount']
            coupon_discount=request.POST['coupon_discount']
            tax=request.POST['tax']
            shipping_cost=request.POST['shipping_cost']
            grand_total=request.POST['grand_total']
            user=User.objects.get(email=request.session['email'])
            product=Cart.objects.filter(user=user,payment_status=False)
            return render(request,'checkout.html',{'product':product,'sub_total':sub_total,'discount':discount,'coupon_discount':coupon_discount,'tax':tax,'shipping_cost':shipping_cost,'grand_total':grand_total,'ads':ads})
        except:
            sub_total=request.POST['sub_total']
            discount=request.POST['discount']
            coupon_discount=request.POST['coupon_discount']
            tax=request.POST['tax']
            shipping_cost=request.POST['shipping_cost']
            grand_total=request.POST['grand_total']
            user=User.objects.get(email=request.session['email'])
            product=Cart.objects.filter(user=user,payment_status=False)
            return render(request,'checkout.html',{'product':product,'sub_total':sub_total,'discount':discount,'coupon_discount':coupon_discount,'tax':tax,'shipping_cost':shipping_cost,'grand_total':grand_total})            

    else:
        product=Cart.objects.filter(user=user,payment_status=False)
        return render(request,'checkout.html',{'product':product})
        
def shop_detail(request,pk):
    wishlist_flag=False
    cart_flag=False
    product=Product.objects.get(pk=pk)
    products=Product.objects.all()
    try:
        user=User.objects.get(email=request.session['email'])
        Wishlist.objects.get(user=user,product=product)
        wishlist_flag=True
    except:
        pass
    try:
        user=User.objects.get(email=request.session['email'])
        Cart.objects.get(user=user,product=product)
        cart_flag=True
    except:
        pass

    try:
        user=User.objects.get(email=request.session['email'])

        wishlists=Wishlist.objects.filter(user=user)
        pw=[]
        for w in wishlists:
            pw.append(w.product)

        carts=Cart.objects.filter(user=user,payment_status=False)
        pc=[]
        for c in carts:
            pc.append(c.product)
        return render(request,'shop-detail.html',{'product':product,'products':products,'wishlist_flag':wishlist_flag,'cart_flag':cart_flag,'pc':pc,'pw':pw})

    except:
        return render(request,'shop-detail.html',{'product':product,'products':products,'wishlist_flag':wishlist_flag,'cart_flag':cart_flag})

def service(request):
    return render(request,'service.html')

def login(request):
    if request.method=="POST":
        user=User()
        user.email=request.POST['email']
        try:
            user=User.objects.get(email=request.POST['email'])
            if user.password==request.POST['password']:
                if user.usertype=="user":
                    request.session['email']=user.email
                    request.session['fname']=user.fname
                    request.session['profile_pic']=user.profile_pic.url
                    wishlists=Wishlist.objects.filter(user=user)
                    request.session['wishlist_count']=len(wishlists)
                    carts=Cart.objects.filter(user=user,payment_status=False)
                    request.session['cart_count']=len(carts)
                    coupons=Coupon.objects.all()
                    request.session['coupon_count']=len(coupons)
                    return redirect('index')
                else:
                    request.session['email']=user.email
                    request.session['fname']=user.fname
                    request.session['profile_pic']=user.profile_pic.url
                    return redirect('seller_index')
            else:
                msgl="Incorrect Password"
                return render(request,'login.html',{'msgl':msgl,'user':user})    
        except:
            msgl="Invalid Email"
            return render(request,'login.html',{'msgl':msgl})
    else:
        return render(request,'login.html')

def signup(request):
    if request.method=="POST":
        try:
            User.objects.get(email=request.POST['email'])
            msg="Email Already Registered"
            return render(request,'login.html',{'msg':msg})
        except:
            if request.POST['password']==request.POST['cpassword']:
                User.objects.create(
                    fname=request.POST['fname'],
                    lname=request.POST['lname'],
                    mobile=request.POST['mobile'],
                    email=request.POST['emaill'],
                    address=request.POST['address'],
                    profile_pic=request.FILES['profile_pic'],
                    password=request.POST['password'],
                    usertype=request.POST['usertype']
                )
                msg="Successfully Registered"
                return render(request,'login.html',{'msg':msg})
            else:
                msg="Password & Confirm Password Does Not Matched"
                return render(request,'login.html',{'msg':msg})
    else:
        return render(request,'login.html')

def logout(request):
    try:
        del request.session['email']
        del request.session['fname']
        del request.session['profile_pic']
        del request.session['wishlist_count']
        del request.session['cart_count']
        del request.session['coupon_count']
        del request.session['sub_total']
        return redirect('index')
    except:
        return redirect('index')

def change_password(request):
    if request.method=="POST":
        user=User.objects.get(email=request.session['email'])
        if user.password==request.POST['old_password']:
            if request.POST['new_password']==request.POST['cnew_password']:
                user.password=request.POST['new_password']
                user.save()
                return redirect('logout')
            else:
                msg="New Password And Confirm New Password Does Not Matched"
                return render(request,'change_password.html',{'msg':msg})
        else:
            msg="Incorrect Old Password"
            return render(request,'change_password.html',{'msg':msg})
    else:
        return render(request,'change_password.html')

def seller_change_password(request):
    if request.method=="POST":
        user=User.objects.get(email=request.session['email'])
        if user.password==request.POST['old_password']:
            if request.POST['new_password']==request.POST['cnew_password']:
                user.password=request.POST['new_password']
                user.save()
                return redirect('logout')
            else:
                msg="New Password And Confirm New Password Does Not Matched"
                return render(request,'seller_change_password.html',{'msg':msg})
        else:
            msg="Incorrect Old Password"
            return render(request,'seller_change_password.html',{'msg':msg})
    else:
        return render(request,'seller_change_password.html')

def profile(request):
    user=User.objects.get(email=request.session['email'])
    if request.method=="POST":
        user.usertype=request.POST['usertype']
        user.fname=request.POST['fname']
        user.lname=request.POST['lname']
        user.mobile=request.POST['mobile']
        user.address=request.POST['address']
        try:
            user.profile_pic=request.FILES['profile_pic']
        except:
            pass
        user.save()
        request.session['fname']=user.fname
        request.session['profile_pic']=user.profile_pic.url
        msg="Profile Updated Successfully"
        return render(request,'profile.html',{'user':user,'msg':msg})
    else:
        return render(request,'profile.html',{"user":user})

def seller_profile(request):
    user=User.objects.get(email=request.session['email'])
    if request.method=="POST":
        user.usertype=request.POST['usertype']
        user.fname=request.POST['fname']
        user.lname=request.POST['lname']
        user.mobile=request.POST['mobile']
        user.address=request.POST['address']
        try:
            user.profile_pic=request.FILES['profile_pic']
        except:
            pass
        user.save()
        request.session['fname']=user.fname
        request.session['profile_pic']=user.profile_pic.url
        return render(request,'seller_profile.html',{'user':user})
    else:
        return render(request,'seller_profile.html',{"user":user})

def forgot_password(request):
    if request.method=="POST":
        try:
            user=User.objects.get(email=request.POST['email'])
            otp=random.randint(1000,9999)
            subject = 'OTP for Forgot Password'
            message = "Hello "+user.fname+" your OTP for forgot password is "+str(otp)
            email_from = settings.EMAIL_HOST_USER
            recipient_list = [user.email, ]
            send_mail( subject, message, email_from, recipient_list )
            return render(request,'verify_otp.html',{'otp':otp,'email':user.email})
        except:
            msg="Invalid Email"
            return render(request,'forgot_password.html',{'msg':msg})
    else:
        return render(request,'forgot_password.html')

def verify_otp(request):
    email=request.POST['email']
    otp=request.POST['otp']
    uotp=request.POST['uotp']
    if otp==uotp:
           return render(request,'update_password.html',{'email':email})
    else:
        msg="Incorrect OTP"
        return render(request,'verify_otp.html',{'email':email,'otp':otp,'msg':msg})

def update_password(request):
    email=request.POST['email']
    np=request.POST['new_password']
    cnp=request.POST['cnew_password']
        
    if np==cnp:
            user=User.objects.get(email=email)
            user.password=np
            user.save()
            return redirect('login')
    else:
        msg="New Password And Confirm New Password Does Not Matched"
        return render(request,'update_password.html',{'email':email,'msg':msg})

def seller_add_product(request):
    if request.method=="POST":
        seller=User.objects.get(email=request.session['email'])
        Product.objects.create(
            seller=seller,
            product_category=request.POST['product_category'],
            product_company=request.POST['product_company'],
            product_name=request.POST['product_name'],
            product_price=request.POST['product_price'],
            product_size=request.POST['product_size'],
            discount=request.POST['discount'],
            shipping_cost=request.POST['shipping_cost'],
            product_image=request.FILES['product_image']
        )
        msg="Product Successfully Added"
        return render(request,'seller_add_product.html',{'msg':msg})
    else:
        return render(request,'seller_add_product.html')

def seller_view_product(request):
    seller=User.objects.get(email=request.session['email'])
    products=Product.objects.filter(seller=seller)
    return render(request,'seller_view_product.html',{'products':products})

def seller_product_detail(request,pk):
    product=Product.objects.get(pk=pk)
    seller=User.objects.get(email=request.session['email'])
    products=Product.objects.filter(seller=seller)
    return render(request,'seller_product_detail.html',{'product':product,'products':products})

def seller_edit_product(request,pk):
    product=Product.objects.get(pk=pk)
    if request.method=="POST":
        product.product_category=request.POST['product_category']
        product.product_company=request.POST['product_company']
        product.product_name=request.POST['product_name']
        product.product_price=request.POST['product_price']
        product.product_size=request.POST['product_size']
        product.discount=request.POST['discount']
        product.shipping_cost=request.POST['shipping_cost']
        try:
            product.product_image=request.FILES['product_image']
        except:
            pass
        product.save()
        msg="Product Edited Successfully"
        return render(request,'seller_edit_product.html',{'product':product,'msg':msg})
    else:
        return render(request,'seller_edit_product.html',{'product':product})

def seller_product_delete(request,pk):
    product=Product.objects.get(pk=pk)
    product.delete()
    return redirect('seller_view_product')

def add_to_wishlist(request,pk):
    product=Product.objects.get(pk=pk)
    user=User.objects.get(email=request.session['email'])
    Wishlist.objects.create(user=user,product=product)
    return redirect('wishlist')

def wishlist(request):
    user=User.objects.get(email=request.session['email'])
    wishlists=Wishlist.objects.filter(user=user)
    request.session['wishlist_count']=len(wishlists)
    carts=Cart.objects.filter(user=user)
    pc=[]
    for a in carts:
        pc.append(a.product)
    return render(request,'wishlist.html',{'wishlists':wishlists,'pc':pc})

def remove_from_wishlist(request,pk):
    user=User.objects.get(email=request.session['email'])
    product=Product.objects.get(pk=pk)
    wishlist=Wishlist.objects.get(user=user,product=product)
    wishlist.delete()
    return redirect('wishlist')

def add_to_cart(request,pk):
    product=Product.objects.get(pk=pk)
    user=User.objects.get(email=request.session['email'])
    Cart.objects.create(
        user=user,
        product=product,
        product_price=product.product_price,
        total_price=product.product_price
    )
    return redirect('cart')

def cart(request):
    user=User.objects.get(email=request.session['email'])
    carts=Cart.objects.filter(user=user,payment_status=False)
    request.session['cart_count']=len(carts)

    coupon_discount=0
    tax=5
    sub_total=0
    discount=0
    shipping_cost=0
    for a in carts:
        sub_total=sub_total+a.total_price
        discount=discount+((a.product_price*a.product.discount/100)*(a.product_qty))
        shipping_cost=shipping_cost+a.product.shipping_cost
    grand_total=int(sub_total-discount+shipping_cost+tax)
    request.session['sub_total']=int(sub_total)

    return render(request,'cart.html',{'carts':carts,'sub_total':sub_total,'discount':discount,'shipping_cost':shipping_cost,'coupon_discount':coupon_discount,'tax':tax,'grand_total':grand_total})

def remove_from_cart(request,pk):
    user=User.objects.get(email=request.session['email'])
    product=Product.objects.get(pk=pk)
    cart=Cart.objects.get(user=user,product=product)
    cart.delete()
    return redirect('cart')

def change_qty(request,pk):
    cart=Cart.objects.get(pk=pk)
    product_qty=int(request.POST['product_qty'])
    cart.product_qty=product_qty
    cart.total_price=cart.product_price*cart.product_qty
    cart.save()
    return redirect('cart')

def apply_coupon(request):
    if request.method=="POST":
        user=User.objects.get(email=request.session['email'])
        carts=Cart.objects.filter(user=user,payment_status=False)
        request.session['cart_count']=len(carts)

        coupon_discount=0
        try:
            coupon=Coupon.objects.get(coupon_code=request.POST['coupon_code'])
            if request.POST['password']==coupon.password:
                coupon_discount=coupon.coupon_disc
                msg="Coupon discount added succefully"
            else:
                msg="incorrect password"
        except:
            msg="Incorrect Coupon Code"

        tax=5
        sub_total=0
        discount=0
        shipping_cost=0
        for a in carts:
            sub_total=sub_total+a.total_price
            discount=discount+((a.product_price*a.product.discount/100)*(a.product_qty))
            shipping_cost=shipping_cost+a.product.shipping_cost
        grand_total=sub_total-discount+shipping_cost-coupon_discount+tax
        if grand_total<=0:
            grand_total=0

        return render(request,'cart.html',{'carts':carts,'sub_total':sub_total,'discount':discount,'shipping_cost':shipping_cost,'grand_total':grand_total,'coupon_discount':coupon_discount,'tax':tax,'msg':msg})

    else:
        return render(request,'cart.html',{'carts':carts,'sub_total':sub_total,'discount':discount,'shipping_cost':shipping_cost,'grand_total':grand_total,'tax':tax})

def add_coupon(request):
    try:
        user=User.objects.get(email=request.session['email'])
        if user.email=='admin@gmail.com':
            coupon_code=str(str(chr(random.randint(65,90)))+str(random.randint(1000,9999))+str(chr(random.randint(65,90)))+str(random.randint(1000,9999))+str(chr(random.randint(65,90)))+str(random.randint(1000,9999)))
            w='abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ123456789!@#$&'
            passlen=8
            password=''.join(random.sample(w,passlen))

            if request.method=="POST":
                Coupon.objects.create(
                    coupon_code=request.POST['coupon_code'],
                    password=request.POST['password'],
                    coupon_disc=request.POST['coupon_disc']
                )
                msg="Coupon Add Successfully"
                coupons=Coupon.objects.all()
                request.session['coupon_count']=len(coupons)
                return render(request,'add_coupon.html',{'msg':msg,'coupon_code':coupon_code,'password':password})
            else:
                return render(request,'add_coupon.html',{'coupon_code':coupon_code,'password':password})
        else:
            return redirect('index')
    except:
        return redirect('index')

def price_filter(request):
    if request.method=="POST":
        ratio=request.POST['price']
        if ratio=='1':
            product=Product.objects.filter(product_price__lte=500)
            length=len(product)

            try:
                user=User.objects.get(email=request.session['email'])

                wishlists=Wishlist.objects.filter(user=user)
                pw=[]
                for w in wishlists:
                    pw.append(w.product)

                carts=Cart.objects.filter(user=user,payment_status=False)
                pc=[]
                for c in carts:
                    pc.append(c.product)
                return render(request,'shop.html',{'product':product,'ratio':ratio,'length':length,'pc':pc,'pw':pw})
            except:
                return render(request,'shop.html',{'product':product,'ratio':ratio,'length':length})
        
        elif ratio=='2':
            product=Product.objects.filter(product_price__gt=500,product_price__lte=1000)
            length=len(product)

            try:
                user=User.objects.get(email=request.session['email'])

                wishlists=Wishlist.objects.filter(user=user)
                pw=[]
                for w in wishlists:
                    pw.append(w.product)

                carts=Cart.objects.filter(user=user,payment_status=False)
                pc=[]
                for c in carts:
                    pc.append(c.product)
                return render(request,'shop.html',{'product':product,'ratio':ratio,'length':length,'pc':pc,'pw':pw})
            except:
                return render(request,'shop.html',{'product':product,'ratio':ratio,'length':length})
        
        elif ratio=='3':
            product=Product.objects.filter(product_price__gt=1000,product_price__lte=2000)
            length=len(product)

            try:
                user=User.objects.get(email=request.session['email'])

                wishlists=Wishlist.objects.filter(user=user)
                pw=[]
                for w in wishlists:
                    pw.append(w.product)

                carts=Cart.objects.filter(user=user,payment_status=False)
                pc=[]
                for c in carts:
                    pc.append(c.product)
                return render(request,'shop.html',{'product':product,'ratio':ratio,'length':length,'pc':pc,'pw':pw})
            except:
                    return render(request,'shop.html',{'product':product,'ratio':ratio,'length':length})
        
        elif ratio=='4':
            product=Product.objects.filter(product_price__gt=2000,product_price__lte=5000)
            length=len(product)

            try:
                user=User.objects.get(email=request.session['email'])

                wishlists=Wishlist.objects.filter(user=user)
                pw=[]
                for w in wishlists:
                    pw.append(w.product)

                carts=Cart.objects.filter(user=user,payment_status=False)
                pc=[]
                for c in carts:
                    pc.append(c.product)
                return render(request,'shop.html',{'product':product,'ratio':ratio,'length':length,'pc':pc,'pw':pw})
            except:
                    return render(request,'shop.html',{'product':product,'ratio':ratio,'length':length})
        
        elif ratio=='5':
            product=Product.objects.filter(product_price__gt=5000,product_price__lte=10000)
            length=len(product)

            try:
                user=User.objects.get(email=request.session['email'])

                wishlists=Wishlist.objects.filter(user=user)
                pw=[]
                for w in wishlists:
                    pw.append(w.product)

                carts=Cart.objects.filter(user=user,payment_status=False)
                pc=[]
                for c in carts:
                    pc.append(c.product)
                return render(request,'shop.html',{'product':product,'ratio':ratio,'length':length,'pc':pc,'pw':pw})
            except:
                    return render(request,'shop.html',{'product':product,'ratio':ratio,'length':length})
       
        elif ratio=='6':
            product=Product.objects.filter(product_price__gt=10000,product_price__lte=15000)
            length=len(product)

            try:
                user=User.objects.get(email=request.session['email'])

                wishlists=Wishlist.objects.filter(user=user)
                pw=[]
                for w in wishlists:
                    pw.append(w.product)

                carts=Cart.objects.filter(user=user,payment_status=False)
                pc=[]
                for c in carts:
                    pc.append(c.product)
                return render(request,'shop.html',{'product':product,'ratio':ratio,'length':length,'pc':pc,'pw':pw})
            except:
                    return render(request,'shop.html',{'product':product,'ratio':ratio,'length':length})
       
        elif ratio=='7':
            product=Product.objects.filter(product_price__gt=15000,product_price__lte=20000)
            length=len(product)

            try:
                user=User.objects.get(email=request.session['email'])

                wishlists=Wishlist.objects.filter(user=user)
                pw=[]
                for w in wishlists:
                    pw.append(w.product)

                carts=Cart.objects.filter(user=user,payment_status=False)
                pc=[]
                for c in carts:
                    pc.append(c.product)
                return render(request,'shop.html',{'product':product,'ratio':ratio,'length':length,'pc':pc,'pw':pw})
            except:
                    return render(request,'shop.html',{'product':product,'ratio':ratio,'length':length})
        
        elif ratio=='8':
            product=Product.objects.filter(product_price__gt=20000,product_price__lte=25000)
            length=len(product)

            try:
                user=User.objects.get(email=request.session['email'])

                wishlists=Wishlist.objects.filter(user=user)
                pw=[]
                for w in wishlists:
                    pw.append(w.product)

                carts=Cart.objects.filter(user=user,payment_status=False)
                pc=[]
                for c in carts:
                    pc.append(c.product)
                return render(request,'shop.html',{'product':product,'ratio':ratio,'length':length,'pc':pc,'pw':pw})
            except:
                    return render(request,'shop.html',{'product':product,'ratio':ratio,'length':length})
       
        elif ratio=='9':
            product=Product.objects.filter(product_price__gt=25000,product_price__lte=50000)
            length=len(product)

            try:
                user=User.objects.get(email=request.session['email'])

                wishlists=Wishlist.objects.filter(user=user)
                pw=[]
                for w in wishlists:
                    pw.append(w.product)

                carts=Cart.objects.filter(user=user,payment_status=False)
                pc=[]
                for c in carts:
                    pc.append(c.product)
                return render(request,'shop.html',{'product':product,'ratio':ratio,'length':length,'pc':pc,'pw':pw})
            except:
                    return render(request,'shop.html',{'product':product,'ratio':ratio,'length':length})
        
        elif ratio=='10':
            product=Product.objects.filter(product_price__gt=50000)
            length=len(product)

            try:
                user=User.objects.get(email=request.session['email'])

                wishlists=Wishlist.objects.filter(user=user)
                pw=[]
                for w in wishlists:
                    pw.append(w.product)

                carts=Cart.objects.filter(user=user,payment_status=False)
                pc=[]
                for c in carts:
                    pc.append(c.product)
                return render(request,'shop.html',{'product':product,'ratio':ratio,'length':length,'pc':pc,'pw':pw})
            except:
                return render(request,'shop.html',{'product':product,'ratio':ratio,'length':length})
        
        else:
            product=Product.objects.all()
            try:
                user=User.objects.get(email=request.session['email'])

                wishlists=Wishlist.objects.filter(user=user)
                pw=[]
                for w in wishlists:
                    pw.append(w.product)

                carts=Cart.objects.filter(user=user,payment_status=False)
                pc=[]
                for c in carts:
                    pc.append(c.product)
                return render(request,'shop.html',{'product':product,'pc':pc,'pw':pw})
            except:
                return render(request,'shop.html',{'product':product})
    else:
        return redirect('shop')

def sort_by(request):
    sorts=request.POST['sort']
    if request.POST['sort']=='1':
        product=Product.objects.all().order_by('-product_price')
        length=len(product)

        try:
            user=User.objects.get(email=request.session['email'])

            wishlists=Wishlist.objects.filter(user=user)
            pw=[]
            for w in wishlists:
                pw.append(w.product)

            carts=Cart.objects.filter(user=user,payment_status=False)
            pc=[]
            for c in carts:
                pc.append(c.product)
            return render(request,'shop.html',{'product':product,'sorts':sorts,'length':length,'pc':pc,'pw':pw})
        except:
            return render(request,'shop.html',{'product':product,'sorts':sorts,'length':length})
    
    elif request.POST['sort']=='2':
        product=Product.objects.all().order_by('product_price')
        length=len(product)

        try:
            user=User.objects.get(email=request.session['email'])

            wishlists=Wishlist.objects.filter(user=user)
            pw=[]
            for w in wishlists:
                pw.append(w.product)

            carts=Cart.objects.filter(user=user,payment_status=False)
            pc=[]
            for c in carts:
                pc.append(c.product)
            return render(request,'shop.html',{'product':product,'sorts':sorts,'length':length,'pc':pc,'pw':pw})
        except:
            return render(request,'shop.html',{'product':product,'sorts':sorts,'length':length})
    
    else:
        product=Product.objects.all()
        length=len(product)

        try:
            user=User.objects.get(email=request.session['email'])

            wishlists=Wishlist.objects.filter(user=user)
            pw=[]
            for w in wishlists:
                pw.append(w.product)

            carts=Cart.objects.filter(user=user,payment_status=False)
            pc=[]
            for c in carts:
                pc.append(c.product)
            return render(request,'shop.html',{'product':product,'sorts':sorts,'length':length,'pc':pc,'pw':pw})
        except:
            return render(request,'shop.html',{'product':product,'sorts':sorts,'length':length})

def search(request):
    search=request.POST['search']
    product=Product.objects.filter(product_name__icontains=search)
    length=len(product)     
    try:
        user=User.objects.get(email=request.session['email'])

        wishlists=Wishlist.objects.filter(user=user)
        pw=[]
        for w in wishlists:
            pw.append(w.product)

        carts=Cart.objects.filter(user=user,payment_status=False)
        pc=[]
        for c in carts:
            pc.append(c.product)
        return render(request,'shop.html',{'product':product,'length':length,'search':search,'pc':pc,'pw':pw})
    
    except:
        return render(request,'shop.html',{'product':product,'length':length,'search':search})

def product_sub_categories(request,product_name):
    product_sc=product_name
    product=Product.objects.filter(product_name__icontains=product_name)
    length=len(product)     
    try:
        user=User.objects.get(email=request.session['email'])

        wishlists=Wishlist.objects.filter(user=user)
        pw=[]
        for w in wishlists:
            pw.append(w.product)

        carts=Cart.objects.filter(user=user,payment_status=False)
        pc=[]
        for c in carts:
            pc.append(c.product)
        return render(request,'shop.html',{'product':product,'length':length,'product_sc':product_sc,'pc':pc,'pw':pw})

    except:
        return render(request,'shop.html',{'product':product,'length':length,'product_sc':product_sc})

def product_categories(request,product_category):
    product_sc=product_category
    product=Product.objects.filter(product_category=product_category)
    length=len(product)     
    try:
        user=User.objects.get(email=request.session['email'])

        wishlists=Wishlist.objects.filter(user=user)
        pw=[]
        for w in wishlists:
            pw.append(w.product)

        carts=Cart.objects.filter(user=user,payment_status=False)
        pc=[]
        for c in carts:
            pc.append(c.product)
        return render(request,'shop.html',{'product':product,'length':length,'product_sc':product_sc,'pw':pw,'pc':pc})

    except:
        return render(request,'shop.html',{'product':product,'length':length,'product_sc':product_sc})

def brand(request):
    brands=request.POST['brand']
    product=Product.objects.filter(product_company=request.POST['brand'])
    length=len(product)     
    try:
        user=User.objects.get(email=request.session['email'])

        wishlists=Wishlist.objects.filter(user=user)
        pw=[]
        for w in wishlists:
            pw.append(w.product)

        carts=Cart.objects.filter(user=user,payment_status=False)
        pc=[]
        for c in carts:
            pc.append(c.product)
        return render(request,'shop.html',{'product':product,'brands':brands,'length':length,'pw':pw,'pc':pc})

    except:
        return render(request,'shop.html',{'product':product,'brands':brands,'length':length})

def my_order(request):
    user=User.objects.get(email=request.session['email'])
    carts=Cart.objects.filter(user=user,order_status=False,payment_status=True)
    return render(request,'my_order.html',{'carts':carts})

def my_address(request):
    if request.method=="POST":
        user=User.objects.get(email=request.session['email'])
        try:
            ads=Adress.objects.get(user=user)
            ads.fname=request.POST['fname']
            ads.lname=request.POST['lname']
            ads.mobile=request.POST['mobile']
            ads.email=request.POST['email']
            ads.state=request.POST['state']
            ads.district=request.POST['district']
            ads.taluka=request.POST['taluka']
            ads.city=request.POST['city']
            ads.address=request.POST['address']
            ads.save()
            msg1='Your Address Is Successfully Updated'
            return render(request,'address.html',{'ads':ads,'msg1':msg1})
        except:
            Adress.objects.create(
            user=user,
            fname=request.POST['fname'],
            lname=request.POST['lname'],
            mobile=request.POST['mobile'],
            email=request.POST['email'],
            state=request.POST['state'],
            district=request.POST['district'],
            taluka=request.POST['taluka'],
            city=request.POST['city'],
            address=request.POST['address'],
            )
            ads=Adress.objects.get(user=user)
            msg2='Your Address Is Saved Successfully'
            return render(request,'address.html',{'ads':ads,'msg2':msg2})

    else:
        try:
            user=User.objects.get(email=request.session['email'])
            ads=Adress.objects.get(user=user)
            msg3='Update Your Address Here'
            return render(request,'address.html',{'ads':ads,'msg3':msg3})
        except:
            msg4='Add Your Address Here'
            return render(request,'address.html',{'msg4':msg4})
