from django.shortcuts import render, get_object_or_404
from .models import *
from .translation_functions import *


def projects(request):
    projects_list = Project.objects.all()
    context = {
        'projects': projects_list
    }
    return render(request, "traduko/projects.html", context)


def project(request, project_id):
    current_project = get_object_or_404(Project, pk=project_id)
    languages_with_stats = get_project_language_statistics(current_project)

    context = {
        'languages_with_stats': languages_with_stats,
        'project': current_project,
    }
    return render(request, "traduko/project.html", context)


def translate(request, project_id, language):
    current_project = get_object_or_404(Project, pk=project_id)
    current_language = get_object_or_404(Language, code=language)
    available_languages = (Language.objects.filter(code=current_project.source_language.code) |
                           Language.objects.filter(languageversion__project=current_project)).\
                            order_by('code') # TODO: languages of current user

    if current_language == current_project.source_language:
        editmode = True
    else:
        editmode = False
        current_language_version = get_object_or_404(LanguageVersion, language=current_language, project=current_project)

    # Data from query string
    current_directory = request.GET['dir'].strip('/') if 'dir' in request.GET.keys() else ''
    state_filter = request.GET['state'] if 'state' in request.GET.keys() else STATE_FILTER_ALL
    search_string = request.GET['q'] if 'q' in request.GET.keys() else ''

    all_strings = TrString.objects.filter(project=current_project)
    all_strings = filter_by_state(all_strings, language, state_filter)
    all_strings = filter_by_search(all_strings, language, search_string)
    strings = all_strings.filter(path=current_directory)

    subdirectories = get_subdirectories(all_strings, current_directory)

    current_path = []
    if current_directory != '':
        directories = current_directory.split('/')
        for i in range(len(directories)):
            current_path.append({
                'name': directories[i],
                'path': '/'.join(directories[0:i+1])
            })

    for trstr in strings:
        trstr.original_text = None
        trstr.translated_text = None
        for trans in trstr.trstringtext_set.all():
            if trans.language == current_project.source_language:
                trstr.original_text = trans
            if trans.language == current_language:
                trstr.translated_text = trans

        if trstr.translated_text is None:
            trstr.state = TRANSLATION_STATE_UNTRANSLATED
        else:
            trstr.state = trstr.translated_text.state

    context = {
        'editmode': editmode,
        'project': current_project,
        'strings': strings,
        'language': current_language,
        'subdirectories': subdirectories,
        'current_path': current_path,
        'current_directory': current_directory,
        'state_filter': state_filter,
        'q': search_string,
        'available_languages': available_languages
    }
    return render(request, "traduko/translate.html", context)
