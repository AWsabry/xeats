from os import name
from django.urls import path,include
from . import views


urlpatterns = [    
    path('',views.index,name='index',),
    path('shop',views.shop,name='shop'),
    path('thankyou',views.thankyou,name='thankyou'),
    path('checkout',views.checkout,name='checkout'),
    path('contacts',views.contacts,name='contacts'),
    path('<int:id>',views.productDetails, name = 'productDetails'),
    path('email_verify', views.send_activate_mail, name='email_verify'),
    path('logout', views.logout, name='logout'),
    path('login', views.login, name='login'),
    path('reset_cart', views.reset_cart, name='reset_cart'),
]
