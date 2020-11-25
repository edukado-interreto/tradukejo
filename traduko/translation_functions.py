import difflib

from django.db.models import Sum, Q
from .models import *
from collections import OrderedDict
import json


def is_project_admin(user, project):
    if user.is_superuser or user in project.admins.all():
        return True
    else:
        return False


def is_allowed_to_translate(user, project, language):
    if is_project_admin(user, project):
        return True

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


def update_string_count(project):
    trstrings = TrString.objects.filter(project=project).aggregate(Sum('words'), Sum('characters'))
    project.strings = project.trstring_set.count()
    project.words = trstrings['words__sum']
    project.characters = trstrings['characters__sum']
    project.save()


def add_stats_to_language_version(languageversion):
    for l in languageversion:
        translated = TrStringText.objects.filter(trstring__project=l.project, language=l.language, state=TRANSLATION_STATE_TRANSLATED)
        outdated = l.outdated_strings = TrStringText.objects.filter(trstring__project=l.project, language=l.language, state=TRANSLATION_STATE_OUTDATED)

        l.translated_strings = translated.count()
        l.outdated_strings = outdated.count()
        l.untranslated_strings = l.project.strings - l.translated_strings - l.outdated_strings

        translated_aggregated = translated.aggregate(Sum('trstring__words'), Sum('trstring__characters'))
        outdated_aggregated = outdated.aggregate(Sum('trstring__words'), Sum('trstring__characters'))

        l.translated_words = translated_aggregated['trstring__words__sum']
        if l.translated_words is None:
            l.translated_words = 0
        l.outdated_words = outdated_aggregated['trstring__words__sum']
        if l.outdated_words is None:
            l.outdated_words = 0
        l.untranslated_words = l.project.words - l.translated_words - l.outdated_words

        l.translated_characters = translated_aggregated['trstring__characters__sum']
        if l.translated_characters is None:
            l.translated_characters = 0
        l.outdated_characters = outdated_aggregated['trstring__characters__sum']
        if l.outdated_characters is None:
            l.outdated_characters = 0
        l.untranslated_characters = l.project.characters - l.translated_characters - l.outdated_characters

        l.translated_percent = l.translated_words / l.project.words * 100
        l.outdated_percent = l.outdated_words / l.project.words * 100
        l.untranslated_percent = l.untranslated_words / l.project.words * 100

    return languageversion


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

    current_user = add_stats_to_language_version(current_user)
    other_available = add_stats_to_language_version(other_available)

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
