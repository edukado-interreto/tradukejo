from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse, Http404
from django.shortcuts import render, get_object_or_404
from django.template.loader import render_to_string
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from .models import *
from .decorators import *
from .translation_functions import *
from django.contrib.auth.decorators import login_required
from django.utils import timezone
import json


@require_POST
@login_required
@user_allowed_to_translate
def save_translation(request, trstring_id, language):
    current_language = get_object_or_404(Language, code=language)
    current_string = get_object_or_404(TrString, pk=trstring_id)
    editmode = current_language == current_string.project.source_language
    if editmode:
        new_pluralized = bool(request.POST.get('pluralized') == 'true')
        new_context = request.POST.get('context')
        minor_change = bool(request.POST.get('minor') == 'true')
    else:
        new_pluralized = False
        new_context = ''
        minor_change = False

    saved_data = add_or_update_trstringtext(current_string.project,
                                            current_string.path,
                                            current_string.name,
                                            current_language,
                                            request.POST.get('text'),
                                            request.user,
                                            new_pluralized,
                                            True,
                                            new_context,
                                            minor_change)

    saved_data['trstring'].state = saved_data['trstringtext'].state
    saved_data['trstring'].translated_text = saved_data['trstringtext']
    saved_data['trstring'].original_text = TrStringText.objects.get(language=current_string.project.source_language,
                                                            trstring=current_string)

    context = {
        'editmode': editmode,
        'str': saved_data['trstring'],
        'language': current_language,
    }
    return render(request, "traduko/translation/translation-row.html", context)


@require_POST
@login_required
@user_allowed_to_translate
def save_translation_old(request, trstring_id, language):
    current_language = get_object_or_404(Language, code=language)
    current_string = get_object_or_404(TrString, pk=trstring_id)
    editmode = current_language == current_string.project.source_language
    if editmode:
        new_pluralized = bool(request.POST.get('pluralized') == 'true')
        new_context = request.POST.get('context')

    try:
        translated_text = TrStringText.objects.get(language=current_language, trstring=current_string)
        new_translation = False
    except ObjectDoesNotExist:
        translated_text = TrStringText(language=current_language, trstring=current_string)
        new_translation = True

    parsed_text_data = parse_submitted_text(request.POST.get('text'),
                                            TrStringText.objects.get(trstring=current_string, language=current_string.project.source_language).pluralized,
                                            current_language.nplurals())

    if new_translation or parsed_text_data['text'] != translated_text.text or (editmode and (translated_text.pluralized != new_pluralized or current_string.context != new_context)):  # If there are changes
        # If not new string and text has changed: save in history
        if not new_translation and parsed_text_data['text'] != translated_text.text:
            # Save as pluralized only if string has several forms
            old_version_pluralized = translated_text.number_of_pluralized_texts() == translated_text.language.nplurals() and translated_text.language.nplurals() > 1
            history = TrStringTextHistory(trstringtext=translated_text,
                                          pluralized=old_version_pluralized,
                                          text=translated_text.text,
                                          translated_by=translated_text.translated_by)
            history.save()

        # Update the translation
        translated_text.state = TRANSLATION_STATE_TRANSLATED
        translated_text.translated_by = request.user
        translated_text.text = parsed_text_data['text']

        if editmode:  # Update word and character count
            update_project_admins(request.user, current_string.project)
            translated_text.pluralized = new_pluralized
            current_string.context = new_context
            current_string.words = parsed_text_data['words']
            current_string.characters = parsed_text_data['characters']
            current_string.save()

            minor_change = bool(request.POST.get('minor') == 'true')  # Update translation status of translations
            if not minor_change:
                current_string.trstringtext_set.exclude(language=current_language).update(state=TRANSLATION_STATE_OUTDATED)
                translated_text.last_change = timezone.now()
        else:
            original_text = get_object_or_404(TrStringText, trstring=current_string,
                                              language=current_string.project.source_language)
            translated_text.pluralized = original_text.pluralized
            translated_text.last_change = timezone.now()

        translated_text.save()

    update_translators_when_translating(request.user, current_string.project, current_language)

    # Adding parameters for template
    current_string.state = translated_text.state
    current_string.translated_text = translated_text
    current_string.original_text = TrStringText.objects.get(language=current_string.project.source_language, trstring=current_string)

    context = {
        'editmode': editmode,
        'str': current_string,
        'language': current_language,
    }
    return render(request, "traduko/translation/translation-row.html", context)


