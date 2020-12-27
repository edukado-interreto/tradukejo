from django.conf.urls import include, url
from django.urls import path
from users.views import *
from django.contrib.auth import views as auth_views

urlpatterns = [
    path("account/signup/", register, name="register"),
    path('account/login/', auth_views.LoginView.as_view(), name="login"),
    url(r"^account/", include("django.contrib.auth.urls")),
    path("user/<int:user_id>/", profile, name="profile"),
    path("user/settings/", user_settings, name="user_settings"),
]
