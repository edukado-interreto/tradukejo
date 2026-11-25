"""
Controllers of the API v3.

All endpoints are read-only. Hidden projects, and everything in them,
are only visible to their admins and to superusers, like on the website.
"""

from http import HTTPStatus
from typing import Any, ClassVar, Final

from django.db.models import Q, QuerySet
from dmr import Path, Query, ResponseSpec
from dmr.plugins.msgspec import MsgspecSerializer
from dmr_jsonapi import JsonApiController, JsonApiError
from dmr_jsonapi.builders import document, pagination_links
from dmr_jsonapi.errors import error_object
from dmr_jsonapi.objects import ErrorDocument, Links, Meta

from traduko.api.v3.queries import (
    CodePath,
    DetailQuery,
    ListQuery,
    PkPath,
    StringListQuery,
    TranslationListQuery,
)
from traduko.api.v3.resources import (
    LanguageDocument,
    LanguageListDocument,
    LanguageVersionDocument,
    LanguageVersionListDocument,
    ProjectDocument,
    ProjectListDocument,
    ResourceBuilder,
    StringDocument,
    StringListDocument,
    TranslationDocument,
    TranslationListDocument,
)
from traduko.models import (
    Language,
    LanguageVersion,
    Project,
    TrString,
    TrStringText,
)

_PROJECT_INCLUDE: Final = frozenset(("sourceLanguage", "languageVersions"))
_LANGUAGE_VERSION_INCLUDE: Final = frozenset(("project", "language"))
_STRING_INCLUDE: Final = frozenset(("project", "translations"))
_TRANSLATION_INCLUDE: Final = frozenset(("string", "language"))


class ApiV3Controller(JsonApiController[MsgspecSerializer]):
    """Shared logic: includes, pagination, 404s and visibility."""

    #: Relationships that can be passed to ``?include=``.
    allowed_include: ClassVar[frozenset[str]] = frozenset()

    responses = (
        ResponseSpec(ErrorDocument, status_code=HTTPStatus.BAD_REQUEST),
        ResponseSpec(ErrorDocument, status_code=HTTPStatus.NOT_FOUND),
    )

    def builder(self, query: DetailQuery) -> ResourceBuilder:
        """Resource builder, checks ``?include=`` first."""
        include = frozenset(
            name.strip() for name in (query.include or "").split(",") if name.strip()
        )
        unknown = sorted(include - self.allowed_include)
        if unknown:
            allowed = ", ".join(sorted(self.allowed_include)) or "nothing"
            raise JsonApiError(
                error_object(
                    f"Cannot include {', '.join(unknown)}. Allowed: {allowed}",
                    code="invalid_include",
                    source={"parameter": "include"},
                ),
                status_code=HTTPStatus.BAD_REQUEST,
            )
        return ResourceBuilder(self.request, include)

    def visible_projects(self) -> QuerySet[Project]:
        user = self.request.user
        if user.is_superuser:
            return Project.objects.all()
        if user.is_authenticated:
            return Project.objects.filter(Q(visible=True) | Q(admins=user)).distinct()
        return Project.objects.filter(visible=True)

    def visible_project(self, pk: int) -> Project:
        return get_or_404(self.visible_projects(), "Project", pk=pk)

    def paginate(
        self,
        queryset: QuerySet[Any],
        query: ListQuery,
    ) -> tuple[list[Any], Links, Meta]:
        """Items of the page, pagination links and the total count."""
        number, size = query.page_number, query.page_size
        total = queryset.count()
        start = (number - 1) * size
        if number > 1 and start >= total:
            raise JsonApiError(
                error_object(
                    f"Page {number} does not exist",
                    code="not_found",
                    source={"parameter": "page[number]"},
                ),
                status_code=HTTPStatus.NOT_FOUND,
            )
        items = list(queryset[start : start + size])
        links = pagination_links(self.request, number=number, size=size, total=total)
        return items, links, {"total": total}

    def self_links(self) -> Links:
        return {"self": self.request.build_absolute_uri()}


def get_or_404(queryset: QuerySet[Any], name: str, **lookup: Any) -> Any:
    """Like ``get_object_or_404``, with a JSON:API error document."""
    try:
        return queryset.get(**lookup)
    except queryset.model.DoesNotExist:
        raise JsonApiError(
            error_object(f"{name} not found", code="not_found"),
            status_code=HTTPStatus.NOT_FOUND,
        ) from None


# Languages


class LanguageListController(ApiV3Controller):
    """All languages known by Tradukejo."""

    def get(self, parsed_query: Query[ListQuery]) -> LanguageListDocument:
        builder = self.builder(parsed_query)
        items, links, meta = self.paginate(
            Language.objects.order_by("code"), parsed_query
        )
        return document(  # type: ignore[return-value]
            [builder.language(language) for language in items],
            links=links,
            meta=meta,
        )


class LanguageDetailController(ApiV3Controller):
    """One language, by its code."""

    def get(
        self,
        parsed_path: Path[CodePath],
        parsed_query: Query[DetailQuery],
    ) -> LanguageDocument:
        builder = self.builder(parsed_query)
        language = get_or_404(Language.objects.all(), "Language", code=parsed_path.code)
        return document(  # type: ignore[return-value]
            builder.language(language),
            links=self.self_links(),
        )


# Projects


