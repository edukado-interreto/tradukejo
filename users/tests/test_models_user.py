import pytest
from django.core.exceptions import ValidationError
from django.db.utils import IntegrityError

from users.models import User



@pytest.mark.django_db
def test_user_str():
    user = User.objects.create_user("zam")
    assert str(user) == "zam"
    assert repr(user) == "<User: zam>"


@pytest.mark.django_db
def test_user_default():
    user = User.objects.create_user("zam")
    assert user.email_new_texts
    assert user.email_translation_request
    assert user.email_new_comments
    assert user.email_language == "eo"


@pytest.mark.django_db
def test_user_same_emails():
    User.objects.create_user("zam", email="e@i.eo")
    with pytest.raises(IntegrityError):
        User.objects.create_user("maz", email="e@i.eo")
