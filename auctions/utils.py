from .models import Watchlist, Listings

def lenth_listings():
    listings = Listings.objects.all()
    return len(listings)

def actual_index(pk):
    if pk == 0:
        return 0
    return pk - 1

def who_winning(bids):
    try:
        auction_winner = bids[actual_index(len(bids))].user_id
    except:
        auction_winner = None
    return auction_winner

def in_watchlist(listing, user):
    watchlist = Watchlist.objects.filter(listing_id=listing, user_id=user)
    in_watchlist = False
    if watchlist:
        in_watchlist = True
    return in_watchlist
