
from django.urls import path
from rest_framework import views
from rest_framework.urlpatterns import format_suffix_patterns
from accounts.views import *
from accounts.views import checkItems
from . import views

urlpatterns = [
    path("api/v1/user/register/", CustomerRegisterView.as_view(),name="customerregister"),
    path("api/v1/user/registerviaemail/", CustomerRegisterViaEmail.as_view(),name="customerregisterviaemail"),

    path("api/v1/restaurant/register/", RestaurantRegisterView.as_view(),name="restaurantregister"),
    path("api/v1/restaurant/registerviaemail/", RestaurantRegisterViaEmail.as_view(),name="restaurantregisterviaemail"),
    
    path("api/v1/delivery/register/", DeliveryRegisterView.as_view(),name="deliveryregister"),
    path("api/v1/delivery/registerviaemail/", DeliveryRegisterViaEmail.as_view(),name="deliveryregisterviaemail"),
    
    path("api/v1/verifyotp/", verifyOTPView.as_view(), name="verifyotp"),
    path('api/v/resendotp/', ResendOTP.as_view(), name='resendotp'),
    
    path('api/v1/login/', Login.as_view(), name="customerlogin"),
    path('api/v1/logout/', Logout.as_view()),

    path('api/v1/forgetpassword/', ForgetPasswordView.as_view()),
    path("forgetpasswordotpverify/", ForgetPasswordOTPVerify.as_view()),
    path("changepassword/", PasswordChangeView.as_view()),
    path("api/v1/user/update/<int:pk>", UserDetails.as_view()),


    path("api/v1/address/", AddressView.as_view()),
    path("api/v1/address/<int:pk>", AddressDetails.as_view()),

    path("api/v1/stores/", StoreView.as_view()),
    path("api/v1/stores/<int:pk>", StoreDetail.as_view()),


    path("api/v1/restaurantearnings/", Restaurant_earningsView.as_view()),
    path("api/v1/restaurantearnings/<int:pk>", Restaurant_earningsDetail.as_view()),
    
    path("api/v1/itemcategory/", ItemCategoryView.as_view()),
    path("api/v1/itemcategory/<int:pk>", ItemCategoryDetail.as_view()),

    path("api/v1/items/", ItemView.as_view()),
    path("api/v1/items/<int:pk>", ItemDetail.as_view()),

    path("api/v1/customeritemslist", CustomerItemsList.as_view()),

    path('api/v1/addtocart/', AddToCartAPI.as_view(), name='add'),
    path("api/v1/addtocart/<int:pk>/", CartDetails.as_view()),

    path('api/v1/wishlist/', Wishlist.as_view(), name='add'),
    path("api/v1/wishlist/<int:pk>/", WishlistDetail.as_view()),


    path("api/v1/orders/", OrderView.as_view()),
    path("api/v1/orders/<int:pk>", OrderDetail.as_view()),

    path('api/v1/card/', CardView.as_view(), name='add'),
    path("api/v1/card/<int:pk>/", CardDetail.as_view()),

    path('api/v1/invoice/', InvoiceView.as_view(), name='add'),
    path("api/v1/invoice/<int:pk>/", InvoiceDetail.as_view()),

    path('api/v1/review/', ReviewView.as_view(), name='add'),
    path('api/v1/reply/', ChatView.as_view(), name='add'),
    
    # path('api/v1/ticket/create/', TicketView.as_view(), name='add'),



    path('api/messages/<int:userId>/<int:adminId>', views.message_list, name='message-detail'),  # For GET request.
    path('api/v1/ticket/create/', views.message_list, name='message-list'),   # For POST
    # path('api/users/<int:pk>', views.user_list, name='user-detail'),      # GET request for user with id
    # path('api/users/', views.user_list, name='user-list'),    # POST for new user and GET for all users list



    path('customerorder/', CustomerOrderList.as_view()),
    path('api/v1/deliverypartner/', DeliveryPartnerView.as_view()),
    path("api/v1/deliverypartner/<int:pk>/", DeliveryPartnerDetails.as_view()),

    path('api/v1/customersupport/', CustomerSupportView.as_view()),
    path("api/v1/customersupport/<int:pk>/", CustomerSupportDetail.as_view()),
]
urlpatterns = format_suffix_patterns(urlpatterns)
