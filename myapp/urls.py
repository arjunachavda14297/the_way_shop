from django.urls import path
from . import views

urlpatterns = [
    path('',views.index,name='index'),
    path('my_account/',views.my_account,name='my_account'),
    path('contact_us/',views.contact_us,name='contact_us'),
    path('about/',views.about,name='about'),
    path('shop/',views.shop,name='shop'),
    path('cart/',views.cart,name='cart'),
    path('checkout/',views.checkout,name='checkout'),
    path('wishlist/',views.wishlist,name='wishlist'),
    path('shop_detail/<int:pk>/',views.shop_detail,name='shop_detail'),
    path('service/',views.service,name='service'),
    path('login/',views.login,name='login'),
    path('signup/',views.signup,name='signup'),
    path('logout/',views.logout,name='logout'),
    path('change_password/',views.change_password,name='change_password'),
    path('profile/',views.profile,name='profile'),
    path('forgot_password/',views.forgot_password,name='forgot_password'),
    path('verify_otp/',views.verify_otp,name='verify_otp'),
    path('update_password/',views.update_password,name='update_password'),
    path('seller_index/',views.seller_index,name='seller_index'),
    path('seller_add_product/',views.seller_add_product,name='seller_add_product'),
    path('seller_view_product/',views.seller_view_product,name='seller_view_product'),
    path('seller_change_password/',views.seller_change_password,name='seller_change_password'),
    path('seller_profile/',views.seller_profile,name='seller_profile'),
    path('seller_product_detail/<int:pk>/',views.seller_product_detail,name='seller_product_detail'),
    path('seller_edit_product/<int:pk>/',views.seller_edit_product,name='seller_edit_product'),
    path('seller_product_delete/<int:pk>/',views.seller_product_delete,name='seller_product_delete'),
    path('add_to_wishlist/<int:pk>/',views.add_to_wishlist,name='add_to_wishlist'),
    path('remove_from_wishlist/<int:pk>/',views.remove_from_wishlist,name='remove_from_wishlist'),
    path('add_to_cart/<int:pk>/',views.add_to_cart,name='add_to_cart'),
    path('remove_from_cart/<int:pk>/',views.remove_from_cart,name='remove_from_cart'),
    path('change_qty/<int:pk>/',views.change_qty,name='change_qty'),
    path('apply_coupon/',views.apply_coupon,name='apply_coupon'),
    path('add_coupon/',views.add_coupon,name='add_coupon'),
    path('price_filter/',views.price_filter,name='price_filter'),
    path('sort_by/',views.sort_by,name='sort_by'),
    path('search/',views.search,name='search'),
    path('product_sub_categories/<str:product_name>/',views.product_sub_categories,name='product_sub_categories'),
    path('product_categories/<str:product_category>/',views.product_categories,name='product_categories'),
    path('pay/',views.initiate_payment, name='pay'),
    path('callback/',views.callback, name='callback'),
    path('brand/',views.brand,name='brand'),
    path('ajax/validate_email/',views.validate_email,name='validate_email'),
    path('ajax/validate_emaill/',views.validate_emaill,name='validate_emaill'),
    path('my_order/',views.my_order,name='my_order'),
    path('my_address/',views.my_address,name='my_address'),
    path('our_location/',views.our_location,name='our_location'),
]