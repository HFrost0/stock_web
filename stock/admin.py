from django.contrib import admin
from .models import Stock, Share, DailyBasic

# Register your models here.
admin.site.register(Stock)
admin.site.register(Share)
admin.site.register(DailyBasic)
