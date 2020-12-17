import difflib

from django.core.mail import send_mail
from django.db.models import Sum, Q
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.html import strip_tags

from .models import *
from collections import OrderedDict
import json, html


def is_project_admin(user, project):
    if user.is_superuser or user in project.admins.all():
        return True
    else:
        return False


def is_allowed_to_translate(user, project, language):
    if is_project_admin(user, project):
        return True

    if project.locked or not project.visible:
        return False

    try:
        lv = LanguageVersion.objects.get(project=project, language=language)
    except LanguageVersion.DoesNotExist:
        lv = None

    if lv is not None and user in lv.translators.all():
        return True

    return False


def get_subdirectories(trstrings, current_directory):
    string_subdirectories = trstrings.filter(path__startswith=current_directory)
    # TODO: improve this (distinct not supported by SQLite)
    subdirectories = {}
    for s in string_subdirectories:
        subdirectory = s.path[len(current_directory):].strip('/')
        if subdirectory.find('/') >= 0:
            subdirectory = subdirectory[0:subdirectory.find('/')]
        if subdirectory != '' and subdirectory not in subdirectories.keys():
            path = current_directory + ('/' if current_directory != '' else '') + subdirectory
            wordcharcount = string_subdirectories.filter(path__startswith=path).aggregate(Sum('words'), Sum('characters'))
            subdirectories[subdirectory] = {
                'path': path,
                'strings': string_subdirectories.filter(path__startswith=path).count(),
                'words': wordcharcount['words__sum'],
                'characters': wordcharcount['characters__sum'],
            }
    return OrderedDict(sorted(subdirectories.items()))


def update_project_count(project):
    trstrings = TrString.objects.filter(project=project).aggregate(Sum('words'), Sum('characters'))
    project.strings = project.trstring_set.count()
    project.words = trstrings['words__sum']
    project.characters = trstrings['characters__sum']
    project.save()


def update_all_language_versions_count(project):
    languageversions = project.languageversion_set.all()
    for lv in languageversions:
        update_language_version_count(lv)


def update_language_version_count(l):  # l: languageversion
    translated = TrStringText.objects.filter(trstring__project=l.project, language=l.language,
                                             state=TRANSLATION_STATE_TRANSLATED)
    outdated = l.outdated_strings = TrStringText.objects.filter(trstring__project=l.project, language=l.language,
                                                                state=TRANSLATION_STATE_OUTDATED)

    l.translated_strings = translated.count()
    l.outdated_strings = outdated.count()

    translated_aggregated = translated.aggregate(Sum('trstring__words'), Sum('trstring__characters'))
    outdated_aggregated = outdated.aggregate(Sum('trstring__words'), Sum('trstring__characters'))

    l.translated_words = translated_aggregated['trstring__words__sum']
    if l.translated_words is None:
        l.translated_words = 0
    l.outdated_words = outdated_aggregated['trstring__words__sum']
    if l.outdated_words is None:
        l.outdated_words = 0

    l.translated_characters = translated_aggregated['trstring__characters__sum']
    if l.translated_characters is None:
        l.translated_characters = 0
    l.outdated_characters = outdated_aggregated['trstring__characters__sum']
    if l.outdated_characters is None:
        l.outdated_characters = 0

    l.save()


def get_project_languages_for_user(project, user):
    if is_project_admin(user, project):
        available_languages = (Language.objects.filter(code=project.source_language.code) |
                              Language.objects.filter(languageversion__project=project))
    else:
        available_languages = Language.objects.filter(languageversion__project=project, languageversion__translators=user)

    return available_languages.order_by('code')


def get_project_language_statistics(project, user):
    if is_project_admin(user, project):
        current_user = project.languageversion_set.all()
        other_available = LanguageVersion.objects.none()
    else:
        current_user = project.languageversion_set.filter(translators=user)
        other_available = project.languageversion_set.exclude(translators=user)

    for lv in other_available:
        lv.translation_request_sent = lv.translatorrequest_set.filter(user=user).count() > 0

    return {
        'current_user': current_user,
        'other_available': other_available,
    }


# Returns languages that don't have a language version in a given project but could be added
def addible_languages(project):
    if project.needed_languages.count() > 0:
        languages = project.needed_languages.all()
    else:
        languages = Language.objects.all()
    languages = languages.exclude(code=project.source_language.code).exclude(languageversion__project=project)
    return languages.order_by('code')


def filter_by_state(trstrings, current_language, state):
    if state == STATE_FILTER_UNTRANSLATED:
        return trstrings.exclude(trstringtext__language=current_language)
    elif state == STATE_FILTER_OUTDATED:
        return trstrings.filter(trstringtext__language=current_language, trstringtext__state=TRANSLATION_STATE_OUTDATED)
    elif state == STATE_FILTER_OUTDATED_UNTRANSLATED:
        untranslated = trstrings.exclude(trstringtext__language=current_language)
        outdated = trstrings.filter(trstringtext__language=current_language, trstringtext__state=TRANSLATION_STATE_OUTDATED)
        return (untranslated | outdated).distinct()  # Otherwise some strings appear several times, I don't know why
    else:
        return trstrings


