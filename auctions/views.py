from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django import forms
from .models import Listings, User, Bids, Comments
from django.utils.timezone import now
import time

from . import models

STATIC_VERSION = int(time.time()) 

class listingForm(forms.Form):
    title = forms.CharField(max_length=50)
    description = forms.CharField(max_length=200, widget=forms.Textarea(
        attrs={"rows": 10, "cols": 50, "placeholder": "Describe the item here!"}
    ))
    price = forms.DecimalField(decimal_places=2, max_digits=10)
    image = forms.ImageField()


def index(request): 
    listings = models.Listings.objects.all()
    return render(request, "auctions/index.html", {
        "listings": listings,
        "STATIC_VERSION": STATIC_VERSION
    })

def create(request):
    if request.method == 'POST':
        form = listingForm(request.POST, request.FILES)
        if form.is_valid():
            data = form.cleaned_data
            s = Listings.objects.create(
                title=data.title,
                description=data.description,
                price=data.price,
                data_stamp=now(),
                user_id=request.user
                # Adicionar o campo imagem e testar a inserção de dados!!!
                )
            s.save()


    return render(request, "auctions/create.html", {
        "forms": listingForm,
        "STATIC_VERSION": STATIC_VERSION
    })


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password.",
                "STATIC_VERSION": STATIC_VERSION
            })
    else:
        return render(request, "auctions/login.html", {
            "STATIC_VERSION": STATIC_VERSION
        })


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match.",
                "STATIC_VERSION": STATIC_VERSION
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken.",
                "STATIC_VERSION": STATIC_VERSION
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")