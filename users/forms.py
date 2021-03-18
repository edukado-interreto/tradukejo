from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model


class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = get_user_model()
        fields = UserCreationForm.Meta.fields + ('email',)


class UserSettingsForm(forms.ModelForm):
    class Meta:
        model = get_user_model()
        fields = ['email_language', 'email_new_texts', 'email_translation_request', 'email_new_comments']
