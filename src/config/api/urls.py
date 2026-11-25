from typing import Final

from dmr.openapi import build_schema
from dmr.openapi.views import OpenAPIJsonView, RedocView, SwaggerView
from dmr.routing import Router, path

from traduko.api import controllers

_EXPORT_ROUTES: Final = (
    ("project/<int:pk>/export/nested/", controllers.ExportNestedController),
    ("project/<int:pk>/export/po/", controllers.ExportPoController),
    ("project/<int:pk>/export/", controllers.ExportSimpleController),
)


def _export_paths(route: str, controller: type[controllers.ExportController]):
    """Bare route plus one `<stem>.<format>` route per accepted format."""
    suffixed = [
        path(f"{route}<slug:stem>.{fmt}", controller.as_view(), {"format": fmt})
        for fmt in controller.accept_formats
    ]
    return [*suffixed, path(route, controller.as_view())]


router = Router(
    "api/",
    [
        *(p for route, ctrl in _EXPORT_ROUTES for p in _export_paths(route, ctrl)),
        path(
            "project/<int:pk>/languages/",
            controllers.LanguageListController.as_view(),
            name="languages",
        ),
    ],
)

schema = build_schema(router)

urlpatterns = [
    router.to_urlpatterns(),
    path("api/docs", RedocView.as_view(schema), name="redoc"),
    path("api/schema", OpenAPIJsonView.as_view(schema), name="schema"),
    path("api/swagger", SwaggerView.as_view(schema), name="swagger"),
]