class ProjectListController(ApiV3Controller):
    """Projects, newest first."""

    allowed_include = _PROJECT_INCLUDE

    def get(self, parsed_query: Query[ListQuery]) -> ProjectListDocument:
        builder = self.builder(parsed_query)
        queryset = (
            self.visible_projects()
            .select_related("source_language")
            .prefetch_related("languageversion_set__language")
            .order_by("-pk")
        )
        items, links, meta = self.paginate(queryset, parsed_query)
        return document(  # type: ignore[return-value]
            [builder.project(project) for project in items],
            included=builder.included(),
            links=links,
            meta=meta,
        )


class ProjectDetailController(ApiV3Controller):
    """One project."""

    allowed_include = _PROJECT_INCLUDE

    def get(
        self,
        parsed_path: Path[PkPath],
        parsed_query: Query[DetailQuery],
    ) -> ProjectDocument:
        builder = self.builder(parsed_query)
        project = self.visible_project(parsed_path.pk)
        return document(  # type: ignore[return-value]
            builder.project(project),
            included=builder.included(),
            links=self.self_links(),
        )


# Language versions


class ProjectLanguageVersionListController(ApiV3Controller):
    """Languages that a project is translated to, with statistics."""

    allowed_include = _LANGUAGE_VERSION_INCLUDE

    def get(
        self,
        parsed_path: Path[PkPath],
        parsed_query: Query[ListQuery],
    ) -> LanguageVersionListDocument:
        builder = self.builder(parsed_query)
        project = self.visible_project(parsed_path.pk)
        queryset = (
            LanguageVersion.objects.filter(project=project)
            .select_related("project", "language")
            .order_by("language")
        )
        items, links, meta = self.paginate(queryset, parsed_query)
        return document(  # type: ignore[return-value]
            [builder.language_version(lv) for lv in items],
            included=builder.included(),
            links=links,
            meta=meta,
        )


class LanguageVersionDetailController(ApiV3Controller):
    """One language of a project, with statistics."""

    allowed_include = _LANGUAGE_VERSION_INCLUDE

    def get(
        self,
        parsed_path: Path[PkPath],
        parsed_query: Query[DetailQuery],
    ) -> LanguageVersionDocument:
        builder = self.builder(parsed_query)
        lv = get_or_404(
            LanguageVersion.objects.filter(
                project__in=self.visible_projects()
            ).select_related("project", "language"),
            "Language version",
            pk=parsed_path.pk,
        )
        return document(  # type: ignore[return-value]
            builder.language_version(lv),
            included=builder.included(),
            links=self.self_links(),
        )


# Strings


class ProjectStringListController(ApiV3Controller):
    """
    Strings of a project, ordered by path and name.

    ``?include=translations`` adds the texts of all languages,
    the source language included.
    """

    allowed_include = _STRING_INCLUDE

    def get(
        self,
        parsed_path: Path[PkPath],
        parsed_query: Query[StringListQuery],
    ) -> StringListDocument:
        builder = self.builder(parsed_query)
        project = self.visible_project(parsed_path.pk)
        queryset = (
            TrString.objects.filter(project=project)
            .select_related("project")
            .prefetch_related("trstringtext_set__language")
            .order_by("path", "name", "pk")
        )
        if parsed_query.filter_path is not None:
            queryset = queryset.filter(path=parsed_query.filter_path)
        items, links, meta = self.paginate(queryset, parsed_query)
        return document(  # type: ignore[return-value]
            [builder.string(trstring) for trstring in items],
            included=builder.included(),
            links=links,
            meta=meta,
        )


class StringDetailController(ApiV3Controller):
    """One string."""

    allowed_include = _STRING_INCLUDE

    def get(
        self,
        parsed_path: Path[PkPath],
        parsed_query: Query[DetailQuery],
    ) -> StringDocument:
        builder = self.builder(parsed_query)
        trstring = get_or_404(
            TrString.objects.filter(project__in=self.visible_projects())
            .select_related("project")
            .prefetch_related("trstringtext_set__language"),
            "String",
            pk=parsed_path.pk,
        )
        return document(  # type: ignore[return-value]
            builder.string(trstring),
            included=builder.included(),
            links=self.self_links(),
        )


# Translations


class StringTranslationListController(ApiV3Controller):
    """Texts of a string in all languages, the source language included."""

    allowed_include = _TRANSLATION_INCLUDE

    def get(
        self,
        parsed_path: Path[PkPath],
        parsed_query: Query[TranslationListQuery],
    ) -> TranslationListDocument:
        builder = self.builder(parsed_query)
        trstring = get_or_404(
            TrString.objects.filter(project__in=self.visible_projects()),
            "String",
            pk=parsed_path.pk,
        )
        queryset = (
            TrStringText.objects.filter(trstring=trstring)
            .select_related("trstring__project", "language")
            .order_by("language")
        )
        if parsed_query.filter_language is not None:
            queryset = queryset.filter(language=parsed_query.filter_language)
        items, links, meta = self.paginate(queryset, parsed_query)
        return document(  # type: ignore[return-value]
            [builder.translation(text) for text in items],
            included=builder.included(),
            links=links,
            meta=meta,
        )


class TranslationDetailController(ApiV3Controller):
    """One text of a string in one language."""

    allowed_include = _TRANSLATION_INCLUDE

    def get(
        self,
        parsed_path: Path[PkPath],
        parsed_query: Query[DetailQuery],
    ) -> TranslationDocument:
        builder = self.builder(parsed_query)
        text = get_or_404(
            TrStringText.objects.filter(
                trstring__project__in=self.visible_projects()
            ).select_related("trstring__project", "language"),
            "Translation",
            pk=parsed_path.pk,
        )
        return document(  # type: ignore[return-value]
            builder.translation(text),
            included=builder.included(),
            links=self.self_links(),
        )
