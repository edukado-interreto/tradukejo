from django.conf import settings
from django.conf.urls.i18n import i18n_patterns
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path, re_path
from dmr.plugins.msgspec import MsgspecSerializer
from dmr.routing import build_404_handler, build_500_handler

from .api import urls as api_urls


urlpatterns = [
    path("admin/", admin.site.urls),
    *api_urls.urlpatterns,
    re_path(r"^i18n/", include("django.conf.urls.i18n")),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


urlpatterns += i18n_patterns(
    path("", include("traduko.urls")),
    path("", include("users.urls")),
)

handler404 = build_404_handler(api_urls.router.prefix, serializer=MsgspecSerializer)
handler500 = build_500_handler(api_urls.router.prefix, serializer=MsgspecSerializer)
