from django.urls import path
from pets.views import PetView, PetByIdView, PetByTraitView

urlpatterns = [
    path("pets/", PetView.as_view()),
    path("pets/<int:pet_id>/", PetByIdView.as_view()),
    path("pets/<str:pet_trait>/", PetByTraitView.as_view())
]