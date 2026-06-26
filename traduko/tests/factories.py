import factory
from django.contrib.auth import get_user_model
from factory.django import DjangoModelFactory
from faker import Faker

from traduko.models import Language
from users.tests.factories import UserFactory

fake = Faker()


def lang_code(obj):
    name = obj.name.lower()
    return f"{name[:2]}-{name[-3:]}"


class LanguageFactory(DjangoModelFactory):
    """
    Factory for the Language model.
    """

    class Meta:
        model = "traduko.Language"
        django_get_or_create = ("name",)

    name = factory.Faker("language_name")
    code = factory.LazyAttribute(lang_code)
    plural_forms = "nplurals=2; plural=(n == 1 ? 0 : 1);"


class ProjectFactory(DjangoModelFactory):
    """
    Factory for the Project model.
    """

    class Meta:
        model = "traduko.Project"
        skip_postgeneration_save = True

    name = factory.Faker("company")
    url = factory.Faker("url")
    source_language = factory.SubFactory(LanguageFactory)
    image = factory.django.ImageField(
        color=factory.Faker("color"), width=512, height=512
    )
    description = factory.Faker("text", max_nb_chars=200)
    update_explanations = factory.Faker("text", max_nb_chars=400)
    export_explanations = factory.Faker("text", max_nb_chars=400)
    strings = factory.Faker("random_int", min=0, max=10000)
    words = factory.Faker("random_int", min=0, max=50000)
    characters = factory.Faker("random_int", min=0, max=200000)
    visible = factory.Faker("boolean", chance_of_getting_true=90)
    locked = factory.Faker("boolean", chance_of_getting_true=10)

    @factory.post_generation
    def needed_languages(self, create, extracted, **kwargs):
        if not create:
            return
        if extracted:
            for lang in extracted:
                self.needed_languages.add(lang)
        else:
            # Optionally attach up to 5 random languages
            langs = Language.objects.order_by("?")[: fake.random_int(min=1, max=5)]
            self.needed_languages.set(langs)

    @factory.post_generation
    def admins(self, create, extracted, **kwargs):
        if not create:
            return
        if extracted:
            for admin in extracted:
                self.admins.add(admin)
        else:
            # Optionally attach up to 3 random users
            User = get_user_model()
            users = User.objects.order_by("?")[: fake.random_int(min=1, max=3)]
            self.admins.set(users)


class LanguageVersionFactory(DjangoModelFactory):
    """Factory for the LanguageVersion model."""

    class Meta:
        model = "traduko.LanguageVersion"

    project = factory.SubFactory(ProjectFactory)
    language = factory.SubFactory(LanguageFactory)


class TranslatorRequestFactory(DjangoModelFactory):
    """Factory for the TranslatorRequest model."""

    class Meta:
        model = "traduko.TranslatorRequest"

    language_version = factory.SubFactory(LanguageVersionFactory)
    user = factory.SubFactory(UserFactory)
    explanation = factory.Faker("paragraph", nb_sentences=3)


class TrStringFactory(DjangoModelFactory):
    """Factory for the TrString model."""

    class Meta:
        model = "traduko.TrString"

    project = factory.SubFactory(ProjectFactory)


class TrStringTextFactory(DjangoModelFactory):
    """Factory for the TrStringText model."""

    class Meta:
        model = "traduko.TrStringText"

    trstring = factory.SubFactory(TrStringFactory)
    language = factory.SubFactory(LanguageFactory)


class TrStringTextHistoryFactory(DjangoModelFactory):
    class Meta:
        model = "traduko.TrStringTextHistory"

    trstringtext = factory.SubFactory(TrStringTextFactory)
    translated_by = factory.SubFactory(UserFactory)


class StringActivityFactory(DjangoModelFactory):
    class Meta:
        model = "traduko.StringActivity"

    trstringtext = factory.SubFactory(TrStringTextFactory)
    user = factory.SubFactory(UserFactory)


class CommentFactory(DjangoModelFactory):
    class Meta:
        model = "traduko.Comment"

    trstringtext = factory.SubFactory(TrStringTextFactory)
    author = factory.SubFactory(UserFactory)
