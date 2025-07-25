from django.urls import path
from . import views

app_name = "worker_home"

urlpatterns = [
    path('worker/',views.worker_view,name='worker'),
    path('worker/pick_shift/',views.pick_shift,name='pick_shift'),
    path('worker/ongoing_orders/',views.ongoing_orders,name='ongoing_orders'),
    path('worker/close_bill/',views.close_bill,name='close_bill'),
    path('worker/NotAutohrized/',views.not_authorized,name='notauthorized'),
]