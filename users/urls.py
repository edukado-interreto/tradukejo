from django.conf.urls import include, url
from django.urls import path
from users.views import *
from django.contrib.auth import views as auth_views

urlpatterns = [
    path("kontoj/registrigxi/", register, name="register"),
    path('kontoj/ensaluti/', auth_views.LoginView.as_view(), name="login"),
    url(r"^kontoj/", include("django.contrib.auth.urls")),
    path("uzanto/<int:user_id>/", profile, name="profile"),
]
