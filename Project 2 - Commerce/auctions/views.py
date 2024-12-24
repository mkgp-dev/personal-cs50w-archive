from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import IntegrityError
from django.db.models import Max
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse

from .models import User, Auction, Comment, Bid, Watchlist


def index(request):
    # Active listings
    active_auctions = Auction.objects.filter(active=True)

    return render(request, "auctions/index.html", {
        "active_auctions": active_auctions
    })


def login_view(request):
    # Check if user is already login
    if request.user.is_authenticated:
        return HttpResponseRedirect(reverse("index"))

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
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    # Check if user is already login
    if request.user.is_authenticated:
        return HttpResponseRedirect(reverse("index"))

    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")

# Create listing
@login_required(login_url=login_view)
def create_auction(request):
    if request.method == 'POST':
        # Define variable/s
        title = request.POST['title']
        description = request.POST['description']
        bid = float(request.POST['bid'])
        image = request.POST.get('image', '')
        category = request.POST.get('category', '')

        if not title or not description:
            return render(request, "auctions/create.html", {
                "message_error": "Missing fields are required."
            })

        if bid <= 0:
            return render(request, "auctions/create.html", {
                "message_error": "Your starting bid should be greater than 0."
            })

        # Import to model
        new_auction_created = Auction(
            user=request.user,
            title=title,
            description=description,
            image=image,
            category=category,
            bid=bid,
            default_bid=bid,
        )

        new_auction_created.save()

        return render(request, "auctions/create.html", {
            "message_success": "You have created your auction."
        })

    return render(request, "auctions/create.html")

# Shortcut function
# https://docs.djangoproject.com/en/5.1/topics/http/shortcuts/

# Messages function
# https://docs.djangoproject.com/en/5.1/ref/contrib/messages/

# Filter function
# https://docs.djangoproject.com/en/5.1/topics/db/queries/

# Display listing
def item_page(request, item_id):
    # Note to myself:
    # Have a proper 404 Not Found
    # item = get_object_or_404(Auction, pk=item_id)

    try:
        item = Auction.objects.get(pk=item_id)
    except Auction.DoesNotExist:
        return render(request, "auctions/item.html", {
            "not_found": True
        })

    item_bids = Bid.objects.filter(auction_list=item).order_by('-amount')
    comments = Comment.objects.filter(auction_list=item).order_by('-id')
    max_bid = Bid.objects.filter(auction_list=item).aggregate(Max('amount'))['amount__max']
    user_watchlist = False

    # Watchlist
    if request.user.is_authenticated:
        user_watchlist = Watchlist.objects.filter(user=request.user, auction_list=item).exists()

    # Bidding winner
    auction_winner = None
    if not item.active and max_bid:
        auction_winner = Bid.objects.filter(auction_list=item, amount=max_bid).first().user

    # Mechanism
    if request.method == "POST":
        action = request.POST['action']

        # Close auction
        if action == 'close_auction':
            item.active = False
            item.save()
            messages.success(request, "You have successfully closed your auction.")
            return redirect('item_page', item_id=item_id)

        elif action == 'add_watchlist':
            if not user_watchlist:
                Watchlist.objects.create(user=request.user, auction_list=item)
                # messages.success(request, "You have added this item to your watchlist.")
            return redirect('item_page', item_id=item_id)

        elif action == 'remove_watchlist':
            Watchlist.objects.filter(user=request.user, auction_list=item).delete()
            # messages.success(request, "You have removed this item to your watchlist.")
            return redirect('item_page', item_id=item_id)

        elif action == 'user_bid':
            amount = float(request.POST['bid'])

            try:
                if amount < item.bid or (max_bid and amount <= max_bid):
                    messages.error(request, "Your bid must be higher from the current price.")
                else:
                    Bid.objects.create(user=request.user, auction_list=item, amount=amount)
                    item.default_bid = amount
                    item.save()
                    messages.success(request, "Your bid was successfully.")
            except ValueError:
                messages.error(request, "Invalid bid amount.")

            return redirect('item_page', item_id=item_id)

        elif action == 'user_comment':
            comment = request.POST['comment']
            if comment:
                Comment.objects.create(user=request.user, auction_list=item, comment=comment)

            return redirect('item_page', item_id=item_id)

    return render(request, "auctions/item.html", {
        "item": item,
        "comments": comments,
        "watchlist_bool": user_watchlist,
        "auction_winner": auction_winner,
        "bids": item_bids,
    })

# Display watchlist
@login_required(login_url=login_view)
def watchlist_page(request):
    watchlist_items = Watchlist.objects.filter(user=request.user)

    return render(request, 'auctions/watchlist.html', {
        "items": watchlist_items,
    })

# Display categories
def category_page(request):
    category = Auction.objects.filter(active=True).exclude(category__exact="").values('category').order_by('category')

    return render(request, 'auctions/category.html', {
        "categories": category,
    })

def category_list(request, category):
    category_list = Auction.objects.filter(active=True, category=category)

    return render(request, 'auctions/category.html', {
        "category": category,
        "lists": category_list
    })