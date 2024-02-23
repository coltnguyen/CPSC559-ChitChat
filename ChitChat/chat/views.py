from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from .models import User
from .serializers import UserSerializer
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status


# Create your views here.
def chat(request):
    return render(request, 'chat/chatroom.html')


@api_view(['GET'])
def loginUser(request):

    userName = request.query_params["userName"]
    password = request.query_params["password"]

    testUser = User.objects.filter(userName=userName)
    testUser = testUser.filter(password=password)

    if testUser:
        serializer = UserSerializer(testUser, many=True)  
        return JsonResponse(serializer.data, safe=False)       
    else:
        return Response(status=status.HTTP_400_BAD_REQUEST)
    

@api_view(['POST'])
def registerUser(request):  
    if request.method == "POST":
        serializer = UserSerializer(data = request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        



