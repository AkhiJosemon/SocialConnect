
from django.contrib import admin
from django.urls import path
from . import views 
from . views import EditUserView
from . views import UserDetailsView,AllUserDetailsView,SpecificUserDetails,CurrentUser,searchUserView
from django.conf import settings
from django.conf.urls.static import static

from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)


urlpatterns = [
    path("register/", views.RegisterView.as_view(), name="user-register"),
    path("login/", views.LoginView.as_view(), name="user-login"),
    path("user/details/",views.UserDetails.as_view(), name = "user-details"),
    path("otp_verify/",views.OtpVerify.as_view(), name = "user-details"),

    path('user-details/',UserDetailsView.as_view(), name='user-details'),

    path('all-user-details/',AllUserDetailsView.as_view(), name='all-user-details'),


    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    path('specific-user-details/',SpecificUserDetails.as_view(), name='specific-user-details'),

    path('current-user/',CurrentUser.as_view(),name='current-user'),
    path('edit-user/', EditUserView.as_view(),name = 'edit-user'),
    path('search/', searchUserView.as_view(), name='search_users'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


