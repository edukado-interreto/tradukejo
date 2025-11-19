from django.conf import settings
from django.conf.urls.i18n import i18n_patterns
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path, re_path

from tradukejo.api import urls as api_urls


urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include(api_urls)),
    re_path(r"^i18n/", include("django.conf.urls.i18n")),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


urlpatterns += i18n_patterns(
    path("", include("traduko.urls")),
    path("", include("users.urls")),
)