def filter_by_search(trstrings, current_language, search_string):
    search_string = search_string.strip()
    if search_string == '' or trstrings.count() == 0:
        return trstrings
    else:
        in_source_language = trstrings.filter(trstringtext__language=trstrings[0].project.source_language, trstringtext__text__icontains=search_string)
        if trstrings[0].project.source_language == current_language:
            return in_source_language
        else:
            in_current_language = trstrings.filter(trstringtext__language=current_language, trstringtext__text__icontains=search_string)
            return (in_current_language | in_source_language).distinct()  # Otherwise some strings appear several times, I don't know why


# submitted_text has to be a JSON string like [{"name":"text[0]","value":"content here"},{"name":"text[1]","value":"content2 here"}]
# There should be several values for translations of pluralized strings, and one otherwise
def parse_submitted_text(submitted_text, is_pluralized, nplurals):
    try:
        json_data = json.loads(submitted_text)
    except ValueError as e:
        json_data = [{'name': 'text[0]', 'value': submitted_text},]

    submitted_strings = {}
    for s in json_data:
        submitted_strings[s['name']] = s['value']

    if is_pluralized:
        words = 0
        characters = 0
        strings = []
        i = 0
        while i < nplurals and 'text['+str(i)+']' in submitted_strings.keys():
            t = submitted_strings['text['+str(i)+']'].strip()
            words = words + len(t.split())
            characters = characters + len(t)
            strings.append(t)
            i = i + 1
        text = json.dumps(strings, ensure_ascii=False)
    else:
        text = submitted_strings['text[0]'] if 'text[0]' in submitted_strings.keys() else submitted_text
        text = text.strip()
        words = len(text.split())
        characters = len(text)
    return {
        'text': text,
        'words': words,
        'characters': characters,
    }


def get_text_difference(text, n_text):
    """
    http://stackoverflow.com/a/788780
    Unify operations between two compared strings seqm is a difflib.
    SequenceMatcher instance whose a & b are strings
    """
    seqm = difflib.SequenceMatcher(None, text, n_text)
    output= []
    for opcode, a0, a1, b0, b1 in seqm.get_opcodes():
        if opcode == 'equal':
            output.append(seqm.a[a0:a1])
        elif opcode == 'insert':
            output.append("<ins>" + seqm.b[b0:b1] + "</ins>")
        elif opcode == 'delete':
            output.append("<del>" + seqm.a[a0:a1] + "</del>")
        elif opcode == 'replace':
            # seqm.a[a0:a1] -> seqm.b[b0:b1]
            output.append("<del>" + seqm.a[a0:a1] + "</del>")
            output.append("<ins>" + seqm.b[b0:b1] + "</ins>")
        else:
            raise RuntimeError
    return ''.join(output)


def get_history_comparison(history):
    """
    Generates visual comparison of changes in the history of versions of a translated text.
    It adds to history object an ordered dictionary. A simple string has only one element in this dictionary,
    but it may be more if we are dealing with a pluralized string.
    """
    for i in range(len(history) - 1):
        new = history[i]
        new_texts = new.pluralized_text_dictionary()
        old = history[i+1]
        old_texts = old.pluralized_text_dictionary()

        new.comparison = OrderedDict()

        if len(new_texts) == 1 and len(old_texts) == 1:  # Non-pluralized string
            new.comparison['1'] = get_text_difference(html.escape(old_texts['1']), html.escape(new_texts['1']))
        elif len(new_texts) == len(old_texts):  # Pluralized string
            for j in range(len(new_texts)):
                keys = list(new_texts.keys())
                new_values = list(new_texts.values())
                old_values = list(old_texts.values())
                new.comparison[keys[j]] = get_text_difference(html.escape(old_values[j]), html.escape(new_values[j]))
        elif len(old_texts) == 1:  # Old string is not pluralized, new one is
            old_values = list(old_texts.values())
            old_text = old_values[0]
            for number, text in new_texts.items():
                new.comparison[number] = get_text_difference(html.escape(old_text), html.escape(text))
        elif len(new_texts) == 1:  # Old string is pluralized, new one is not
            new_values = list(new_texts.values())
            new_text = new_values[0]
            new.comparison['1'] = get_text_difference(html.escape(old_texts['1']), html.escape(new_text))
        else:  # Pluralized but with different amounts of plural forms, no comparison shown because something is wrong
            new.comparison = new_texts
            for number, text in new_texts.items():
                new.comparison[number] = html.escape(text)

    # Last version: nothing to compare, just put the text
    history[-1].comparison = history[-1].pluralized_text_dictionary()

    return history


def send_email_to_admins_about_translation_request(request, translator_request):
    project = translator_request.language_version.project
    language = translator_request.language_version.language
    administrators = project.admins.all()
    for admin in administrators:
        if admin.email_translation_request:
            mail_context = {
                'admin': admin,
                'project': project,
                'language': language,
                'translator_request': translator_request,
                'url': request.build_absolute_uri(reverse('translator_request_list', args=(project.pk, ))),
            }
            html_message = render_to_string("traduko/email/new-translator-request.html", mail_context)
            plain_text_message = strip_tags(html_message)

            send_mail(
                'Tradukejo de E@I: peto de tradukrajto por ' + project.name,
                plain_text_message,
                None,
                [admin.email],
                html_message=html_message
            )
