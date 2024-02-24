from django.urls import path
from . import views

urlpatterns = [
    # path('chat/', views.chat, name='chat'),
    path('register/', views.registerUser),
    path('login/', views.loginUser),
]