from django.conf import settings
from django.conf.urls.i18n import i18n_patterns
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path, re_path
from dmr.plugins.msgspec import MsgspecSerializer
from dmr.routing import build_404_handler, build_500_handler

from .api import urls as api_urls
from .api import v3 as api_v3


urlpatterns = [
    path("admin/", admin.site.urls),
    *api_v3.urlpatterns,
    *api_urls.urlpatterns,
    re_path(r"^i18n/", include("django.conf.urls.i18n")),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


urlpatterns += i18n_patterns(
    path("", include("traduko.urls")),
    path("", include("users.urls")),
)

_api_404 = build_404_handler(api_urls.router.prefix, serializer=MsgspecSerializer)
_api_500 = build_500_handler(api_urls.router.prefix, serializer=MsgspecSerializer)


def _is_api_v3(request) -> bool:
    return request.path_info.startswith(f"/{api_v3.PREFIX}")


def handler404(request, exception):
    if _is_api_v3(request):
        return api_v3.handler404(request, exception)
    return _api_404(request, exception)


def handler500(request):
    if _is_api_v3(request):
        return api_v3.handler500(request)
    return _api_500(request)
