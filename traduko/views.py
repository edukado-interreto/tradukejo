from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render, get_object_or_404, redirect, reverse
from .models import *
from .translation_functions import *
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .decorators import *
from django.db.models import Q


def projects(request):
    if request.user.is_superuser:
        projects_list = Project.objects.all()
    elif request.user.is_authenticated:
        projects_list = Project.objects.filter(Q(visible=True) | Q(admins=request.user)).distinct()
    else:
        projects_list = Project.objects.filter(visible=True)

    projects_list = projects_list.order_by('-pk')
    context = {
        'projects': projects_list
    }
    return render(request, "traduko/projects.html", context)


@login_required
def projectpage(request, project_id):
    current_project = get_object_or_404(Project, pk=project_id)
    project_admin = is_project_admin(request.user, current_project)

    if not current_project.visible and not project_admin:
        raise PermissionDenied()

    if project_admin:
        if current_project.last_translator_notification is None:
            show_translator_notifications_button = True
        else:
            new_texts = TrString.objects.filter(project=current_project, last_change__gte=current_project.last_translator_notification).count()
            show_translator_notifications_button = new_texts > 0
    else:
        show_translator_notifications_button = False

    languages_with_stats = get_project_language_statistics(current_project, request.user)

    context = {
        'my_languages_with_stats': languages_with_stats['current_user'],
        'available_languages_with_stats': languages_with_stats['other_available'],
        'project': current_project,
        'is_project_admin': project_admin,
        'addible_languages': addible_languages(current_project),
        'show_translator_notifications_button': show_translator_notifications_button,
    }

    if user_is_project_admin:
        context['translator_request_count'] = TranslatorRequest.objects.filter(language_version__project=current_project).count()

    return render(request, "traduko/project.html", context)


@login_required
@user_allowed_to_translate
def translate(request, project_id, language):
    current_project = get_object_or_404(Project, pk=project_id)
    current_language = get_object_or_404(Language, code=language)

    if current_language == current_project.source_language:
        editmode = True
    else:
        try:
            language_version = LanguageVersion.objects.get(project=current_project, language=current_language)
        except ObjectDoesNotExist:
            messages.error(request,
                           f"Ne ekzistas versio de ĉi tiu projekto en tiu lingvo ({current_language.name}).")
            return redirect('project', project_id)
        editmode = False

    available_languages = get_project_languages_for_user(current_project, request.user)

    # Data from query string
    current_directory = request.GET['dir'].strip('/') if 'dir' in request.GET.keys() else ''
    state_filter = request.GET['state'] if 'state' in request.GET.keys() else STATE_FILTER_ALL
    sort = request.GET['sort'] if 'sort' in request.GET.keys() else SORT_STRINGS_BY_OLDEST
    search_string = request.GET['q'] if 'q' in request.GET.keys() else ''

    all_strings = TrString.objects.filter(project=current_project)
    all_strings = filter_by_state(all_strings, language, state_filter)
    all_strings = filter_by_search(all_strings, language, search_string)
    strings = all_strings.filter(path=current_directory)
    if sort == SORT_STRINGS_BY_NEWEST:
        strings = strings.order_by('-last_change')
    elif sort == SORT_STRINGS_BY_NAME:
        strings = strings.order_by('name')
    else:
        strings = strings.order_by('last_change')
    for s in strings:
        print(s.last_change)

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
            messages.success(request, f"La lingvo {lang.name} estis aldonita.")
    update_project_admins(request.user, project)

    return redirect('project', project_id)
