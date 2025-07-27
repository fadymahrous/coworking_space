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
    path('v1/api/foodmenue/',views.FoodViewAPI.as_view(),name='api-foodmenue'),
    path('v1/api/cart/',views.CartViewAPI.as_view(),name='api-cart'),
    path('v1/api/order/',views.OrderAPI.as_view(),name='api-order'),
    path('v1/api/bill/',views.BillAPI.as_view(),name='api-bill'),
]