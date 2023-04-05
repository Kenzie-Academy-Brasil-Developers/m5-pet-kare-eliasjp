from groups.views import GroupView, GroupIdView
from django.urls import path

urlpatterns = [
    path("groups/", GroupView.as_view()),
    path("groups/<int:id>/", GroupIdView.as_view())
]