from django.contrib import messages
from django.http import Http404, RawPostDataException
from django.shortcuts import get_object_or_404, redirect
from .models import *
from .translation_functions import *
from django.core.exceptions import PermissionDenied


def find_project_from_params(all_arguments):
    if 'trstringtext_id' in all_arguments.keys():
        trstringtext = get_object_or_404(TrStringText, pk=all_arguments['trstringtext_id'])
        project = trstringtext.trstring.project
    else:
        if 'project_id' in all_arguments.keys():
            project = get_object_or_404(Project, pk=all_arguments['project_id'])
        elif 'trstring_id' in all_arguments.keys():
            project = get_object_or_404(TrString, pk=all_arguments['trstring_id']).project
        elif 'request_id' in all_arguments.keys():
            project = get_object_or_404(TranslatorRequest, pk=all_arguments['request_id']).language_version.project
        elif 'comment_id' in all_arguments.keys():
            project = get_object_or_404(Comment, pk=all_arguments['comment_id']).trstringtext.trstring.project
        else:
            raise Http404()
    return project


def find_language_from_params(all_arguments):
    if 'trstringtext_id' in all_arguments.keys():
        trstringtext = get_object_or_404(TrStringText, pk=all_arguments['trstringtext_id'])
        language = trstringtext.language
    else:
        if 'language' in all_arguments.keys():
            language = get_object_or_404(Language, code=all_arguments['language'])
        else:
            raise Http404()
    return language


def user_allowed_to_translate(function):
    def wrap(request, *args, **kwargs):
        try:
            json_postdata = json.loads(request.body.decode('utf-8'))
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
            json_postdata = json.loads(request.body.decode('utf-8'))
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
            json_postdata = json.loads(request.body.decode('utf-8'))
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
