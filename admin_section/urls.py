from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns

from admin_section.views import DeliveryPartnerApprovalView, RestaurantApprovalView

urlpatterns = [
    path("restaurantapproval/", RestaurantApprovalView.as_view(),
         name="restaurantapproval"),
    path("deliveryapproval/", DeliveryPartnerApprovalView.as_view(),
         name="deliveryapproval"),
]
urlpatterns = format_suffix_patterns(urlpatterns)
