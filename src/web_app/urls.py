from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='web_app-home'),
    path('inbox/', views.inbox, name='web_app-inbox'),
    path('message/', views.message, name='web_app-message'),
    path('getnewaddress', views.get_new_address, name='web_app-get_new_address'),
    path('deleteaddress', views.delete_address, name='web_app-delete_address'),
]