from django.contrib import admin

from accounts.models import *

# Register your models here.
admin.site.register(CustomUser)
admin.site.register(verify)
admin.site.register(Address)
admin.site.register(Gallery)
admin.site.register(Store)

admin.site.register(Restaurant_earning)
admin.site.register(Item_category)
admin.site.register(Item)
admin.site.register(Cart)
admin.site.register(Wishlist)
admin.site.register(Order)
admin.site.register(Card)
admin.site.register(Invoice)
admin.site.register(DeliveryPartnerProfile)





