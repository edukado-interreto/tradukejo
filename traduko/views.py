from django.shortcuts import render, get_object_or_404, redirect, reverse
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

    user_is_project_admin = is_project_admin(request.user, current_project)

    context = {
        'my_languages_with_stats': languages_with_stats['current_user'],
        'available_languages_with_stats': languages_with_stats['other_available'],
        'project': current_project,
        'is_project_admin': user_is_project_admin,
        'addible_languages': addible_languages(current_project)
    }

    if user_is_project_admin:
        context['translator_request_count'] = TranslatorRequest.objects.filter(language_version__project=current_project).count()

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

    # Data from query string
    current_directory = request.GET['dir'].strip('/') if 'dir' in request.GET.keys() else ''
    state_filter = request.GET['state'] if 'state' in request.GET.keys() else STATE_FILTER_ALL
    sort = request.GET['sort'] if 'sort' in request.GET.keys() else SORT_STRINGS_BY_NAME
    search_string = request.GET['q'] if 'q' in request.GET.keys() else ''

    all_strings = TrString.objects.filter(project=current_project)
    all_strings = filter_by_state(all_strings, language, state_filter)
    all_strings = filter_by_search(all_strings, language, search_string)
    strings = all_strings.filter(path=current_directory)
    if sort == SORT_STRINGS_BY_NEWEST:
        strings = strings.order_by('-last_change')
    else:
        strings = strings.order_by('name')

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
        'sort': sort,
        'q': search_string,
        'available_languages': available_languages,
    }
    return render(request, "traduko/translate.html", context)


@login_required
def add_language_version(request, project_id, language):
    project = get_object_or_404(Project, pk=project_id)
    if is_project_admin(request.user, project):
        lang = get_object_or_404(Language, code=language)
        if LanguageVersion.objects.filter(project=project, language=lang).count() == 0:
            LanguageVersion(project=project, language=lang).save()
            messages.success(request, 'La lingvo ' + lang.name + ' estis aldonita.')

    return redirect('project', project_id)


@login_required
def translator_request_list(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    if not is_project_admin(request.user, project):
        messages.error(request, 'Vi ne rajtas vidi ĉi tiun paĝon.')
        return redirect('project', project_id)

    requests = TranslatorRequest.objects.filter(language_version__project=project).order_by('-create_date')

    context = {
        'project': project,
        'requests': requests
    }
    return render(request, "traduko/project-translator-requests.html", context)


@login_required
def accept_translator_request(request, request_id):
    translatorrequest = get_object_or_404(TranslatorRequest, pk=request_id)
    if not is_project_admin(request.user, translatorrequest.language_version.project):
        messages.error(request, 'Vi ne rajtas vidi ĉi tiun paĝon.')
        return redirect('project', translatorrequest.language_version.project.pk)

    translatorrequest.language_version.translators.add(translatorrequest.user)
    translatorrequest.language_version.save()
    translatorrequest.delete()

    # TODO send mail confirmation

    return redirect('translator_request_list', translatorrequest.language_version.project.pk)


@login_required
def decline_translator_request(request, request_id):
    translatorrequest = get_object_or_404(TranslatorRequest, pk=request_id)
    if not is_project_admin(request.user, translatorrequest.language_version.project):
        messages.error(request, 'Vi ne rajtas vidi ĉi tiun paĝon.')
        return redirect('project', translatorrequest.language_version.project.pk)

    # Delete the language version if no translations
    if TrStringText.objects.filter(trstring__project=translatorrequest.language_version.project, language=translatorrequest.language_version.language).count() == 0:
        translatorrequest.language_version.delete()  # translatorrequest deleted by cascade
    else:
        translatorrequest.delete()

    # TODO send mail confirmation

    return redirect('translator_request_list', translatorrequest.language_version.project.pk)


@login_required
def add_string(request, project_id):
    # TODO: use Django forms
    # TODO: posting pluralized strings
    project = get_object_or_404(Project, pk=project_id)
    if not is_project_admin(request.user, project):
        messages.error(request, 'Vi ne rajtas vidi ĉi tiun paĝon.')
        return redirect('project', project_id)

    name = request.POST.get('name').strip()
    pluralized = bool(request.POST.get('pluralized') == 'true')
    text_data = parse_submitted_text(request.POST.get('text'), pluralized, project.source_language.nplurals())
    path = request.POST.get('path').strip('/ ')
    querystring = '?dir=' + path if path != '' else ''

    if name == '' or text_data['characters'] == 0:
        messages.error(request, 'Bonvolu plenigi ĉiujn kampojn.')
    elif TrString.objects.filter(project=project, path=path, name=name).count() > 0:
        messages.error(request, 'Ĉi tiu nomo ({}#{}) jam estas uzata.'.format(path, name))
    else:
        context = request.POST.get('context').strip()
        trstring = TrString(project=project, path=path, name=name, context=context,
                            words=text_data['words'],
                            characters=text_data['characters'])
        trstring.save()
        trstringtext = TrStringText(trstring=trstring,
                                    language=project.source_language,
                                    text=text_data['text'],
                                    pluralized=pluralized,
                                    translated_by=request.user)
        trstringtext.save()
        update_string_count(project)

    return redirect(reverse('translate', args=[project.pk, project.source_language.code]) + querystring)
