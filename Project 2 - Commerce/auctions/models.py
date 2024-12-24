from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    pass

# Model field types
# https://docs.djangoproject.com/en/5.0/ref/models/fields/#field-types

# Auction Model
class Auction(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="lists")

    # Auction fields
    title = models.CharField(max_length=255)
    description = models.TextField()
    image = models.URLField(blank=True, null=True)
    category = models.CharField(max_length=32, blank=True, null=True)

    # 9,999,999.99
    bid = models.DecimalField(max_digits=9, decimal_places=2)
    default_bid = models.DecimalField(max_digits=9, decimal_places=2, null=True, blank=True)

    # Check if it still active
    active = models.BooleanField(default=True)

    # Sorting by date
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

# Bid Model
class Bid(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="bids")
    auction_list = models.ForeignKey(Auction, on_delete=models.CASCADE, related_name="bids")
    amount = models.DecimalField(max_digits=9, decimal_places=2)
    bid_created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username}: {self.amount}"

# Comment Model
class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="comments")
    auction_list = models.ForeignKey(Auction, on_delete=models.CASCADE, related_name="comments")
    comment = models.TextField()

    def __str__(self):
        return f"{self.user.username} commented in {self.auction_list.title}"

# Watchlist Model
class Watchlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="watchlist")
    auction_list = models.ForeignKey(Auction, on_delete=models.CASCADE, related_name="watchlist")

    def __str__(self):
        return f"{self.user.username}: {self.auction_list.title}"