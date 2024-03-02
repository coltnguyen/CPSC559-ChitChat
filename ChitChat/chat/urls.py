from django.urls import path, include
from . import views

urlpatterns = [
    path('chat/', views.chat, name='chat'),
    path('register/', views.registerUser, name='register'),
    path('login/', views.loginUser, name='login'),
    path('message/create', views.createMessage, name='createMessage'),
    path('message/all/', views.allMessages, name='allMessages'),
]
