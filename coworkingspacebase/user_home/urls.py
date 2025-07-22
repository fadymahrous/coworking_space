from django.urls import path
from . import views

app_name = "user_home"

urlpatterns = [
    path('home/',views.welcome,name='home'),
    path('home/service/',views.services_view,name='service'),
    path('home/menue/',views.food_view,name='menue'),
    path('home/billview/',views.bill_view,name='billview'),
    path('home/opinion/',views.opinion_view,name='opinion'),
    path('home/cart/',views.cart_view,name='cart'),
    path('api/foodviewapi/',views.FoodViewAPI.as_view(),name='foodviewapi'),
    path('api/getbill/',views.GetBill.as_view(),name='getbill'),
    path('api/cartviewapi/',views.CartViewAPI.as_view(),name='cartviewapi'),
    path('api/cartviewsubmitapi/',views.CartViewSubmitAPI.as_view(),name='cartviewsubmitapi'),
]