from django.contrib import admin
from .models import Auction, Bid, Comment, Watchlist

# Customization
class Auction_Custom(admin.ModelAdmin):
	list_display = ('user', 'title', 'category', 'bid', 'default_bid', 'active')
	search_fields = ('user', 'title', 'category')

class Bid_Custom(admin.ModelAdmin):
	list_display = ('user', 'auction_list', 'amount', 'bid_created')
	search_fields = ('user__username', 'auction_list__title')

class Comment_Custom(admin.ModelAdmin):
	list_display = ('user', 'auction_list', 'comment')
	search_fields = ('user__username', 'auction_list__title', 'comment')

class Watchlist_Custom(admin.ModelAdmin):
	list_display = ('user', 'auction_list')
	search_fields = ('user__username', 'auction_list__title')

# Register to Admin
admin.site.register(Auction, Auction_Custom)
admin.site.register(Bid, Bid_Custom)
admin.site.register(Comment, Comment_Custom)
admin.site.register(Watchlist, Watchlist_Custom)