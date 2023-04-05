from django.shortcuts import render
from rest_framework.views import APIView, Request, Response, status
from pets.serializer import PetSerializer

# Create your views here.
class PetView(APIView):
    def get(self, request: Request):
        return Response("call pet view", status.HTTP_200_OK)
    
    def post(self, request: Request):
        serialized = PetSerializer(data=request.data)

        if not serialized.is_valid():
            return Response(serialized.errors, status.HTTP_400_BAD_REQUEST)
        
        print(dict(serialized.validated_data))

        return Response("call post pet view", status.HTTP_201_CREATED)