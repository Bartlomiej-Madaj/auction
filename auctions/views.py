from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from .models import User, Listing, Category, Bid, Watchlist, Comment


def index(request):
    listings = Listing.objects.filter(is_active = True).order_by("-listing_date")

    return render(request, "auctions/index.html",{"listings": listings, "headline": "Active Listings"})


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
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


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
    
@login_required   
def create_listing(request):
    user = request.user
    categories = Category.objects.all().values()
    category_list = list(category['name'] for category in categories)

    if request.method == "POST":
        try:
            entered_bid = float(request.POST['starting_bid'])
        except ValueError:
            return render(request, "auctions/create_listing.html.html", {"categories": category_list, "bid_message": 'The bid have to be greater or equal 0!'})
        title = request.POST['title']
        description = request.POST['description']
        entered_category = request.POST['category']
        listing_url = request.POST['listing_url']
        if not title.strip():
            return render(request, "auctions/create_listing.html", {"categories": category_list, "title_message": 'You have to add title!'})
        if entered_bid <= 0:
            return render(request, "auctions/create_listing.html", {"categories": category_list, "bid_message": 'The bid have to be greater or equal 0!'})
        if len(description) < 10:
            return render(request, "auctions/create_listing.html", {"categories": category_list, "description_message": 'Your description have to be longer then 10 characters!'})
        if not entered_category in category_list:
            return render(request, "auctions/create_listing.html", {"categories": category_list, "category_message": 'You have to choose correct category!'})
        if not listing_url:
            listing_url = "https://as1.ftcdn.net/v2/jpg/05/04/28/96/1000_F_504289605_zehJiK0tCuZLP2MdfFBpcJdOVxKLnXg1.jpg" 
        starting_bid = Bid(user=user, bid=entered_bid)
        starting_bid.save()
        
        category = Category.objects.get(name=entered_category)
        listing = Listing.objects.create(author=user, title=title, starting_bid=starting_bid, current_bid=starting_bid, description=description, category=category, url=listing_url)
        print(listing)
        return HttpResponseRedirect(reverse("index"))

    return render(request, "auctions/create_listing.html", {"categories": category_list})

def listing(request, listing_id):
    try:
        listing = Listing.objects.get(id=listing_id)
    except Listing.DoesNotExist:
        return render(request, "auctions/404.html", {"message": "This listing does not exist!"})
    user = request.user
    listings_id = Watchlist.objects.filter(user_id=user.id, listing_id=listing_id).values("listing_id")
    comments = Comment.objects.filter(listing=listing).order_by("-comment_date")
    message = None
    try:
        int(listing_id)
    except:
        return render(request, "auctions/404.html", {"message": "This listing does not exist!"})
    
    if not listing_id in [listing["listing_id"] for listing in listings_id]:
        message ="Add to watchlist"
    else:
        message ="Remove from watchlist"

    return render(request, "auctions/listing.html", {"listing": listing, "text_button": message, "author": user, "comments": comments })

@login_required
def watchlist(request):
    if request.method == "POST":
        listings_id = Listing.objects.values_list('id', flat=True)
        try:
            listing_id = int(request.POST["listing_id"])
        except ValueError:
            return render(request, "auctions/404.html", {"message": "This listing does not exist!"})
        flag = request.POST["flag"]
  
        if listing_id in listings_id:
            try:
                listing = Listing.objects.get(id=listing_id)
            except Listing.DoesNotExist:
                return render(request, "auctions/404.html", {"message": "This listing does not exist!"})
            user = request.user
            try:
                listings_id = Watchlist.objects.filter(user_id=user.id, listing_id=listing_id).values("listing_id")
            except Watchlist.DoesNotExist:
                return render(request, "auctions/404.html", {"message": "This listing does not exist!"})  

            if listing_id in [listing["listing_id"] for listing in listings_id]:
                Watchlist.objects.get(listing=listing, user=user).delete()
                if flag == "listing":
                    return HttpResponseRedirect(f"{listing_id}")
                elif flag == "watchlist":
                    return HttpResponseRedirect(reverse('watchlist'))
                else:
                    return render(request, "auctions/404.html", {"message": "This listing does not exist!"})  
            else:
                Watchlist.objects.create(user=user, listing=listing)
            return HttpResponseRedirect(f"{listing_id}")
        else:
            return render(request, "auctions/404.html", {"message": "This listing does not exist!"})
           
    watchlist = Watchlist.objects.all()
    return render(request, "auctions/watchlist.html", {"listings": [listing.listing for listing in watchlist]})

