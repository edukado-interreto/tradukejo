import os

from compressor.utils.staticfiles import finders
from django.contrib.staticfiles.storage import StaticFilesStorage
from django.contrib.staticfiles.utils import get_files
from django.core.exceptions import ObjectDoesNotExist
from django.middleware import csrf
from django.shortcuts import render, get_object_or_404, redirect, reverse
from django.templatetags.static import static

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
            new_texts = TrString.objects.filter(project=current_project,
                                                last_change__gte=current_project.last_translator_notification).count()
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
        'last_activities': get_last_activities(current_project)
    }

    if user_is_project_admin:
        context['translator_request_count'] = TranslatorRequest.objects.filter(
            language_version__project=current_project).count()

    return render(request, "traduko/project.html", context)


@login_required
def translate(request, project_id, language=""):
    current_project = get_object_or_404(Project, pk=project_id)
    available_languages = get_project_languages_for_user(current_project, request.user)

    js_files = []
    result = finders.find('traduko/vue-translation-interface/js')
    for root, dirs, files in os.walk(result):
        for filename in files:
            if filename.endswith('.js'):
                js_files.append({
                    'filename': filename,
                    'prefetch': not filename.startswith('app.') and not filename.startswith('chunk-vendors.'),
                })
    css_files = []
    result = finders.find('traduko/vue-translation-interface/css')
    if result:
        for root, dirs, files in os.walk(result):
            for filename in files:
                if filename.endswith('.css'):
                    css_files.append({
                        'filename': filename,
                        'prefetch': not filename.startswith('app.') and not filename.startswith('chunk-vendors.'),
                    })

    serialized_languages = []
    for l in available_languages:
        serialized_languages.append(l.to_dict())

    context = {
        'project': current_project,
        'available_languages': json.dumps(serialized_languages, ensure_ascii=False),
        'csrf': csrf.get_token(request),
        'imgURL': static('traduko/img'),
        'js_files': js_files,
        'css_files': css_files,
        'is_admin': 'true' if is_project_admin(request.user, current_project) else 'false',
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
