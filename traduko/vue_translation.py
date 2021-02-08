from django.contrib.auth.decorators import login_required
from django.core import serializers
from django.db import IntegrityError
from django.http import JsonResponse, Http404, HttpResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from traduko.decorators import user_allowed_to_translate, user_is_project_admin, user_has_any_right_for_project
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
    chosen_string_id = postdata['chosen_string'] if 'chosen_string' in postdata.keys() else None
    previous_ids = postdata['previous_ids'] if 'previous_ids' in postdata.keys() else []

    all_strings = get_all_strings(current_project, current_language, state_filter, search_string)
    strings, can_load_more = get_strings_to_translate(all_strings,
                                                      current_language,
                                                      current_directory,
                                                      sort,
                                                      previous_ids=previous_ids,
                                                      chosen_string_id=chosen_string_id)
    strings_data = []
    for s in strings:
        strings_data.append(s.to_dict(s.original_text, s.translated_text))

    context = {
        'strings': strings_data,
        'can_load_more': can_load_more,
    }
    response = JsonResponse(context)
    return response


@login_required
@user_allowed_to_translate
@require_POST
def get_directories(request):
    postdata = json.loads(request.body.decode('utf-8'))

    current_project = get_object_or_404(Project, pk=postdata['project_id'])
    current_language = get_object_or_404(Language, code=postdata['language'])

    # Search and filter data
    current_directory = postdata['dir'].strip('/') if 'dir' in postdata.keys() else ''
    state_filter = postdata['state'] if 'state' in postdata.keys() else STATE_FILTER_ALL
    search_string = postdata['q'] if 'q' in postdata.keys() else ''

    all_strings = get_all_strings(current_project, current_language, state_filter, search_string)
    subdirectories = get_subdirectories(all_strings, current_directory)

    context = {
        'directories': subdirectories,
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


@require_POST
@login_required
@user_is_project_admin
def delete_string(request):
    postdata = json.loads(request.body.decode('utf-8'))
    trstring = get_object_or_404(TrString, pk=postdata['trstring_id'])
    update_project_admins(request.user, trstring.project)
    trstring.delete()
    return JsonResponse({'deleted': True})


@require_POST
@login_required
@user_allowed_to_translate
def save_translation(request):
    postdata = json.loads(request.body.decode('utf-8'))

    current_language = get_object_or_404(Language, code=postdata['language'])
    current_string = get_object_or_404(TrString, pk=postdata['trstring_id'])
    editmode = current_language == current_string.project.source_language
    if editmode:
        new_pluralized = bool(postdata['pluralized'])
        new_context = postdata['context']
        minor_change = bool(postdata['minor'])

        new_name = postdata['name'].strip()
        new_path = postdata['path'].strip(' /')
        if new_name != current_string.name or new_path != current_string.path:
            current_string.name = new_name
            current_string.path = new_path
            try:
                current_string.save()
            except IntegrityError:
                response = HttpResponse('Jam ekzistas ĉeno kun ĉi tiu nomo.')
                response.status_code = 409
                return response

    else:
        new_pluralized = False
        new_context = ''
        minor_change = False

    saved_data = add_or_update_trstringtext(current_string.project,
                                            current_string.path,
                                            current_string.name,
                                            current_language,
                                            json.dumps(postdata['text']),
                                            request.user,
                                            new_pluralized,
                                            True,
                                            new_context,
                                            minor_change)

    if editmode:
        original_text = saved_data['trstringtext']
    else:
        original_text = TrStringText.objects.get(language=current_string.project.source_language,
                                                 trstring=current_string)

    saved_string = current_string.to_dict(original_text, saved_data['trstringtext'])

    return JsonResponse(saved_string)


@require_POST
@login_required
@user_is_project_admin
def add_string(request):
    postdata = json.loads(request.body.decode('utf-8'))

    project = get_object_or_404(Project, pk=postdata['project_id'])

    name = postdata['name'].strip()
    pluralized = bool(postdata['pluralized'])
    path = postdata['path'].strip(' /')
    context = postdata['context'].strip()

    try:
        saved_data = add_or_update_trstringtext(project,
                                                path,
                                                name,
                                                project.source_language,
                                                json.dumps(postdata['text']),
                                                request.user,
                                                pluralized,
                                                True,
                                                context,
                                                False,
                                                True)
    except IntegrityError:
        response = HttpResponse('Jam ekzistas ĉeno kun ĉi tiu nomo.')
        response.status_code = 409  # 409 Conflict
        return response

    update_project_admins(request.user, project)

    saved_string = saved_data['trstring'].to_dict(saved_data['trstringtext'], saved_data['trstringtext'])

    return JsonResponse(saved_string)


@require_POST
@login_required
@user_has_any_right_for_project
def get_history(request):
    postdata = json.loads(request.body.decode('utf-8'))

    trstringtext = get_object_or_404(TrStringText, pk=postdata['trstringtext_id'])

    old_versions = TrStringTextHistory.objects.filter(trstringtext=trstringtext).order_by('-create_date')

    history = list(old_versions)
    history.insert(0, TrStringTextHistory(text=trstringtext.text,  # Add the current version to the beginning in order to show comparisons
                                          translated_by=trstringtext.translated_by,
                                          create_date=trstringtext.last_change,
                                          pluralized=trstringtext.pluralized,
                                          trstringtext=trstringtext))
    history[0].current = True

    history = get_history_comparison(history)

    data = []
    for h in history:
        data.append(h.to_dict(h.comparison))

    return JsonResponse(data, safe=False)


@require_POST
@login_required
@user_has_any_right_for_project
def get_comments(request):
    postdata = json.loads(request.body.decode('utf-8'))

    trstringtext = get_object_or_404(TrStringText, pk=postdata['trstringtext_id'])

    comments = Comment.objects.filter(trstringtext=trstringtext).order_by('create_date')

    data = []
    for c in comments:
        data.append(c.to_dict())

    return JsonResponse(data, safe=False)


@require_POST
@login_required
@user_has_any_right_for_project
def save_comment(request):
    postdata = json.loads(request.body.decode('utf-8'))

    trstringtext = get_object_or_404(TrStringText, pk=postdata['trstringtext_id'])

    text = postdata['text'].strip()

    comment = Comment(trstringtext=trstringtext, author=request.user, text=text)
    comment.save()

    return JsonResponse(comment.to_dict(), safe=False)


@require_POST
@login_required
@user_has_any_right_for_project
def delete_comment(request):
    postdata = json.loads(request.body.decode('utf-8'))

    comment = get_object_or_404(Comment, pk=postdata['comment_id'])
    if is_project_admin(request.user, comment.trstringtext.trstring.project) or request.user == comment.author:
        comment.delete()
    else:
        response = HttpResponse('Vi ne rajtas forigi ĉi tiun komenton.')
        response.status_code = 403

    return JsonResponse({'ok': True}, safe=False)
