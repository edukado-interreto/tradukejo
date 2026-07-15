import json

from django.core.exceptions import PermissionDenied
from django.http import Http404, RawPostDataException
from django.shortcuts import get_object_or_404

from traduko.translation_functions import (
    is_allowed_to_translate,
    is_project_admin,
    user_has_translation_right,
)

from .models import (
    Comment,
    Language,
    Project,
    TranslatorRequest,
    TrString,
    TrStringText,
)


def find_project_from_params(args):
    match args:
        case {"trstringtext_id": text_id}:
            return get_object_or_404(TrStringText, pk=text_id).trstring.project

        case {"project_id": project_id}:
            return get_object_or_404(Project, pk=project_id)

        case {"trstring_id": string_id}:
            return get_object_or_404(TrString, pk=string_id).project

        case {"request_id": request_id}:
            qs = TranslatorRequest.objects.select_related("language_version__project")
            tr_request = get_object_or_404(qs, pk=request_id)
            return tr_request.language_version.project

        case {"comment_id": comment_id}:
            qs = Comment.objects.select_related("trstringtext__trstring__project")
            comment = get_object_or_404(qs, pk=comment_id)
            return comment.trstringtext.trstring.project

        case _:
            raise Http404("No valid project identifier found in parameters.")


def find_language_from_params(all_arguments):
    if "trstringtext_id" in all_arguments.keys():
        trstringtext = get_object_or_404(
            TrStringText, pk=all_arguments["trstringtext_id"]
        )
        language = trstringtext.language
    else:
        if "language" in all_arguments.keys():
            language = get_object_or_404(Language, code=all_arguments["language"])
        else:
            raise Http404()
    return language


def user_allowed_to_translate(function):
    def wrap(request, *args, **kwargs):
        try:
            json_postdata = json.loads(request.body.decode("utf-8"))
            all_arguments = {**kwargs, **json_postdata}
        except json.JSONDecodeError:
            all_arguments = kwargs
        project = find_project_from_params(all_arguments)
        language = find_language_from_params(all_arguments)

        allowed = is_allowed_to_translate(request.user, project, language)

        if allowed:
            return function(request, *args, **kwargs)
        else:
            raise PermissionDenied()

    wrap.__doc__ = function.__doc__
    wrap.__name__ = function.__name__
    return wrap


def user_has_any_right_for_project(function):
    def wrap(request, *args, **kwargs):
        try:
            json_postdata = json.loads(request.body.decode("utf-8"))
            all_arguments = {**kwargs, **json_postdata}
        except json.JSONDecodeError:
            all_arguments = kwargs

        project = find_project_from_params(all_arguments)

        allowed = user_has_translation_right(request.user, project)

        if allowed:
            return function(request, *args, **kwargs)
        else:
            raise PermissionDenied()

    wrap.__doc__ = function.__doc__
    wrap.__name__ = function.__name__
    return wrap


def user_is_project_admin(function):
    def wrap(request, *args, **kwargs):
        try:
            json_postdata = json.loads(request.body.decode("utf-8"))
            all_arguments = {**kwargs, **json_postdata}
        except json.JSONDecodeError:
            all_arguments = kwargs
        except RawPostDataException:
            all_arguments = kwargs

        project = find_project_from_params(all_arguments)

        allowed = is_project_admin(request.user, project)

        if allowed:
            return function(request, *args, **kwargs)
        else:
            raise PermissionDenied()

    wrap.__doc__ = function.__doc__
    wrap.__name__ = function.__name__
    return wrap
