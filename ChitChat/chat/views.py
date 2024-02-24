from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from .models import User
from .serializers import UserSerializer
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status


# This was used in initial stages for testing purposes.
# However, this server was modified to be an API server that handles
# data retreival/modification with the database. As such it will not serve
# static files. All visual rendering will be dealt with by the client server code.
# This is due to the fact that daphne, the ASGI server we are using does not support
# returning static files.
# def chat(request):
#     return render(request, 'chat/chatroom.html')

@api_view(['GET'])
def messages(request, room_name):
    # if the cr exists: find and return all messages
    # else: return 404 does not exist to indicate cr not found
    return Response(status=status.HTTP_400_BAD_REQUEST)


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




