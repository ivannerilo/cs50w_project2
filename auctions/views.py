from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django import forms
from .models import Listings, User, Bids, Comments, CATEGORIES
from django.utils.timezone import now
from .utils import actual_index
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
    listings = models.Listings.objects.all()
    return render(request, "auctions/index.html", {
        "listings": listings,
        "STATIC_VERSION": STATIC_VERSION
    })

def show_listing(request, pk):
    l = Listings.objects.get(pk=pk)
    c = Comments.objects.filter(listing_id=l)
    bids = Bids.objects.filter(listing_id=l)
    context = {
        "message": None,
        "listing": l,
        "comments": c,
        "bid_form": bidsForm(),
        "comment_form": commentForm(),
        "STATIC_VERSION": STATIC_VERSION,
        "bids": len(bids),
        "listing_user": l.user_id
    }

    #Processo de manipulação dos formulários.
    if request.method == "POST": 
        # Forumulários só são processados se o user estiver logado.
        if request.user.is_authenticated: 
            # Se o formulário for de Bid:
            if request.POST.get("bid"):
                form = bidsForm(request.POST)
                # verifica se o formulário é valido:
                if form.is_valid():
                    # Se o valor bidado não for maior que o o último bid, não autoriza a operação e retorna mensagem.
                    if int(request.POST["bid"]) <= int(l.price):
                        context["message"] = "The bid value must me higher than the actual price."
                        return render(request, "auctions/listing.html", context)
                    # Caso o valor for válido, salva no banco.
                    b = Bids(
                        price=request.POST["bid"],
                        listing_id=l,
                        user_id=request.user
                    )
                    b.save()
                    l.price = request.POST["bid"]
                    l.save(update_fields=["price"])
                # Retorna uma mensagem se o formulário não for válido.
                else:
                    context["form"] =  form
                    return render(request, "auctions/listing.html", context)
            # Se o formulário for de comment:
            elif request.POST.get("comment"):
                form = commentForm(request.POST)
                # verifica se o formulário é valido:
                if form.is_valid():
                    # Salva no banco:
                    c = Comments(
                        comment = request.POST["comment"],
                        user_id = request.user,
                        data_stamp = now(),
                        listing_id = l
                    )
                    c.save()
                else:
                    context["form"] =  form
                    return render(request, "auctions/listing.html", context)
        # Retorna uma mensagem se o user não estiver logado.
        else:
            context["message"] = "You need to be loged In to place a bid!"
            return render(request, "auctions/listing.html", context)
    # Caso o usuário tente acessar um listing que não existe.      
    # if pk > len(listing_list) or pk < 0:
    #     pk = 1 
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