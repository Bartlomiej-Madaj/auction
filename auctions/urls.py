from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("create-new-listing", views.create_listing, name="create_listing"),
    path("<int:listing_id>", views.listing, name="listing"),
    path("watchlist", views.watchlist, name="watchlist"),
    path("close-auction", views.close_action, name="close_auction"),
    path("closed-listings", views.closed_listings, name="closed_listings"),
    path("bid", views.bid_listing, name="bid_listing"),
    path("comment", views.add_comment, name="add_comment"),
    path("delete-comment", views.delete_comment, name="delete_comment"),
    path("categories", views.categories, name="categories"),
    path("listings/<str:category>", views.category_listings, name="category_listings"),
    path("<path:remaining_path>", views.error, name="error"),
    
]
