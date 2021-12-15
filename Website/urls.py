from django.urls import path,include
from . import views


urlpatterns = [    
    path('',views.index,name='index',),
    path('shop',views.shop,name='shop'),
    path('thankyou',views.thankyou,name='thankyou'),
    path('checkout',views.checkout,name='checkout'),
    path('contacts',views.contacts,name='contacts'),
    path('<int:id>',views.productDetails,name = 'productDetails')
]
