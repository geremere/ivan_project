from django.contrib import admin

from app.product.models import User, Rate, RateHistory

admin.site.register(User)

admin.site.register(Rate)

admin.site.register(RateHistory)
