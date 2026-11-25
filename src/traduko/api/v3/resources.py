"""
Resource objects and documents of the API v3.

Each resource type has its own attributes, resource and document types.
They are concrete ``TypedDict`` types instead of ``ResourceObject[...]``,
because the OpenAPI schema names every specialization of a generic
``TypedDict`` the same way.
"""

import json
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Literal, NotRequired

from django.http import HttpRequest
from django.urls import reverse
from dmr_jsonapi.builders import (
    relationship_to_many,
    relationship_to_one,
    resource_identifier,
    resource_object,
)
from dmr_jsonapi.objects import (
    DocumentEnvelope,
    Links,
    Relationship,
    ResourceObject,
)
from typing_extensions import TypedDict

from traduko.models import (
    TRANSLATION_STATE_OUTDATED,
    Language,
    LanguageVersion,
    Project,
    TrString,
    TrStringText,
)

URL_NAMESPACE = "api-v3"

LANGUAGES = "languages"
PROJECTS = "projects"
LANGUAGE_VERSIONS = "languageVersions"
STRINGS = "strings"
TRANSLATIONS = "translations"


# Attributes


class LanguageAttributes(TypedDict):
    name: str
    direction: Literal["ltr", "rtl"]
    pluralForms: str
    pluralExamples: list[str]
    google: bool
    deepl: bool
    yandex: bool


class ProjectAttributes(TypedDict):
    name: str
    url: str
    description: str
    image: str | None
    strings: int
    words: int
    characters: int
    locked: bool
    createDate: datetime
    lastChange: datetime


class LanguageVersionAttributes(TypedDict):
    translatedStrings: int
    translatedWords: int
    translatedCharacters: int
    outdatedStrings: int
    outdatedWords: int
    outdatedCharacters: int
    untranslatedStrings: int
    untranslatedWords: int
    untranslatedCharacters: int


class StringAttributes(TypedDict):
    path: str
    name: str
    context: str
    words: int
    characters: int
    lastChange: datetime


class TranslationAttributes(TypedDict):
    pluralized: bool
    texts: list[str]
    state: Literal["translated", "outdated"]
    lastChange: datetime


# Resources


class _Resource(TypedDict):
    type: str
    id: str
    relationships: NotRequired[dict[str, Relationship]]
    links: Links


class LanguageResource(_Resource):
    attributes: LanguageAttributes


class ProjectResource(_Resource):
    attributes: ProjectAttributes


class LanguageVersionResource(_Resource):
    attributes: LanguageVersionAttributes


class StringResource(_Resource):
    attributes: StringAttributes


class TranslationResource(_Resource):
    attributes: TranslationAttributes


# Documents


class LanguageDocument(DocumentEnvelope):
    data: LanguageResource


class LanguageListDocument(DocumentEnvelope):
    data: list[LanguageResource]


class ProjectDocument(DocumentEnvelope):
    data: ProjectResource


class ProjectListDocument(DocumentEnvelope):
    data: list[ProjectResource]


class LanguageVersionDocument(DocumentEnvelope):
    data: LanguageVersionResource


class LanguageVersionListDocument(DocumentEnvelope):
    data: list[LanguageVersionResource]


class StringDocument(DocumentEnvelope):
    data: StringResource


class StringListDocument(DocumentEnvelope):
    data: list[StringResource]


class TranslationDocument(DocumentEnvelope):
    data: TranslationResource


class TranslationListDocument(DocumentEnvelope):
    data: list[TranslationResource]


# Builders


