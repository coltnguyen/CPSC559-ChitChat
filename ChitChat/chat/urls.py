from django.urls import path, include
from . import views

urlpatterns = [
    path('chat/', views.chat, name='chat'),
    path('register/', views.registerUser, name='register'),
    path('login/', views.loginUser, name='login'),
]
