from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser, models.Model):
    url = models.URLField(default="https://as2.ftcdn.net/v2/jpg/02/15/84/43/1000_F_215844325_ttX9YiIIyeaR7Ne6EaLLjMAmy4GvPC69.jpg")

class Category(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return f"{self.name}"


class Bid(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user")
    bid_date = models.DateTimeField(auto_now_add=True)
    bid = models.FloatField()
    def __str__(self):
        return f"Bid author: {self.user}, bid: {self.bid}, date: {self.bid_date}"

class Listing(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="listing_author")
    title = models.CharField(max_length=100)
    listing_date = models.DateTimeField(auto_now_add=True)
    description = models.TextField()
    url = models.URLField()
    starting_bid = models.ForeignKey(Bid, on_delete=models.CASCADE, related_name="starting_bid")
    current_bid = models.ForeignKey(Bid, on_delete=models.CASCADE, related_name="current_bid")
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="category")
    winner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="winner", null=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"Listing author: {self.author}, title: {self.title}, url: {self.url}, current_bid: {self.current_bid}"
    
class Comment(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="comment_author")
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="listing_comment", null=True)
    comment_date = models.DateTimeField(auto_now_add=True)
    content = models.TextField()
    
    def __str__(self):
        return f"Comment author: {self.author}, comment date: {self.comment_date}"

class Watchlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="watchlist_user")
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="watchlist_listing")

    def __str__(self):
        return f"Watchlist author: {self.user}, listings: {self.listing},"
