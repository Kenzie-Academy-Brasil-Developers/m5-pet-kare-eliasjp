from django.db import models
from django.utils import timezone

# Create your models here.
class Trait(models.Model):
    name = models.CharField(max_length=20, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    pets = models.ManyToManyField("pets.Pet", related_name="traits")