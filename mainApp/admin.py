from django.contrib import admin

from.models import *

admin.site.register((Maincategory,Subcategory,Brand,Product,Buyer,Wishlist,Checkout,CheckoutProducts,Contact))
