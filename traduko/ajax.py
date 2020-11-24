from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse, Http404
from django.shortcuts import render, get_object_or_404
from django.template.loader import render_to_string
from django.views.decorators.csrf import csrf_exempt
from .models import *
from datetime import datetime
from .translation_functions import *
from django.contrib.auth.decorators import login_required
import json


@csrf_exempt
@login_required
def save_translation(request, trstring_id, language):
    # TODO: if no change
    if request.method != "POST":
        return HttpResponse('')

    current_language = get_object_or_404(Language, code=language)
    current_string = get_object_or_404(TrString, pk=trstring_id)
    editmode = current_language == current_string.project.source_language

    if not is_allowed_to_translate(request.user, current_string, current_language):
        return HttpResponse('Vi ne rajtas traduki al tiu lingvo (' + current_language.name + ').')

    try:
        translated_text = TrStringText.objects.get(language=current_language, trstring=current_string)
    except ObjectDoesNotExist:
        translated_text = TrStringText(language=current_language, trstring=current_string)

    parsed_text_data = parse_submitted_text(request.POST.get('text'),
                                            TrStringText.objects.get(trstring=current_string, language=current_string.project.source_language).pluralized,
                                            current_language.nplurals())

    translated_text.state = TRANSLATION_STATE_TRANSLATED
    translated_text.translated_by = request.user
    translated_text.text = parsed_text_data['text']

    if editmode:  # Update word and character count
        translated_text.pluralized = bool(request.POST.get('pluralized') == 'true')
        current_string.context = request.POST.get('context')
        current_string.words = parsed_text_data['words']
        current_string.characters = parsed_text_data['characters']
        current_string.save()
        update_string_count(current_string.project)

        minor_change = bool(request.POST.get('minor') == 'true')  # Update translation status of translations
        if not minor_change:
            current_string.trstringtext_set.exclude(language=current_language).update(state=TRANSLATION_STATE_OUTDATED)
            translated_text.last_change = datetime.now()
    else:
        original_text = get_object_or_404(TrStringText, trstring=current_string,
                                          language=current_string.project.source_language)
        translated_text.pluralized = original_text.pluralized
        translated_text.last_change = datetime.now()

    translated_text.save()

    current_string.state = TRANSLATION_STATE_TRANSLATED
    current_string.translated_text = translated_text
    current_string.original_text = TrStringText.objects.get(language=current_string.project.source_language, trstring=current_string)

    context = {
        'editmode': editmode,
        'str': current_string,
        'language': current_language,
    }
    return render(request, "traduko/translation/translation-row.html", context)


@login_required
def get_string_translation(request, trstring_id, language):
    translated_text = get_object_or_404(TrStringText, language=language, trstring=trstring_id)
    str = TrString()
    str.original_text = translated_text
    context = {
        'str': str
    }
    return render(request, "traduko/translation/original-text.html", context)


def change_translation_state(request, trstringtext_id, state):
    trstringtext = get_object_or_404(TrStringText, pk=trstringtext_id)
    if trstringtext.language == trstringtext.trstring.project.source_language:
        raise Http404('Malĝusta ĉeno')

    if not is_allowed_to_translate(request.user, trstringtext.trstring.project, trstringtext.language):
        return HttpResponse('Vi ne rajtas traduki al tiu lingvo (' + trstringtext.language.name + ').')

    trstringtext.state = state
    trstringtext.save()

    current_string = trstringtext.trstring
    current_string.state = state
    current_string.translated_text = trstringtext
    current_string.original_text = TrStringText.objects.get(language=current_string.project.source_language,
                                                            trstring=current_string)

    context = {
        'editmode': False,
        'str': current_string,
        'language': trstringtext.language,
    }
    return render(request, "traduko/translation/translation-row.html", context)


@login_required
def markoutdated(request, trstringtext_id):
    return change_translation_state(request, trstringtext_id, TRANSLATION_STATE_OUTDATED)


@login_required
def marktranslated(request, trstringtext_id):
    return change_translation_state(request, trstringtext_id, TRANSLATION_STATE_TRANSLATED)


@login_required
def deletestring(request, trstring_id):
    trstring = get_object_or_404(TrString, pk=trstring_id)
    if is_project_admin(request.user, trstring.project):
        trstring.delete()
        update_string_count(trstring.project)
        return HttpResponse('La ĉeno estis forigita.')
    else:
        return HttpResponse('Vi ne rajtas forigi ĉenojn.')


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
        TranslatorRequest(user=request.user, explanation=request.POST.get('explanation'), language_version=lv).save()
        message = 'La peto estis sendita.'

    button = render_to_string("traduko/project/translation_request_sent_button.html")
    response_dict = {
        'message': message,
        'button': button
    }
    return HttpResponse(json.dumps(response_dict, ensure_ascii=False))
