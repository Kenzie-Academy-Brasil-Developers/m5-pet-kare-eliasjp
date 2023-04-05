from django.shortcuts import render
from rest_framework.views import APIView, Request, Response, status

# Create your views here.
class TraitView(APIView):
    def get(self, request: Request):
        return Response("return get all TraitView", status.HTTP_200_OK)
    
    def post(self, request: Request):
        return Response("return post TraitView", status.HTTP_201_CREATED)
    
class TraitByIdView(APIView):
    def get(self, request: Request, id):
        return Response("return get by Id TraitByIdView", status.HTTP_200_OK)