from django.db import models
from django.contrib.auth.models import User



class Patrol(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    image = models.ImageField(default="default.jpg", upload_to="profile_pics")
    points = models.PositiveIntegerField(default=0)
    people = models.PositiveIntegerField(default=0)
    usedcodes = models.TextField(default="", blank=True, null=True)
    built_buildings = models.TextField(default="", blank=True, null=True)
    number_of_built_buildings = models.PositiveIntegerField(default=0)
    cash = models.PositiveIntegerField(default=0)



    def __str__(self):
        return f"{self.user.username} Profile {self.id}"


class Building(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.TextField()
    built = models.BooleanField(default=False)
    image = models.URLField(blank=True, null=True)
    patrol = models.ForeignKey(Patrol, on_delete=models.CASCADE, blank=True, null=True)
    cost = models.PositiveIntegerField(default=100)
    generate_people = models.PositiveIntegerField(default=1)
    generate_points = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.name} Building {self.id}"


class Big_Building(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.TextField()
    how_much_built = models.PositiveIntegerField(default=0)
    size = models.PositiveIntegerField(default=4)
    image = models.URLField(
        default="https://ebilet-media.azureedge.net/media/18709/teatr-dom-git450.jpg",
        blank=True,
        null=True,
    )
    patrol = models.TextField(default="0", blank=True, null=True)
    cost = models.PositiveIntegerField(default=500)
    generate_people = models.PositiveIntegerField(default=2)
    generate_points = models.PositiveIntegerField(default=2)

    def __str__(self):
        return f"{self.name} Big_Building {self.id}"


from django.db import models

# Create your models here.
