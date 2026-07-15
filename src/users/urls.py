from django.contrib.auth import views as auth_views
from django.urls import include, path, re_path

from users.views import profile, register, user_settings

urlpatterns = [
    path("account/signup/", register, name="register"),
    path("account/login/", auth_views.LoginView.as_view(), name="login"),
    re_path(r"^account/", include("django.contrib.auth.urls")),
    path("user/<int:user_id>/", profile, name="profile"),
    path("user/settings/", user_settings, name="user_settings"),
]
