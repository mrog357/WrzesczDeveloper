from django.contrib import admin

from .models import Question, Plot, CashCode

from users.models import Patrol

admin.site.register(Question)

admin.site.register(Plot)

admin.site.register(Patrol)

admin.site.register(CashCode)