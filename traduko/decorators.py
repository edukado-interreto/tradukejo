from django.contrib import messages
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect
from .models import *
from .translation_functions import *
from django.core.exceptions import PermissionDenied


def user_allowed_to_translate(function):
    def wrap(request, *args, **kwargs):
        try:
            json_postdata = json.loads(request.body.decode('utf-8'))
            all_arguments = {**kwargs, **json_postdata}
        except json.JSONDecodeError:
            all_arguments = kwargs

        if 'trstringtext_id' in all_arguments.keys():
            trstringtext = get_object_or_404(TrStringText, pk=all_arguments['trstringtext_id'])
            language = trstringtext.language
            project = trstringtext.trstring.project
        else:
            if 'language' in all_arguments.keys():
                language = get_object_or_404(Language, code=all_arguments['language'])
            else:
                raise Http404()

            if 'project_id' in all_arguments.keys():
                project = get_object_or_404(Project, pk=all_arguments['project_id'])
            elif 'trstring_id' in all_arguments.keys():
                project = get_object_or_404(TrString, pk=all_arguments['trstring_id']).project
            elif 'request_id' in all_arguments.keys():
                project = get_object_or_404(TranslatorRequest, pk=all_arguments['request_id']).language_version.project
            else:
                raise Http404()

        allowed = is_allowed_to_translate(request.user, project, language)

        if allowed:
            return function(request, *args, **kwargs)
        else:
            messages.error(request, f"Vi ne rajtas traduki al tiu lingvo ({language.name}).")
            return redirect('project', project.pk)
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

        if 'project_id' in all_arguments.keys():
            project = get_object_or_404(Project, pk=all_arguments['project_id'])
        elif 'trstring_id' in all_arguments.keys():
            project = get_object_or_404(TrString, pk=all_arguments['trstring_id']).project
        elif 'trstringtext_id' in all_arguments.keys():
            project = get_object_or_404(TrStringText, pk=all_arguments['trstringtext_id']).trstring.project
        elif 'request_id' in all_arguments.keys():
            project = get_object_or_404(TranslatorRequest, pk=all_arguments['request_id']).language_version.project
        else:
            raise Http404()

        allowed = is_project_admin(request.user, project)

        if allowed:
            return function(request, *args, **kwargs)
        else:
            raise PermissionDenied()
    wrap.__doc__ = function.__doc__
    wrap.__name__ = function.__name__
    return wrap
