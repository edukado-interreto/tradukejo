import factory
from factory.django import DjangoModelFactory
from faker import Faker

from users.tests.factories import UserFactory

fake = Faker()


class LanguageFactory(DjangoModelFactory):
    """
    Factory for the Language model.
    """

    class Meta:
        model = "traduko.Language"
        django_get_or_create = ("code",)

    code = factory.Faker("pystr", max_chars=8)
    name = factory.LazyAttribute(lambda o: f"{fake.language_name()} ({o.code})")
    plural_forms = "nplurals=2; plural=(n == 1 ? 0 : 1);"


class ProjectFactory(DjangoModelFactory):
    """
    Factory for the Project model.
    """

    class Meta:
        model = "traduko.Project"
        skip_postgeneration_save = True

    name = factory.LazyFunction(lambda: f"{fake.last_name()} {fake.pyint()}")
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

    @factory.post_generation
    def needed_languages(self, create, extracted, **kwargs):
        if not create:
            return
        if extracted:
            for lang in extracted:
                self.needed_languages.add(lang)
                self.save()

    @factory.post_generation
    def admins(self, create, extracted, **kwargs):
        if not create:
            return
        if extracted:
            for admin in extracted:
                self.admins.add(admin)
                self.save()


class LanguageVersionFactory(DjangoModelFactory):
    """Factory for the LanguageVersion model."""

    class Meta:
        model = "traduko.LanguageVersion"
        skip_postgeneration_save = True

    project = factory.SubFactory(ProjectFactory)
    language = factory.SubFactory(LanguageFactory)

    @factory.post_generation
    def translators(self, create, extracted, **kwargs):
        if not create or not extracted:
            # Simple build, or nothing to add, do nothing.
            return

        # Add the iterable of translators using bulk addition
        self.translators.add(*extracted)
        self.save()


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
    path = factory.Faker("mime_type")
    name = factory.Faker("word")
    context = factory.Faker("sentence")


class TrStringTextFactory(DjangoModelFactory):
    """Factory for the TrStringText model."""

    class Meta:
        model = "traduko.TrStringText"

    trstring = factory.SubFactory(TrStringFactory)
    language = factory.SubFactory(LanguageFactory)
    text = factory.Faker("word")


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
