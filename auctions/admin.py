from django.contrib import admin
from . import models

# Register your models here.
admin.site.register(models.Listings)
admin.site.register(models.User)
admin.site.register(models.Comments)
admin.site.register(models.Bids)

