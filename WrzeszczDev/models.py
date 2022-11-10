import datetime

from django.db import models
from django.utils import timezone
from users.models import Patrol, Color


class CashCode(models.Model):
    id = models.AutoField(primary_key=True)
    code_text = models.CharField(max_length=20)
    cash_value = models.IntegerField(default=100)
    is_used = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.cash_value} {self.id}"


class Building(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50)
    cost = models.IntegerField()
    icon = models.FileField(upload_to="building_icons")
    base_points = models.IntegerField()
    image = models.ImageField(upload_to="building_imgs")
    available = models.BooleanField(default=True)
    is_limited = models.BooleanField(default=False)
    limit = models.IntegerField(null=True, blank=True)
    description = models.TextField( null=True, blank=True)
    color = models.ForeignKey(Color, on_delete=models.SET_NULL, null=True, blank=True)

    first_proximity_bonus = models.IntegerField()
    second_proximity_bonus = models.IntegerField()
    third_proximity_bonus = models.IntegerField()
    fourth_proximity_bonus = models.IntegerField()
    fifth_proximity_bonus = models.IntegerField()
    sixth_proximity_bonus = models.IntegerField()

    def __str__(self):
        return f"{self.name}"

    def bonus(self, proximity):
        match proximity:
            case 1:
                return self.first_proximity_bonus
            case 2:
                return self.second_proximity_bonus
            case 3:
                return self.third_proximity_bonus
            case 4:
                return self.fourth_proximity_bonus
            case 5:
                return self.fifth_proximity_bonus
            case 6:
                return self.sixth_proximity_bonus
            case other:
                return 0


class Plot(models.Model):
    id = models.AutoField(primary_key=True)
    building = models.ForeignKey(Building, on_delete=models.CASCADE, blank=True, null=True)
    pic_position_x = models.IntegerField()
    pic_position_y = models.IntegerField()
    pic_height = models.IntegerField()
    points = models.IntegerField(default=0)
    color = models.ForeignKey(Color, on_delete=models.SET_NULL, null=True)
    owner = models.ForeignKey(Patrol, on_delete=models.SET_NULL, null=True, blank=True)
    name = models.CharField(max_length=50, default="Nazwa")
    bonus = models.FloatField(default=1)

    def __str__(self):
        return f"{self.name}"

    def base_points(self):
        if self.building:
            return self.building.base_points
        else:
            return 0

    def add_bonus(self, bonus):
        self.bonus *= (1+bonus/100)
    def update_points(self):
        old = self.points
        self.points = int(self.base_points()*self.bonus)
        if self.owner:
            self.owner.points += self.points - old
            self.owner.save()
        self.save()

    def building_bonus_exist(self):
        for i in range (1,6):
            if self.building_bonus(i):
                return True
        return False

    def building_bonus(self, proximity):
        if self.building:
            return self.building.bonus(proximity)
        else:
            return 0


class Neighborhood(models.Model):
    base = models.OneToOneField(Plot, on_delete=models.CASCADE, primary_key=True)
    neighbour_1 = models.ForeignKey(Plot, blank=True, null=True, on_delete=models.SET_NULL, related_name='a')
    neighbour_2 = models.ForeignKey(Plot, blank=True, null=True, on_delete=models.SET_NULL, related_name='b')
    neighbour_3 = models.ForeignKey(Plot, blank=True, null=True, on_delete=models.SET_NULL, related_name='d')
    neighbour_4 = models.ForeignKey(Plot, blank=True, null=True, on_delete=models.SET_NULL, related_name='c')
    neighbour_5 = models.ForeignKey(Plot, blank=True, null=True, on_delete=models.SET_NULL, related_name='e')
    neighbour_6 = models.ForeignKey(Plot, blank=True, null=True, on_delete=models.SET_NULL, related_name='f')

    def neighbor(self, position):
        match position:
            case 1:
                return self.neighbour_1
            case 2:
                return self.neighbour_2
            case 3:
                return self.neighbour_3
            case 4:
                return self.neighbour_4
            case 5:
                return self.neighbour_5
            case 6:
                return self.neighbour_6
            case other:
                return None

    def __str__(self):
        return f"Sąsiedztwo   {self.base.name}"


class Factors(models.Model):
    actual = models.BooleanField(default=False)
    connection_bonus = models.IntegerField()
    map_background = models.ImageField(upload_to="media", default=None, null=True)


class Csvs(models.Model):
    file_name = models.FileField(upload_to='csvs')
    activated = models.BooleanField(default=False)

