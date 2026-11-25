"""Routes, docs and error handlers of the JSON:API v3, under ``/api/v3/``."""

from collections.abc import Callable
from http import HTTPStatus
from typing import Any, Final

from dmr.openapi import OpenAPIConfig, build_schema
from dmr.openapi.views import OpenAPIJsonView, RedocView, SwaggerView
from dmr.plugins.msgspec import MsgspecSerializer
from dmr.routing import Router, build_404_handler, build_500_handler, path
from dmr_jsonapi import JsonApiRenderer
from dmr_jsonapi.errors import format_error, with_status

from traduko.api.v3 import controllers
from traduko.api.v3.resources import URL_NAMESPACE

PREFIX: Final = "api/v3/"

router = Router(
    PREFIX,
    [
        path(
            "languages/",
            controllers.LanguageListController.as_view(),
            name="languages",
        ),
        path(
            "languages/<str:code>/",
            controllers.LanguageDetailController.as_view(),
            name="language",
        ),
        path(
            "projects/",
            controllers.ProjectListController.as_view(),
            name="projects",
        ),
        path(
            "projects/<int:pk>/",
            controllers.ProjectDetailController.as_view(),
            name="project",
        ),
        path(
            "projects/<int:pk>/language-versions/",
            controllers.ProjectLanguageVersionListController.as_view(),
            name="project-language-versions",
        ),
        path(
            "projects/<int:pk>/strings/",
            controllers.ProjectStringListController.as_view(),
            name="project-strings",
        ),
        path(
            "language-versions/<int:pk>/",
            controllers.LanguageVersionDetailController.as_view(),
            name="language-version",
        ),
        path(
            "strings/<int:pk>/",
            controllers.StringDetailController.as_view(),
            name="string",
        ),
        path(
            "strings/<int:pk>/translations/",
            controllers.StringTranslationListController.as_view(),
            name="string-translations",
        ),
        path(
            "translations/<int:pk>/",
            controllers.TranslationDetailController.as_view(),
            name="translation",
        ),
    ],
)

schema = build_schema(
    router,
    config=OpenAPIConfig(
        title="Tradukejo API",
        version="3.0",
        description=(
            "Read-only [JSON:API](https://jsonapi.org/) of tradukejo.ikso.net."
            " Exports are still served by the API v1, under /api/."
        ),
    ),
)

urlpatterns = [
    router.to_urlpatterns(namespace=URL_NAMESPACE),
    path(f"{PREFIX}docs", RedocView.as_view(schema), name="v3-redoc"),
    path(f"{PREFIX}schema", OpenAPIJsonView.as_view(schema), name="v3-schema"),
    path(f"{PREFIX}swagger", SwaggerView.as_view(schema), name="v3-swagger"),
]


def _format_error_with(status_code: HTTPStatus) -> Callable[..., Any]:
    """Project-wide handlers don't fill ``status``, so we do it."""

    def factory(error: str | Exception, **kwargs: Any) -> Any:
        return with_status(format_error(error, **kwargs), status_code)

    return factory


handler404 = build_404_handler(
    PREFIX,
    serializer=MsgspecSerializer,
    format_error=_format_error_with(HTTPStatus.NOT_FOUND),
    renderers=[JsonApiRenderer()],
)
handler500 = build_500_handler(
    PREFIX,
    serializer=MsgspecSerializer,
    format_error=_format_error_with(HTTPStatus.INTERNAL_SERVER_ERROR),
    renderers=[JsonApiRenderer()],
)
