from django.shortcuts import render
from django.forms.models import model_to_dict
from rest_framework.views import APIView, Request, Response, status
from groups.serializer import GroupSerializer

# Create your views here.
class GroupView(APIView):
    def get(self, request: Request):
        return Response("oi", status.HTTP_200_OK)
    
    def post(self, request: Request):
        serialized = GroupSerializer(data=request.data)

        if not serialized.is_valid():
            return Response(serialized.errors, status.HTTP_400_BAD_REQUEST)

        return Response(serialized.validated_data, status.HTTP_201_CREATED)
    
class GroupIdView(APIView):
    def get(self, request: Request, id):
        return Response({f"{id}"}, status.HTTP_200_OK)