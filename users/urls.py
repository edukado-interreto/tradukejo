from django.conf.urls import include, url
from django.urls import path
from users.views import *

urlpatterns = [
    path("kontoj/registrigxi/", register, name="register"),
    url(r"^kontoj/", include("django.contrib.auth.urls")),
    path("uzanto/<int:user_id>/", profile, name="profile"),
]