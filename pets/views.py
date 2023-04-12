from django.shortcuts import render
from django.forms.models import model_to_dict
from rest_framework.views import APIView, Request, Response, status
from pets.serializer import PetSerializer
from pets.models import Pet
from groups.models import Group
from groups.serializer import GroupSerializer
from traits.models import Trait
from traits.serializer import TraitSerializer
from rest_framework.pagination import PageNumberPagination

# Create your views here.
class PetView(APIView, PageNumberPagination):
    def get(self, request: Request):
        dict_response = {}

        if not request.query_params.get("trait"):
            dict_response["count"] = Pet.objects.count()
            all_pets = Pet.objects.all()
            result_page = self.paginate_queryset(all_pets, request, view=self)
            serializer = PetSerializer(result_page, many=True)
            return self.get_paginated_response(serializer.data)
        else:
            find_trait = Trait.objects.filter(name=request.query_params.get("trait")).first()
            dict_trait = model_to_dict(find_trait)
            result_page = self.paginate_queryset(dict_trait["pets"], request, view=self)
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
            
        if not find_pet:
            created_pet = Pet.objects.create(**response_info)
            response_info = model_to_dict(created_pet)

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
            trait_item.pets.add(response_info["id"])

        to_dict_group = model_to_dict(group_items)
        to_dict_group["created_at"] = group_items.created_at
        response_info["group"] = to_dict_group

        response_info["traits"] = TraitSerializer(trait_list_appended, many=True).data

        return Response(response_info, status.HTTP_201_CREATED)
    
class PetByIdView(APIView):
    def get(self, request: Request, pet_id):
        find_pet = Pet.objects.filter(id=pet_id).first()
        if not find_pet:
            return Response({"detail": "Not found."}, status.HTTP_404_NOT_FOUND)
        pet_model = model_to_dict(find_pet)
        
        find_group = Group.objects.filter(id=model_to_dict(find_pet)["group"]).first()
        pet_model["group"] = model_to_dict(find_group)
        pet_model["group"]["created_at"] = find_group.created_at

        find_traits = Trait.objects.filter(pets=pet_id)
        if len(find_traits):
            pet_model["traits"] = [model_to_dict(trait) for trait in find_traits]
        else:
            pet_model["traits"] = []
        
        return Response(pet_model, status.HTTP_200_OK)

    def delete(self, request: Request, pet_id):
        find_pet = Pet.objects.filter(id=pet_id)
        if not find_pet:
            return Response({"detail": "Not found."}, status.HTTP_404_NOT_FOUND)
        
        find_pet.delete()
        return Response(None, status.HTTP_204_NO_CONTENT)
    
    def patch(self, request: Request, pet_id):
        find_pet = Pet.objects.filter(id=pet_id).first()
        if not find_pet:
            return Response({"detail": "Not found."}, status.HTTP_404_NOT_FOUND)
        
        serialize = PetSerializer(data=request.data, partial=True)
        serialize.is_valid(raise_exception=True)
        serialized_data = dict(serialize.validated_data)

        if serialized_data.get("group"):
            pet_group = dict((serialized_data).pop("group"))
            find_group = Group.objects.filter(scientific_name=pet_group["scientific_name"]).first()
            if not find_group:
                find_group = Group.objects.create(**pet_group)
            find_pet.group = find_group

        if serialized_data.get("traits"):
            trait_list = []
            pet_trait = (serialized_data).pop("traits")
            for trait in pet_trait:
                trait_dict = dict(trait)
                find_trait = Trait.objects.filter(name__iexact=trait_dict["name"]).first()
                if not find_trait:
                    find_trait = Trait.objects.create(**trait_dict)
                trait_list.append(find_trait)
            find_pet.traits.set(trait_list)

        for key, value in serialized_data.items():
            setattr(find_pet, key, value)

        find_pet.save()

        returning_dict = PetSerializer(find_pet)

        return Response(returning_dict.data, status.HTTP_200_OK)
    
    
class PetByTraitView(APIView, PageNumberPagination):
    def get(self, request: Request, pet_trait):
        find_trait = Trait.objects.filter(name=pet_trait)
        if not find_trait:
            return Response({"detail": "Not found."}, status.HTTP_404_NOT_FOUND)
        
        result_page = self.paginate_queryset(model_to_dict(find_trait[0])["pets"], request, view=self)
        serializer = TraitSerializer(result_page, many=True)

        return self.get_paginated_response(serializer.data)