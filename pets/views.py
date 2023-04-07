from django.shortcuts import render
from django.forms.models import model_to_dict
from rest_framework.views import APIView, Request, Response, status
from pets.serializer import PetSerializer
from pets.models import Pet
from groups.models import Group
from traits.models import Trait
from traits.serializer import TraitSerializer
from rest_framework.pagination import PageNumberPagination

# Create your views here.
class PetView(APIView, PageNumberPagination):
    def get(self, request: Request):
        dict_response = {}

        dict_response["count"] = Pet.objects.count()
        all_pets = Pet.objects.all()
        result_page = self.paginate_queryset(all_pets, request, view=self)
        serializer = PetSerializer(result_page, many=True)

        return self.get_paginated_response(serializer.data)
    
    def post(self, request: Request):
        serialized = PetSerializer(data=request.data)

        if not serialized.is_valid():
            return Response(serialized.errors, status.HTTP_400_BAD_REQUEST)
        
        response_info = dict(serialized.validated_data)
        group_key = dict(response_info.pop("group"))
        traits_key = response_info.pop("traits")

        find_pet = Pet.objects.filter(**response_info).first()
        if find_pet:
            return Response("Pet já existe", status.HTTP_409_CONFLICT)

        group_items = Group.objects.filter(scientific_name=group_key["scientific_name"]).first()

        if not group_items:
            group_items = Group.objects.create(**group_key)
            response_info["group"] = group_items
        else:
            response_info["group"] = group_items

        trait_list_appended = []
        for trait in traits_key:
            trait_item = Trait.objects.filter(name__iexact=dict(trait)["name"]).first()
            if not trait_item:
                trait_item = Trait.objects.create(**trait)
                trait_model_translate = model_to_dict(trait_item)
                trait_model_translate["created_at"] = trait_item.created_at
                trait_list_appended.append(trait_model_translate)
            else:
                trait_model_translate = model_to_dict(trait_item)
                trait_model_translate["created_at"] = trait_item.created_at
                trait_list_appended.append(trait_model_translate)


        if not find_pet:
            created_pet = Pet.objects.create(**response_info)
            response_info = model_to_dict(created_pet)

        to_dict_group = model_to_dict(group_items)
        to_dict_group["created_at"] = group_items.created_at
        response_info["group"] = to_dict_group

        response_info["traits"] = TraitSerializer(trait_list_appended, many=True).data

        return Response(response_info, status.HTTP_201_CREATED)