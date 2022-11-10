from django.db import models
from django.contrib.auth.models import User


class Color(models.Model):
    name = models.CharField(max_length=20, default="czarny")
    icon = models.FileField(upload_to="plot_icons", default="default.jpg")

    def __str__(self):
        return f"{self.name}"

class Patrol(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    image = models.ImageField(default="default.jpg", upload_to="profile_pics")
    points = models.PositiveIntegerField(default=0)
    cash = models.PositiveIntegerField(default=0)
    color = models.ForeignKey(Color, on_delete=models.SET_NULL, null=True)
    name = models.CharField(max_length=40, default="dd")




    def __str__(self):
        return f"{self.name}"




# Create your models here.