@dataclass
class ResourceBuilder:
    """
    Builds resource objects of one request, and collects included ones.

    Relationships named in *include* get full linkage,
    and their resources are added to ``included``.
    Only one level of inclusion is supported.
    """

    request: HttpRequest
    include: frozenset[str] = frozenset()
    _included: dict[tuple[str, str], ResourceObject[Any]] = field(default_factory=dict)

    def included(self) -> list[ResourceObject[Any]] | None:
        """Included resources, ``None`` when nothing was asked."""
        if not self.include:
            return None
        return list(self._included.values())

    def url(self, name: str, *args: Any) -> str:
        return self.request.build_absolute_uri(
            reverse(f"{URL_NAMESPACE}:{name}", args=args)
        )

    def language(self, language: Language) -> LanguageResource:
        attributes: LanguageAttributes = {
            "name": language.name,
            "direction": language.direction,  # type: ignore[typeddict-item]
            "pluralForms": language.plural_forms,
            "pluralExamples": language.plural_examples_list(),
            "google": language.google,
            "deepl": language.deepl,
            "yandex": language.yandex,
        }
        return resource_object(  # type: ignore[return-value]
            LANGUAGES,
            language.code,
            attributes,
            links={"self": self.url("language", language.code)},
        )

    def project(self, project: Project) -> ProjectResource:
        attributes: ProjectAttributes = {
            "name": project.name,
            "url": project.url,
            "description": project.description,
            "image": (
                self.request.build_absolute_uri(project.image.url)
                if project.image
                else None
            ),
            "strings": project.strings,
            "words": project.words,
            "characters": project.characters,
            "locked": project.locked,
            "createDate": project.create_date,
            "lastChange": project.last_change,
        }
        relationships = {
            "sourceLanguage": self._to_one(
                "sourceLanguage",
                LANGUAGES,
                project.source_language_id,
                related=self.url("language", project.source_language_id),
                resource=lambda: self.language(project.source_language),
            ),
            "languageVersions": self._to_many(
                "languageVersions",
                LANGUAGE_VERSIONS,
                related=self.url("project-language-versions", project.pk),
                resources=lambda: [
                    self.language_version(lv)
                    for lv in project.languageversion_set.all()
                ],
            ),
            "strings": {"links": {"related": self.url("project-strings", project.pk)}},
        }
        return resource_object(  # type: ignore[return-value]
            PROJECTS,
            project.pk,
            attributes,
            relationships=relationships,
            links={"self": self.url("project", project.pk)},
        )

    def language_version(self, lv: LanguageVersion) -> LanguageVersionResource:
        attributes: LanguageVersionAttributes = {
            "translatedStrings": lv.translated_strings,
            "translatedWords": lv.translated_words,
            "translatedCharacters": lv.translated_characters,
            "outdatedStrings": lv.outdated_strings,
            "outdatedWords": lv.outdated_words,
            "outdatedCharacters": lv.outdated_characters,
            "untranslatedStrings": lv.untranslated_strings(),
            "untranslatedWords": lv.untranslated_words(),
            "untranslatedCharacters": lv.untranslated_characters(),
        }
        relationships = {
            "project": self._to_one(
                "project",
                PROJECTS,
                lv.project_id,
                related=self.url("project", lv.project_id),
                resource=lambda: self.project(lv.project),
            ),
            "language": self._to_one(
                "language",
                LANGUAGES,
                lv.language_id,
                related=self.url("language", lv.language_id),
                resource=lambda: self.language(lv.language),
            ),
        }
        return resource_object(  # type: ignore[return-value]
            LANGUAGE_VERSIONS,
            lv.pk,
            attributes,
            relationships=relationships,
            links={"self": self.url("language-version", lv.pk)},
        )

    def string(self, trstring: TrString) -> StringResource:
        attributes: StringAttributes = {
            "path": trstring.path,
            "name": trstring.name,
            "context": trstring.context,
            "words": trstring.words,
            "characters": trstring.characters,
            "lastChange": trstring.last_change,
        }
        relationships = {
            "project": self._to_one(
                "project",
                PROJECTS,
                trstring.project_id,
                related=self.url("project", trstring.project_id),
                resource=lambda: self.project(trstring.project),
            ),
            "translations": self._to_many(
                "translations",
                TRANSLATIONS,
                related=self.url("string-translations", trstring.pk),
                resources=lambda: [
                    self.translation(text) for text in trstring.trstringtext_set.all()
                ],
            ),
        }
        return resource_object(  # type: ignore[return-value]
            STRINGS,
            trstring.pk,
            attributes,
            relationships=relationships,
            links={"self": self.url("string", trstring.pk)},
        )

    def translation(self, text: TrStringText) -> TranslationResource:
        attributes: TranslationAttributes = {
            "pluralized": text.pluralized,
            "texts": translation_texts(text),
            "state": (
                "outdated" if text.state == TRANSLATION_STATE_OUTDATED else "translated"
            ),
            "lastChange": text.last_change,
        }
        relationships = {
            "string": self._to_one(
                "string",
                STRINGS,
                text.trstring_id,
                related=self.url("string", text.trstring_id),
                resource=lambda: self.string(text.trstring),
            ),
            "language": self._to_one(
                "language",
                LANGUAGES,
                text.language_id,
                related=self.url("language", text.language_id),
                resource=lambda: self.language(text.language),
            ),
        }
        return resource_object(  # type: ignore[return-value]
            TRANSLATIONS,
            text.pk,
            attributes,
            relationships=relationships,
            links={"self": self.url("translation", text.pk)},
        )

    def _add(self, resource: Any) -> None:
        self._included.setdefault((resource["type"], resource["id"]), resource)

    def _to_one(self, name, resource_type, resource_id, *, related, resource):
        if resource_id is None:
            return relationship_to_one(None, links={"related": related})
        if name in self.include:
            self._add(self._nested_call(resource))
        return relationship_to_one(
            resource_identifier(resource_type, resource_id),
            links={"related": related},
        )

    def _to_many(self, name, resource_type, *, related, resources):
        if name not in self.include:
            return {"links": {"related": related}}
        nested = self._nested_call(resources)
        for item in nested:
            self._add(item)
        return relationship_to_many(
            (resource_identifier(resource_type, item["id"]) for item in nested),
            links={"related": related},
        )

    def _nested_call(self, build):
        """Run *build* with a builder that does not include anything."""
        include, self.include = self.include, frozenset()
        try:
            return build()
        finally:
            self.include = include


def translation_texts(text: TrStringText) -> list[str]:
    """
    All forms of a text, one item when it is not pluralized.

    Pluralized texts are stored as JSON arrays.
    """
    if not text.pluralized:
        return [text.text]
    try:
        texts = json.loads(text.text)
    except ValueError:
        return [text.text]
    if not isinstance(texts, list):
        return [text.text]
    return [str(item) for item in texts]
