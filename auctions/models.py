from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass

class Listings(models.Model):
    title = models.CharField(max_length=50)
    description = models.CharField(max_length=200)
    price = models.DecimalField(decimal_places=2, max_digits=10)
    image = models.ImageField(blank=True, null=True, upload_to="images/")
    data_stamp = models.DateTimeField()
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)


class Bids(models.Model):
    price = models.DecimalField(decimal_places=2, max_digits=10)
    listing_id = models.ForeignKey(Listings, on_delete=models.CASCADE)
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    

class Comments(models.Model):
    comment = models.CharField(max_length=200)
    data_stamp = models.DateTimeField()
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
