from rest_framework import serializers
from groups.serializer import GroupSerializer
from traits.serializer import TraitSerializer
from pets.models import GenderChoices

class PetSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField()
    age = serializers.IntegerField()
    weight = serializers.FloatField()
    sex = serializers.ChoiceField(choices=GenderChoices.choices, default=GenderChoices.DEFAULT)
    group = GroupSerializer()
    traits = TraitSerializer(many=True)