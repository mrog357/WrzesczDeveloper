import datetime

from django.db import models
from django.utils import timezone
from users.models import Patrol




class Question(models.Model):
    question_text = models.CharField(max_length=200)
    pub_date = models.DateTimeField('date published')

    def __str__(self):
        return self.question_text

    def was_published_recently(self):
        return self.pub_date >= timezone.now() - datetime.timedelta(days=1)


class Choice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    choice_text = models.CharField(max_length=200)
    votes = models.IntegerField(default=0)

    def __str__(self):
        return self.choice_text

class CashCode(models.Model):
    code_text = models.TextField(max_length=20)
    cash_value = models.IntegerField(default=100)
    is_used = models.BooleanField(default=False)

class Plot(models.Model):
    id = models.AutoField(primary_key=True)
    owner = models.ForeignKey(Patrol, on_delete=models.CASCADE)

    points = models.IntegerField()
    building = models. IntegerField(default=0)
    icon = models.ImageField(upload_to="plot_icons")
    pic_position_x = models.IntegerField()
    pic_position_y = models.IntegerField()
    pic_height = models.IntegerField()
    pic_width = models.IntegerField()
    points = models.IntegerField(default=0)


class Ownership(models.Model):
    plot = models.OneToOneField(Plot, on_delete=models.CASCADE)
    owner = models.ForeignKey(Plot, on_delete=models.CASCADE)


