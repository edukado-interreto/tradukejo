from django.urls import path, re_path

from traduko import views, ajax

urlpatterns = [
    path("", views.projects, name="projects"),
    path("project/<int:project_id>/", views.projectpage, name="project"),
    path("translate/<int:project_id>/<str:language>/", views.translate, name="translate"),
    path("ajax/save/<int:trstring_id>/<str:language>/", ajax.save_translation, name="save_translation"),
    path("ajax/get-string-translation/<int:trstring_id>/<str:language>/", ajax.get_string_translation, name="get_string_translation"),
    path("ajax/markoutdated/<int:trstringtext_id>/", ajax.markoutdated, name="markoutdated"),
    path("ajax/marktranslated/<int:trstringtext_id>/", ajax.marktranslated, name="marktranslated"),
    path("ajax/deletestring/<int:trstring_id>/", ajax.deletestring, name="deletestring"),
    path("ajax/get-history/<int:trstringtext_id>/", ajax.get_history, name="get_history"),
    path("ajax/request-translator-permission/<int:project_id>/", ajax.request_translator_permission, name="request_translator_permission"),
    path("project/<int:project_id>/add-language-version/<str:language>/", views.add_language_version, name="add_language_version"),
    path("project/<int:project_id>/translator-requests/", views.translator_request_list, name="translator_request_list"),
    path("project/accept-translator-request/<int:request_id>/", views.accept_translator_request, name="accept_translator_request"),
    path("project/decline-translator-request/<int:request_id>/", views.decline_translator_request, name="decline_translator_request"),
    path("project/<int:project_id>/add-string/", views.add_string, name="add_string"),
]
