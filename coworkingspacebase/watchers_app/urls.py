from django.urls import path
from . import views

app_name = "watcher_home"

urlpatterns = [
    path('watcher/',views.watcher_view,name='watcher'),
    path('watcher/addcategory/',views.add_category,name='addcategory'),
    path('watcher/addgoods/',views.add_goods,name='addgoods'),
    path('watcher/NotAutohrized/',views.not_authorized,name='notauthorized'),
]