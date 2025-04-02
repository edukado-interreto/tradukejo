from django.contrib import messages
from django.contrib.auth import login, get_user_model
from django.shortcuts import redirect, render, get_object_or_404
from django.template.loader import render_to_string
from django.urls import reverse
from users.forms import CustomUserCreationForm, UserSettingsForm
from django.core.mail import send_mail
from django.utils.html import strip_tags
from django.contrib.auth.decorators import login_required
from traduko.models import *
from django.utils.translation import gettext as _, get_language

User = get_user_model()


def register(request):
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            user.email_language = get_language()
            user.save()
            login(request, user)

            context = {
                "username": user.username,
                "url": request.build_absolute_uri("/"),
                "instructions_url": request.build_absolute_uri(reverse("instructions")),
            }
            html_message = render_to_string(
                "users/email/registration-confirmation.html", context
            )
            plain_text_message = strip_tags(html_message)

            send_mail(
                _("emails/registration#title"),
                plain_text_message,
                None,
                [user.email],
                html_message=html_message,
            )

            messages.success(
                request, _("messages#account-created").format(email=user.email)
            )
            return redirect(reverse("projects"))
    else:
        form = CustomUserCreationForm()

    return render(request, "users/register.html", {"form": form})


@login_required
def profile(request, user_id):
    current_user = get_object_or_404(User, pk=user_id)
    projects = (
        Project.objects.filter(visible=True, languageversion__translators=current_user)
        .distinct()
        .order_by("name")
    )

    context = {
        "projects": projects,
        "current_user": current_user,
    }
    return render(request, "users/profile.html", context)


@login_required
def user_settings(request):
    if request.method == "POST":
        form = UserSettingsForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, _("messages#changes-saved"))
        else:
            print(form.errors)
            messages.error(request, _("messages#changes-cannot-be-saved"))
    else:
        form = UserSettingsForm(instance=request.user)

    context = {"form": form}
    return render(request, "users/user-settings.html", context)
