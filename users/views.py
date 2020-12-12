from django.contrib.auth import login, get_user_model
from django.shortcuts import redirect, render, get_object_or_404
from django.template.loader import render_to_string
from django.urls import reverse
from users.forms import CustomUserCreationForm
from django.core.mail import send_mail
from django.utils.html import strip_tags

User = get_user_model()


def register(request):
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)

            context = {
                'username': user.username,
                'url': request.build_absolute_uri('/'),
            }
            html_message = render_to_string("users/email/registration-confirmation.html", context)
            plain_text_message = strip_tags(html_message)

            send_mail(
                'Tradukejo de E@I: konfirmo de aliĝo',
                plain_text_message,
                None,
                [user.email],
                html_message=html_message
            )
            return redirect(reverse("projects"))
    else:
        form = CustomUserCreationForm()

    return render(
        request, "users/register.html",
        {"form": form}
    )


def profile(request, user_id):
    current_user = get_object_or_404(User, pk=user_id)

    context = {
        'current_user': current_user,
    }
    return render(request, "users/profile.html", context)
