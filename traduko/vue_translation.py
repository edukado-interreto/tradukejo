from django.contrib.auth.decorators import login_required
from django.core import serializers
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from traduko.decorators import user_allowed_to_translate
from traduko.models import *
from traduko.translation_functions import *


@csrf_exempt
@login_required
@user_allowed_to_translate
@require_POST
def vue_get_strings(request, project_id, language):
    postdata = json.loads(request.body.decode('utf-8'))

    current_project = get_object_or_404(Project, pk=project_id)
    current_language = get_object_or_404(Language, code=language)

    if current_language == current_project.source_language:
        editmode = True
    else:
        language_version = LanguageVersion.objects.get(project=current_project, language=current_language)
        editmode = False

    available_languages = get_project_languages_for_user(current_project, request.user)

    # Search and filter data
    current_directory = postdata['dir'].strip('/') if 'dir' in postdata.keys() else ''
    state_filter = postdata['state'] if 'state' in postdata.keys() else STATE_FILTER_ALL
    sort = postdata['sort'] if 'sort' in postdata.keys() else SORT_STRINGS_BY_NAME
    search_string = postdata['q'] if 'q' in postdata.keys() else ''

    all_strings = get_all_strings(current_project, current_language, state_filter, search_string)
    strings, can_load_more = get_strings_to_translate(all_strings, current_language, current_directory, sort)

    strings_data = []
    for s in strings:
        strings_data.append(s.to_dict(s.original_text, s.translated_text))

    context = {
        'strings': strings_data,
    }
    print(context)
    response = JsonResponse(context)
    return response
