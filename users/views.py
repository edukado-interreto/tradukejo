from django.contrib.auth import login
from django.contrib.auth.models import User
from django.shortcuts import redirect, render, get_object_or_404
from django.urls import reverse
from users.forms import CustomUserCreationForm


def register(request):
    if request.method == "GET":
        return render(
            request, "users/register.html",
            {"form": CustomUserCreationForm}
        )
    elif request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect(reverse("projects"))


def profile(request, user_id):
    current_user = get_object_or_404(User, pk=user_id)

    context = {
        'current_user': current_user,
    }
    return render(request, "users/profile.html", context)
