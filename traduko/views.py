from django.shortcuts import render, get_object_or_404, redirect
from .models import *
from .translation_functions import *
from django.contrib.auth.decorators import login_required
from django.contrib import messages


def projects(request):
    projects_list = Project.objects.all()
    context = {
        'projects': projects_list
    }
    return render(request, "traduko/projects.html", context)


@login_required
def projectpage(request, project_id):
    current_project = get_object_or_404(Project, pk=project_id)
    languages_with_stats = get_project_language_statistics(current_project, request.user)

    context = {
        'my_languages_with_stats': languages_with_stats['current_user'],
        'available_languages_with_stats': languages_with_stats['other_available'],
        'project': current_project,
        'is_project_admin': is_project_admin(request.user, current_project),
        'addible_languages': addible_languages(current_project)
    }
    return render(request, "traduko/project.html", context)


@login_required
def translate(request, project_id, language):
    current_project = get_object_or_404(Project, pk=project_id)
    current_language = get_object_or_404(Language, code=language)

    if not is_allowed_to_translate(request.user, current_project, current_language):
        messages.error(request, 'Vi ne rajtas traduki al tiu lingvo (' + current_language.name + ').')
        return redirect('project', project_id)

    available_languages = get_project_languages_for_user(current_project, request.user)

    if current_language == current_project.source_language:
        editmode = True
    else:
        editmode = False
        current_language_version = get_object_or_404(LanguageVersion, language=current_language,
                                                     project=current_project)

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
                'path': '/'.join(directories[0:i + 1])
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
        'available_languages': available_languages,
        'user_is_project_admin': is_project_admin(request.user, current_project)
    }
    return render(request, "traduko/translate.html", context)
