import factory
from factory.django import DjangoModelFactory, Password
from faker import Faker

fake = Faker()


class UserFactory(DjangoModelFactory):
    """Factory for the User model."""

    class Meta:
        model = "users.User"
        django_get_or_create = ("username",)

    username = factory.Sequence(lambda n: f"user{n}")
    email = factory.LazyAttribute(lambda o: f"{o.username}@example.com")
    first_name = factory.Faker("first_name")
    last_name = factory.Faker("last_name")
    is_active = True
    password = Password("password123")


class DeeplAuthKeyFactory(DjangoModelFactory):
    class Meta:
        model = "users.DeeplAuthKey"