@login_required
def bid_listing(request):
    if request.method == "POST":
        user = request.user
        bid_listing = request.POST['bid_input']
        listing_id = request.POST['listing_id']
        try:
            listing = Listing.objects.get(id=listing_id)
        except Listing.DoesNotExist:
            return render(request, "auctions/404.html", {"message": "This listing does not exist!"})
        if not listing:
            return render(request, "auctions/404.html", {"message": "This listing does not exist!"})
        current_bid = Listing.objects.get(id= listing_id).current_bid.bid
        try:
            float(bid_listing)
        except:
            return render(request, "auctions/404.html", {"message": "This listing does not exist!"})
        if float(bid_listing) > current_bid:
            new_bid = Bid.objects.create(user=user, bid=float(bid_listing))
            Listing.objects.filter(id=listing_id).update(current_bid=new_bid)
            return HttpResponseRedirect(f"{listing_id}") 
        else:
            messages.error(request, "You have to beat the current offer", extra_tags="bid_error")
            return HttpResponseRedirect(f"{listing_id}") 

    return render(request, "auctions/404.html", {"message": "This listing does not exist!"})

@login_required
def close_action(request):
    if request.method == "POST":
        user = request.user
        listing_id = request.POST['listing_id']
        try:
            listing_author = Listing.objects.get(id=listing_id).author
        except Listing.DoesNotExist:
            return render(request, "auctions/404.html", {"message": "This listing does not exist!"})
        listings_id = Listing.objects.filter(is_active=True).values_list('id', flat=True)

        if int(listing_id) in listings_id and user == listing_author:
            winning_bid = Listing.objects.get(id=listing_id).current_bid.user
            Listing.objects.filter(id=listing_id).update(is_active=False, winner=winning_bid)    
            return HttpResponseRedirect(reverse('index'))
        return HttpResponseRedirect(f"{listing_id}")
    else:
        return render(request, "auctions/404.html", {"message": f"Not Found this page!!"})  

@login_required
def closed_listings(request):
    listings = Listing.objects.filter(is_active = False)
    return render(request, "auctions/closed_listings.html",{"listings": listings})

@login_required
def add_comment(request):
    if request.method == "POST":
        user = request.user
        comment = request.POST['comment']
        listing_id = request.POST['listing_id']
        listings_id = Listing.objects.filter(is_active=True).values_list('id', flat=True)

        if int(listing_id) in listings_id:
            listing = Listing.objects.get(id = listing_id)
            comment = Comment.objects.create(author=user, content=comment, listing=listing)
            print(f"comment: {comment}")
            return HttpResponseRedirect(f"{listing_id}") 
    return render(request, "auctions/404.html", {"message": f"Not Found this page!!"}) 

@login_required
def delete_comment(request):
    if request.method == "POST":
        user = request.user
        listing_id = request.POST['listing_id']
        comment_id = request.POST['comment_id']

        # attempt find listing
        try:
            listing = Listing.objects.get(id=listing_id)
        except Listing.DoesNotExist:
            return render(request, "auctions/404.html", {"message": f"Not Found this page!!"})
         
        try:
            comments = Comment.objects.filter(author=user, listing=listing).values_list('id', flat=True)
        except Comment.DoesNotExist:
            return render(request, "auctions/404.html", {"message": f"Not Found this page!!"})
        
        if int(comment_id) in comments:
            Comment.objects.get(id=comment_id).delete()
            return HttpResponseRedirect(f"{listing_id}")
        else:
            return HttpResponseRedirect(f"{listing_id}")

    return render(request, "auctions/404.html", {"message": f"Not Found this page!!"}) 


def categories(request):
    categories = Category.objects.all().values()
    return render(request, "auctions/categories.html", {"categories": categories}) 


def category_listings(request, category):
    try:
        category_listing = Category.objects.get(name=category)
        listing = Listing.objects.filter(category=category_listing)
    except Category.DoesNotExist:
        return render(request, "auctions/404.html", {"message": f"Not Found this page!!"})
    return render(request, "auctions/index.html", {"listings": listing, "headline": "Listings"}) 

def error(request, remaining_path):
    return render(request, "auctions/404.html", {"message": f"Not Found this page!!"})