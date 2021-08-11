"""kkawa URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.urls.conf import include
from accounts import views

from rest_framework import routers
from django.conf.urls import url

# router = routers.DefaultRouter()
# router.register(r'^Orders', views.OrderViewset),

urlpatterns = [
    path('admin/', admin.site.urls),
    # path('', include(router.urls)),


    path('accounts/',include("accounts.urls")),
    path('admin_section/',include("admin_section.urls")),

    path('index', views.social_reg),
    path('home', views.home),
    path('success', views.success),


    path('api/v1/user/search/', views.checkUser),
    path('api/v1/user/read/', views.checkUserId),

    path("api/v1/checkitem/",views.checkItems),
    path("api/v1/store/search/",views.StoreSearch),

    path("api/v1/accounts/", include('allauth.urls')),   #social login
  
    
]