@require_POST
@csrf_exempt
@login_required
def get_string_translation(request, trstring_id, language):
    translated_text = get_object_or_404(TrStringText, language=language, trstring=trstring_id)
    language_to = get_object_or_404(Language, code=request.POST.get('language_to'))
    str = TrString()
    str.original_text = translated_text

    original_string = render_to_string("traduko/translation/original-string.html", {'str': str}, request)
    translator_links = render_to_string("traduko/translation/online_translators_links.html", {'text': translated_text, 'language_to': language_to}, request)

    response_dict = {
        'text': original_string,
        'translator_links': translator_links,
    }
    return HttpResponse(json.dumps(response_dict, ensure_ascii=False))


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
    return render(request, "traduko/translation/translation-row.html", context)


@require_POST
@login_required
@user_allowed_to_translate
def markoutdated(request, trstringtext_id):
    return change_translation_state(request, trstringtext_id, TRANSLATION_STATE_OUTDATED)


@require_POST
@login_required
@user_allowed_to_translate
def marktranslated(request, trstringtext_id):
    return change_translation_state(request, trstringtext_id, TRANSLATION_STATE_TRANSLATED)


@require_POST
@login_required
@user_is_project_admin
def deletestring(request, trstring_id):
    trstring = get_object_or_404(TrString, pk=trstring_id)
    update_project_admins(request.user, trstring.project)
    trstring.delete()
    return HttpResponse('La ĉeno estis forigita.')


@login_required
def request_translator_permission(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    language = get_object_or_404(Language, pk=request.POST.get('language'))

    try:
        lv = LanguageVersion.objects.get(project=project, language=language)
    except LanguageVersion.DoesNotExist:
        lv = LanguageVersion(project=project, language=language)
        lv.save()

    if request.user in lv.translators.all():
        message = 'Vi jam havas la rajton traduki al ĉi tiu lingvo.'
    elif TranslatorRequest.objects.filter(user=request.user, language_version=lv).count() > 0:
        message = 'Vi jam sendis peton por ĉi tiu lingvo.'
    else:
        translator_request = TranslatorRequest(user=request.user, explanation=request.POST.get('explanation'), language_version=lv)
        translator_request.save()
        print(translator_request)
        message = 'La peto estis sendita.'
        send_email_to_admins_about_translation_request(request, translator_request)

    button = render_to_string("traduko/project/translation_request_sent_button.html")
    response_dict = {
        'message': message,
        'button': button
    }
    return HttpResponse(json.dumps(response_dict, ensure_ascii=False))


@login_required
def get_history(request, trstringtext_id):
    trstringtext = get_object_or_404(TrStringText, pk=trstringtext_id)

    old_versions = TrStringTextHistory.objects.filter(trstringtext=trstringtext).order_by('-create_date')

    history = list(old_versions)
    history.insert(0, TrStringTextHistory(text=trstringtext.text,  # Add the current version to the beginning in order to show comparisons
                                          translated_by=trstringtext.translated_by,
                                          create_date=trstringtext.last_change,
                                          pluralized=trstringtext.pluralized,
                                          trstringtext=trstringtext))
    history[0].current = True

    history = get_history_comparison(history)

    context = {
        'versions': history
    }
    return render(request, "traduko/translation/stringtext-history.html", context)


@require_POST
@csrf_exempt
@login_required
@user_allowed_to_translate
def load_more(request, project_id, language):
    current_project = get_object_or_404(Project, pk=project_id)
    current_language = get_object_or_404(Language, pk=language)
    editmode = current_language == current_project.source_language

    start = int(request.POST['start']) if 'start' in request.POST.keys() else 0
    current_directory = request.GET['dir'].strip('/') if 'dir' in request.GET.keys() else ''
    state_filter = request.GET['state'] if 'state' in request.GET.keys() else STATE_FILTER_ALL
    sort = request.GET['sort'] if 'sort' in request.GET.keys() else SORT_STRINGS_BY_OLDEST
    search_string = request.GET['q'] if 'q' in request.GET.keys() else ''

    all_strings = get_all_strings(current_project, current_language, state_filter, search_string)
    strings, can_load_more = get_strings_to_translate(all_strings, current_language, current_directory, sort, start)

    html = ''
    for s in strings:
        context = {
            'editmode': editmode,
            'str': s,
            'language': current_language,
        }
        html = html + render_to_string("traduko/translation/translation-row.html", context, request)
    response_dict = {
        'html': html,
        'can_load_more': 1 if can_load_more else 0,
    }
    return HttpResponse(json.dumps(response_dict, ensure_ascii=False))
