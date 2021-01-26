from django.contrib.auth.decorators import login_required
from django.core import serializers
from django.http import JsonResponse, Http404
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from traduko.decorators import user_allowed_to_translate
from traduko.models import *
from traduko.translation_functions import *


@login_required
@user_allowed_to_translate
@require_POST
def get_strings(request):
    postdata = json.loads(request.body.decode('utf-8'))

    current_project = get_object_or_404(Project, pk=postdata['project_id'])
    current_language = get_object_or_404(Language, code=postdata['language'])

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
    response = JsonResponse(context)
    return response


@require_POST
@login_required
def get_string_translation(request):
    postdata = json.loads(request.body.decode('utf-8'))
    translated_text = get_object_or_404(TrStringText, language=postdata['language'], trstring=postdata['trstring_id'])
    return JsonResponse(translated_text.to_dict())


def change_translation_state(request, trstringtext_id, state):
    trstringtext = get_object_or_404(TrStringText, pk=trstringtext_id)
    if trstringtext.language == trstringtext.trstring.project.source_language:
        raise Http404('Malĝusta ĉeno')

    trstringtext.state = state
    trstringtext.save()

    current_string = trstringtext.trstring
    current_string.state = state
    current_string.translated_text = trstringtext
    current_string.original_text = TrStringText.objects.get(language=current_string.project.source_language,
                                                            trstring=current_string)

    # Add activity to last activities
    activity = StringActivity(trstringtext=trstringtext,
                              language=trstringtext.language,
                              user=request.user,
                              action=ACTION_TYPE_EDIT
                              )
    activity.save()

    update_translators_when_translating(request.user, current_string.project, trstringtext.language)

    context = {
        'editmode': False,
        'str': current_string,
        'language': trstringtext.language,
    }
    return JsonResponse({'state': state})


@require_POST
@login_required
@user_allowed_to_translate
def markoutdated(request):
    postdata = json.loads(request.body.decode('utf-8'))
    return change_translation_state(request, postdata['trstringtext_id'], TRANSLATION_STATE_OUTDATED)


@require_POST
@login_required
@user_allowed_to_translate
def marktranslated(request):
    postdata = json.loads(request.body.decode('utf-8'))
    return change_translation_state(request, postdata['trstringtext_id'], TRANSLATION_STATE_TRANSLATED)
