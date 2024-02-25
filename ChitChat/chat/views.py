from django.contrib.auth import authenticate
from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from .models import User
from .serializers import UserSerializer
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
import json
import logging

logger = logging.getLogger(__name__)



# Create your views here.
def chat(request):
    return render(request, 'chat/chatroom.html')


@api_view(['POST'])
def loginUser(request):
    try:
        message = json.loads(request.body)
        username = message.get('userName')
        password = message.get('password')
    except json.JSONDecodeError:
        return Response(status=status.HTTP_400_BAD_REQUEST)
    except KeyError:
        return Response(status=status.HTTP_400_BAD_REQUEST)

    # Manually check the username and password against the database
    try:
        _ = User.objects.get(userName=username, password=password)
        # If the user is found, return a success response
        return JsonResponse({"username": username, "chatroom": "global"}, status=status.HTTP_200_OK)
    except User.DoesNotExist:
        # If the user is not found, return an unauthorized response
        return Response(status=status.HTTP_401_UNAUTHORIZED)


@api_view(['POST'])
def registerUser(request):
    # Check if the username already exists
    if User.objects.filter(userName=request.data.get('userName')).exists():
        return Response({'message': 'User already exists'}, status=status.HTTP_400_BAD_REQUEST)

    serializer = UserSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response({'message': 'Account Created'}, status=status.HTTP_201_CREATED)
    else:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
