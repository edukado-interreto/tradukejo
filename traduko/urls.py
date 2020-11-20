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
]
