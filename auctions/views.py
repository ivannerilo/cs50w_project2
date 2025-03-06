from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django import forms
from .models import Listings, User, Bids, Comments, Watchlist, CATEGORIES
from django.utils.timezone import now
from .utils import actual_index, who_winning, in_watchlist, lenth_listings
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
    category = forms.ChoiceField(choices=CATEGORIES)


class bidsForm(forms.Form):
    bid = forms.DecimalField(
        label='',
        decimal_places=2,
        max_digits=10,
        widget=forms.TextInput(attrs={"class": "bid_form"}))

class commentForm(forms.Form):
    comment = forms.CharField(max_length=200, label="", widget=forms.TextInput(attrs={"class": "comment_form"}))


def index(request):
    if request.method == 'POST':
        if request.user.is_authenticated:
            l = Listings.objects.get(pk=request.POST["watchlist"])
            w = Watchlist(
                listing_id = l,
                user_id = request.user
            )
            w.save()
            return HttpResponseRedirect(reverse("index"))

    listings = models.Listings.objects.filter(is_active=True) #Adicionar verificações em outros lugares também.
    return render(request, "auctions/index.html", {
        "listings": listings,
        "STATIC_VERSION": STATIC_VERSION
    })

def show_categories(request):
    return render(request, "auctions/categories.html", {
        "categories": CATEGORIES,
        "STATIC_VERSION": STATIC_VERSION
    })

def category(request, category):
    listings = Listings.objects.filter(category=category)
    return render(request, "auctions/index.html", {
        "listings": listings,
        "STATIC_VERSION": STATIC_VERSION
    })

def watch_list(request):
    listings = Listings.objects.filter(id__in=Watchlist.objects.filter(user_id=request.user).values('listing_id'))
    return render(request, "auctions/index.html", {
        "listings": listings,
        "STATIC_VERSION": STATIC_VERSION
    })

def show_listing(request, pk):
    listing = Listings.objects.get(pk=pk) #Possível join
    comments = Comments.objects.filter(listing_id=listing)
    bids = Bids.objects.filter(listing_id=listing)
    auction_winner = who_winning(bids)
    watchlist = in_watchlist(listing, request.user)

    context = {
        "listing": listing,
        "comments": comments,
        "bids": len(bids),
        "bid_form": bidsForm(),
        "comment_form": commentForm(),
        "in_watchlist": watchlist,
        "request_user": request.user,
        "STATIC_VERSION": STATIC_VERSION
    }

    if request.method == "POST": 
        if request.user.is_authenticated:
            match request.POST.keys():
                case keys if "bid" in keys:
                    form = bidsForm(request.POST)
                    if form.is_valid():
                        if int(request.POST["bid"]) <= int(listing.price):
                            context["message"] = "The bid value must me higher than the actual price."
                            return render(request, "auctions/listing.html", context)
                        b = Bids(
                            price=request.POST["bid"],
                            listing_id=listing,
                            user_id=request.user
                        )
                        b.save()
                        listing.price = request.POST["bid"]
                        listing.save(update_fields=["price"])
                        return HttpResponseRedirect(f"/listing/{pk}")
                    else:
                        context["form"] =  form
                        return render(request, "auctions/listing.html", context)

                case keys if "comment" in keys:
                    form = commentForm(request.POST)
                    if form.is_valid():
                        c = Comments(
                            comment = request.POST["comment"],
                            user_id = request.user,
                            data_stamp = now(),
                            listing_id = listing
                        )
                        c.save()
                        return HttpResponseRedirect(f"/listing/{pk}")
                    else:
                        context["form"] =  form
                        return render(request, "auctions/listing.html", context)
                
                case keys if "close" in keys:
                    if listing.user_id != request.user:
                        context["message"] = "You are not the list owner!"
                        return render(request, "auctions/listing.html", context)
                    listing.is_active = False
                    listing.save()
                    print("Veio aqui pia")
                    return HttpResponseRedirect(f"/listing/{pk}")
        else:
            context["message"] = "You need to be loged In!"
            return render(request, "auctions/listing.html", context)
    # - -------- - 
    len_listings = lenth_listings()      
    if pk > len_listings or pk < 0:
        pk = 1 
    if request.user == auction_winner:
        context["message"] = "Your bid is the courrent bid!"
        if listing.is_active == False:
            context["message"] = "YOU WIN THIS AUCTION!!!!"

    return render(request, "auctions/listing.html", context)
    

def create(request):
    if request.method == 'POST':
        form = listingForm(request.POST, request.FILES)
        if form.is_valid():
            s = Listings.objects.create(
                title=form.cleaned_data["title"],
                description=form.cleaned_data["description"],
                price=form.cleaned_data["price"],
                image=form.cleaned_data["image"],
                img_is_url=False, #Adiconar a opção.
                category=form.cleaned_data["category"],
                data_stamp=now(),
                user_id=request.user
            )
            s.save()
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/create.html", {
                "forms": form,
                "STATIC_VERSION": STATIC_VERSION
            })
        
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