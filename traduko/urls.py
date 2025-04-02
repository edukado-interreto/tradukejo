from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, re_path
from django.views.generic import TemplateView

from traduko import views, ajax, admin_views, vue_translation

urlpatterns = [
    path("", views.projects, name="projects"),
    path("project/<int:project_id>/", views.projectpage, name="project"),
    path(
        "translate/<int:project_id>/",
        views.translate,
        name="translate_without_language",
    ),
    path(
        "translate/<int:project_id>/<str:language>/", views.translate, name="translate"
    ),
    path(
        "ajax/request-translator-permission/<int:project_id>/",
        ajax.request_translator_permission,
        name="request_translator_permission",
    ),
    path(
        "project/<int:project_id>/add-language-version/<str:language>/",
        views.add_language_version,
        name="add_language_version",
    ),
    path(
        "project/<int:project_id>/edit/", admin_views.edit_project, name="edit_project"
    ),
    path(
        "project/<int:project_id>/translator-requests/",
        admin_views.translator_request_list,
        name="translator_request_list",
    ),
    path(
        "project/accept-translator-request/<int:request_id>/",
        admin_views.accept_translator_request,
        name="accept_translator_request",
    ),
    path(
        "project/decline-translator-request/<int:request_id>/",
        admin_views.decline_translator_request,
        name="decline_translator_request",
    ),
    path(
        "project/<int:project_id>/send-notifications/",
        admin_views.translator_notifications,
        name="translator_notifications",
    ),
    path(
        "project/<int:project_id>/import-export/",
        admin_views.import_export,
        name="import_export",
    ),
    path(
        "project/<int:project_id>/import/csv/",
        admin_views.import_csv,
        name="import_csv",
    ),
    path(
        "project/<int:project_id>/export/csv/",
        admin_views.export_csv,
        name="export_csv",
    ),
    path(
        "project/<int:project_id>/import/json/",
        admin_views.import_json,
        name="import_json",
    ),
    path(
        "project/<int:project_id>/export/json/",
        admin_views.export_json,
        name="export_json",
    ),
    path(
        "project/<int:project_id>/import/po/", admin_views.import_po, name="import_po"
    ),
    path(
        "project/<int:project_id>/export/po/", admin_views.export_po, name="export_po"
    ),
    path(
        "project/<int:project_id>/import/nested-json/",
        admin_views.import_nested_json,
        name="import_nested_json",
    ),
    path(
        "project/<int:project_id>/export/nested-json/",
        admin_views.export_nested_json,
        name="export_nested_json",
    ),
    path(
        "project/<int:project_id>/import/history/",
        admin_views.import_history,
        name="import_history",
    ),
    path(
        "contact/",
        TemplateView.as_view(template_name="traduko/contact.html"),
        name="contact",
    ),
    path(
        "instructions/",
        TemplateView.as_view(template_name="traduko/instructions.html"),
        name="instructions",
    ),
    path(
        "privacy/",
        TemplateView.as_view(template_name="traduko/privacy.html"),
        name="privacy",
    ),
    path(
        "terms/", TemplateView.as_view(template_name="traduko/terms.html"), name="terms"
    ),
    path("vue/get-strings/", vue_translation.get_strings, name="vue_get_strings"),
    path(
        "vue/get-directories-tree/",
        vue_translation.get_directories_tree,
        name="vue_get_directories_tree",
    ),
    path(
        "vue/get-string-translation/",
        vue_translation.get_string_translation,
        name="vue_get_string_translation",
    ),
    path("vue/mark-outdated/", vue_translation.markoutdated, name="vue_markoutdated"),
    path(
        "vue/mark-translated/",
        vue_translation.marktranslated,
        name="vue_marktranslated",
    ),
    path("vue/delete-string/", vue_translation.delete_string, name="vue_deletestring"),
    path(
        "vue/save-translation/",
        vue_translation.save_translation,
        name="vue_save_translation",
    ),
    path("vue/add-string/", vue_translation.add_string, name="vue_add_string"),
    path("vue/get-history/", vue_translation.get_history, name="vue_get_history"),
    path("vue/get-comments/", vue_translation.get_comments, name="vue_get_comments"),
    path("vue/save-comment/", vue_translation.save_comment, name="vue_save_comment"),
    path(
        "vue/delete-comment/", vue_translation.delete_comment, name="vue_delete_comment"
    ),
    path(
        "vue/get-translation-suggestions/",
        vue_translation.get_translation_suggestions,
        name="vue_get_translation_suggestions",
    ),
]

if settings.DEBUG:
    urlpatterns.extend(static(settings.STATIC_URL, document_root=settings.STATIC_ROOT))
