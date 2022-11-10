from django.contrib import admin

from .models import Plot, CashCode, Building, Neighborhood, Factors, Csvs

from users.models import Patrol, Color



admin.site.register(Plot)

admin.site.register(Patrol)

admin.site.register(CashCode)

admin.site.register(Building)

admin.site.register(Neighborhood)



admin.site.register(Color)

admin.site.register(Factors)

admin.site.register(Csvs)
