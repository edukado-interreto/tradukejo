from typing import Callable

from django.http.response import HttpResponseBase
from django.urls import path
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)
from rest_framework.urlpatterns import format_suffix_patterns

from traduko.api import views as api_views

# Types:
from traduko.api.views import ViewSetClass

Route = str
View = Callable[..., HttpResponseBase]

SUFFIX_REQUIRED = True


def format_suffix_pattern(route: Route, view: View, allowed: list[str]):
    pattern = path(f"{route}<slug:stem>", view)
    return format_suffix_patterns([pattern], SUFFIX_REQUIRED, allowed)[0]


def route_with_suffix(route: Route, view_class: ViewSetClass):
    """Generate pattern with suffix first, then normal pattern"""
    view = view_class.as_view(actions={"get": "retrieve"})
    with_suffix = format_suffix_pattern(route, view, allowed=view_class.accept_formats)
    return [with_suffix, path(route, view)]


def paths_with_suffix(*routes: tuple[Route, ViewSetClass]):
    """Generate and flatten patterns with their suffixes

    Routhly equivalent to:
    return [
        path("export/<slug:stem>.<ext:format>", ViewSet.as_view({"get": "retrieve"})),
        path("export/", ViewSet.as_view({"get": "retrieve"})),
        ...
    ]
    """
    return [p for args in routes for p in route_with_suffix(*args)]


urlpatterns = [
    *paths_with_suffix(
        ("project/<int:pk>/export/nested/", api_views.ExportNested),
        ("project/<int:pk>/export/po/", api_views.ExportPo),
        ("project/<int:pk>/export/", api_views.ExportSimple),
    ),
    path(
        "project/<int:pk>/languages/",
        api_views.LanguageListView.as_view(),
        name="languages",
    ),
    path("docs", SpectacularRedocView.as_view(), name="redoc"),
    path("schema", SpectacularAPIView.as_view(), name="schema"),
    path("swagger", SpectacularSwaggerView.as_view(), name="swagger"),
]
