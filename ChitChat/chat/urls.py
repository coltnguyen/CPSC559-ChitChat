from django.urls import path
from . import views

urlpatterns = [
    path('<room_name>/', views.messages),
    path('register/', views.registerUser),
    path('login/', views.loginUser),
]
