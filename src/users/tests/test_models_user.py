import pytest
from django.db.utils import IntegrityError


from .factories import UserFactory


def test_user_str():
    user = UserFactory.build(username="zam")
    assert str(user) == "zam"
    assert repr(user) == "<User: zam>"


def test_user_default():
    user = UserFactory.build(username="zam")
    assert user.email_new_texts
    assert user.email_translation_request
    assert user.email_new_comments
    assert user.email_language == "eo"


@pytest.mark.django_db
def test_user_same_emails():
    UserFactory(username="zam", email="e@i.eo")
    with pytest.raises(IntegrityError):
        UserFactory(username="maz", email="e@i.eo")
