import io
from zipfile import ZipFile, ZIP_DEFLATED

from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse, JsonResponse
from django.http import FileResponse
from django.shortcuts import render, get_object_or_404, redirect, reverse
from django.utils import timezone
from django.utils.text import slugify
from django.utils.translation import gettext as _
from django.views.decorators.http import require_POST
from .models import *
from .translation_functions import *
from .forms import *
from .import_functions import *
from .export_functions import *
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .decorators import *
from django.db.models import Q


@login_required
@user_is_project_admin
def translator_request_list(request, project_id):
    project = get_object_or_404(Project, pk=project_id)

    requests = TranslatorRequest.objects.filter(
        language_version__project=project
    ).order_by("-create_date")

    context = {"project": project, "requests": requests}
    return render(request, "traduko/project-translator-requests.html", context)


@login_required
@user_is_project_admin
def accept_translator_request(request, request_id):
    translatorrequest = get_object_or_404(TranslatorRequest, pk=request_id)
    translatorrequest.language_version.translators.add(translatorrequest.user)
    translatorrequest.language_version.save()
    translatorrequest.delete()

    current_language = get_language()
    activate(translatorrequest.user.email_language)

    # Email confirmation to the user
    mail_context = {
        "translator": translatorrequest.user,
        "project": translatorrequest.language_version.project,
        "language": translatorrequest.language_version.language,
        "url": request.build_absolute_uri(
            reverse("project", args=(translatorrequest.language_version.project.pk,))
        ),
    }

    html_message = render_to_string(
        "traduko/email/translator-request-accepted.html", mail_context
    )
    plain_text_message = strip_tags(html_message)

    send_mail(
        _("emails/request#accepted-title").format(
            project=translatorrequest.language_version.project.name
        ),
        plain_text_message,
        None,
        [translatorrequest.user.email],
        html_message=html_message,
    )

    activate(current_language)
    update_project_admins(request.user, translatorrequest.language_version.project)
    return redirect(
        "translator_request_list", translatorrequest.language_version.project.pk
    )


@login_required
@user_is_project_admin
def decline_translator_request(request, request_id):
    translatorrequest = get_object_or_404(TranslatorRequest, pk=request_id)

    # Delete the language version if no translations
    if (
        TrStringText.objects.filter(
            trstring__project=translatorrequest.language_version.project,
            language=translatorrequest.language_version.language,
        ).count()
        == 0
    ):
        translatorrequest.language_version.delete()  # translatorrequest deleted by cascade
    else:
        translatorrequest.delete()

    current_language = get_language()
    activate(translatorrequest.user.email_language)

    # Email confirmation to the user
    mail_context = {
        "translator": translatorrequest.user,
        "project": translatorrequest.language_version.project,
        "language": translatorrequest.language_version.language,
    }

    html_message = render_to_string(
        "traduko/email/translator-request-rejected.html", mail_context
    )
    plain_text_message = strip_tags(html_message)

    send_mail(
        _("emails/request#rejected-title").format(
            project=translatorrequest.language_version.project.name
        ),
        plain_text_message,
        None,
        [translatorrequest.user.email],
        html_message=html_message,
    )
    update_project_admins(request.user, translatorrequest.language_version.project)
    activate(current_language)

    return redirect(
        "translator_request_list", translatorrequest.language_version.project.pk
    )


@login_required
@user_is_project_admin
def edit_project(request, project_id):
    project = get_object_or_404(Project, pk=project_id)

    if request.method == "POST":
        form = ProjectForm(request.POST, request.FILES, instance=project)
        if form.is_valid():
            form.save()
            messages.success(request, _("messages#changes-saved"))
        else:
            messages.error(request, _("messages#changes-cannot-be-saved"))
        update_project_admins(request.user, project)
    else:
        form = ProjectForm(instance=project)

    context = {"project": project, "form": form}
    return render(request, "traduko/project-edit.html", context)


@login_required
@user_is_project_admin
def translator_notifications(request, project_id):
    project = get_object_or_404(Project, pk=project_id)

    if request.method == "POST":
        current_language = get_language()
        languages = request.POST.getlist("send[]")
        language_versions = LanguageVersion.objects.filter(
            project=project, language__in=languages
        ).exclude(translated_strings=project.strings)
        if len(language_versions) > 0:
            translators = (
                get_user_model()
                .objects.filter(
                    email_new_texts=True, languageversion__in=language_versions
                )
                .distinct()
                .exclude(pk=request.user.pk)
            )
            for translator in translators:
                activate(translator.email_language)
                lv = LanguageVersion.objects.filter(
                    project=project, translators=translator
                ).exclude(translated_strings=project.strings)
                # Email translator about new strings
                mail_context = {
                    "translator": translator,
                    "project": project,
                    "language_versions": lv,
                    "translate_url": request.build_absolute_uri(
                        reverse("project", args=(project.pk,))
                    ),
                    "settings_url": request.build_absolute_uri(
                        reverse("user_settings")
                    ),
                }
                html_message = render_to_string(
                    "traduko/email/new-texts-to-translate.html", mail_context
                )
                plain_text_message = strip_tags(html_message)

                send_mail(
                    _("emails/new-texts#title").format(project=project.name),
                    plain_text_message,
                    None,
                    [translator.email],
                    html_message=html_message,
                )

            project.last_translator_notification = timezone.now()
            project.save()
            messages.success(request, _("messages#notification-sent"))
        activate(current_language)

    context = {
        "project": project,
    }
    return render(request, "traduko/translator-notifications.html", context)


@login_required
@user_is_project_admin
def import_export(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    context = {
        "project": project,
    }
    return render(request, "traduko/import-export/import-export.html", context)


@login_required
@user_is_project_admin
def import_csv(request, project_id):
    project = get_object_or_404(Project, pk=project_id)

    if request.method == "POST":
        form = ImportForm(request.POST, request.FILES)
        if form.is_valid():
            csv_file = form.cleaned_data["file"]
            if not csv_file.name.endswith(".csv"):
                messages.error(request, "Malĝusta formato de dosiero.")
            else:
                try:
                    import_stats = import_from_csv(
                        project,
                        csv_file,
                        form.cleaned_data["update_texts"],
                        form.cleaned_data["user_is_author"],
                        request.user,
                        import_to=form.cleaned_data["import_to"],
                    )
                    messages.success(
                        request,
                        f"{import_stats['imported_strings']} ĉenoj kaj {import_stats['imported_translations']} tradukoj estis importitaj.",
                    )
                except WrongFormatError:
                    messages.error(request, "Malĝusta formato de dosiero.")
        else:
            messages.error(request, _("messages#changes-cannot-be-saved"))
        update_project_admins(request.user, project)
    else:
        form = ImportForm()

    context = {
        "project": project,
        "form": form,
    }
    return render(request, "traduko/import-export/import-csv.html", context)


@login_required
@user_is_project_admin
def import_json(request, project_id):
    project = get_object_or_404(Project, pk=project_id)

    if request.method == "POST":
        form = ImportForm(request.POST, request.FILES)
        if form.is_valid():
            json_file = form.cleaned_data["file"]
            if not json_file.name.endswith(".json"):
                messages.error(request, "Malĝusta formato de dosiero.")
            else:
                try:
                    import_stats = import_from_json(
                        project,
                        json_file,
                        form.cleaned_data["update_texts"],
                        form.cleaned_data["user_is_author"],
                        request.user,
                        import_to=form.cleaned_data["import_to"],
                    )
                    messages.success(
                        request,
                        f"{import_stats['imported_strings']} ĉenoj kaj {import_stats['imported_translations']} tradukoj estis importitaj.",
                    )
                except WrongFormatError:
                    messages.error(request, "Malĝusta formato de dosiero.")
        else:
            messages.error(request, _("messages#changes-cannot-be-saved"))
        update_project_admins(request.user, project)
    else:
        form = ImportForm()

    context = {
        "project": project,
        "form": form,
    }
    return render(request, "traduko/import-export/import-json.html", context)


@login_required
@user_is_project_admin
def import_po(request, project_id):
    project = get_object_or_404(Project, pk=project_id)

    if request.method == "POST":
        form = POImportForm(request.POST, request.FILES)
        if form.is_valid():
            po_file = form.cleaned_data["file"]
            if not po_file.name.endswith(".po") and not po_file.name.endswith(".pot"):
                messages.error(request, "Malĝusta formato de dosiero.")
            else:
                try:
                    import_stats = import_from_po(
                        project,
                        po_file,
                        form.cleaned_data["update_texts"],
                        form.cleaned_data["user_is_author"],
                        request.user,
                        import_to=form.cleaned_data["import_to"],
                        original_text_as_key=form.cleaned_data["original_text_as_key"],
                    )
                    messages.success(
                        request,
                        f"{import_stats['imported_strings']} ĉenoj kaj {import_stats['imported_translations']} tradukoj estis importitaj.",
                    )
                except WrongFormatError:
                    messages.error(request, "Malĝusta formato de dosiero.")
        else:
            messages.error(request, _("messages#changes-cannot-be-saved"))
        update_project_admins(request.user, project)
    else:
        form = POImportForm()

    context = {
        "project": project,
        "form": form,
    }
    return render(request, "traduko/import-export/import-po.html", context)


@login_required
@user_is_project_admin
def import_nested_json(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    languages = get_languages_for_export(project)

    if request.method == "POST":
        form = ImportFormWithLanguage(
            data=request.POST, files=request.FILES, language_choices=languages
        )
        if form.is_valid():
            json_file = form.cleaned_data["file"]
            try:
                import_stats = import_from_nested_json(
                    project,
                    json_file,
                    form.cleaned_data["language"],
                    form.cleaned_data["update_texts"],
                    form.cleaned_data["user_is_author"],
                    request.user,
                    import_to=form.cleaned_data["import_to"],
                )
                messages.success(
                    request,
                    f"{import_stats['imported_strings']} ĉenoj kaj {import_stats['imported_translations']} tradukoj estis importitaj.",
                )
            except WrongFormatError:
                messages.error(request, "Malĝusta formato de dosiero.")
        else:
            messages.error(request, _("messages#changes-cannot-be-saved"))
        update_project_admins(request.user, project)
    else:
        form = ImportFormWithLanguage(language_choices=languages)

    context = {
        "project": project,
        "form": form,
    }
    return render(request, "traduko/import-export/import-nested-json.html", context)


@login_required
@user_is_project_admin
def import_history(request, project_id):
    project = get_object_or_404(Project, pk=project_id)

    if request.method == "POST":
        form = BasicImportForm(request.POST, request.FILES)
        if form.is_valid():
            json_file = form.cleaned_data["file"]
            try:
                number_imported = import_history_from_json(project, json_file)
                messages.success(
                    request, f"{number_imported} malnovaj ĉenoj estis importitaj."
                )
            except WrongFormatError:
                messages.error(request, "Malĝusta formato de dosiero.")
        else:
            messages.error(request, _("messages#changes-cannot-be-saved"))
        update_project_admins(request.user, project)
    else:
        form = BasicImportForm()

    context = {
        "project": project,
        "form": form,
    }
    return render(request, "traduko/import-export/import-history.html", context)


@login_required
@user_is_project_admin
def export_csv(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    languages = get_languages_for_export(project)

    if request.method == "POST":
        form = ExportForm(data=request.POST, language_choices=languages)
        if form.is_valid():
            data = export_to_csv(
                project,
                path=form.cleaned_data["path"],
                languages=form.cleaned_data["languages"],
                remove_path=form.cleaned_data["remove_path"],
                strings_to_export=form.cleaned_data["strings_to_export"],
            )
            filename = slugify(project.name)
            response = HttpResponse(content_type="text/csv")
            response["Content-Disposition"] = f'attachment; filename="{filename}.csv"'

            writer = csv.DictWriter(response, fieldnames=data["fieldnames"])
            writer.writeheader()
            for row in data["csv_data"]:
                writer.writerow(row)

            return response
    else:
        form = ExportForm(language_choices=languages)
    context = {
        "project": project,
        "form": form,
    }
    return render(request, "traduko/import-export/export-csv.html", context)


@login_required
@user_is_project_admin
def export_json(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    languages = get_languages_for_export(project)

    if request.method == "POST":
        form = ExportForm(data=request.POST, language_choices=languages)
        if form.is_valid():
            data = export_to_json(
                project,
                path=form.cleaned_data["path"],
                languages=form.cleaned_data["languages"],
                remove_path=form.cleaned_data["remove_path"],
                strings_to_export=form.cleaned_data["strings_to_export"],
            )
            filename = slugify(project.name)
            response = JsonResponse(data, safe=False)
            response["Content-Disposition"] = f'attachment; filename="{filename}.json"'
            return response
    else:
        form = ExportForm(language_choices=languages)
    context = {
        "project": project,
        "form": form,
    }
    return render(request, "traduko/import-export/export-json.html", context)


@login_required
@user_is_project_admin
def export_po(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    languages = get_languages_for_export(project)

    if request.method == "POST":
        form = POExportForm(data=request.POST, language_choices=languages)
        if form.is_valid():
            data = export_to_po(
                project,
                path=form.cleaned_data["path"],
                languages=form.cleaned_data["languages"],
                remove_path=form.cleaned_data["remove_path"],
                untranslated_as_source_language=form.cleaned_data[
                    "untranslated_as_source_language"
                ],
                include_outdated=form.cleaned_data["include_outdated"],
                original_text_as_key=form.cleaned_data["original_text_as_key"],
                file_name=form.cleaned_data["file_name"],
                strings_to_export=form.cleaned_data["strings_to_export"],
            )

            buffer = po_as_zip(data, form.cleaned_data["file_name"])
            return FileResponse(buffer, True, filename=f"{slugify(project.name)}.zip")
    else:
        form = POExportForm(
            initial={"untranslated_as_source_language": True},
            language_choices=languages,
        )
    context = {
        "project": project,
        "form": form,
    }
    return render(request, "traduko/import-export/export-po.html", context)


@login_required
@user_is_project_admin
def export_nested_json(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    languages = get_languages_for_export(project)

    if request.method == "POST":
        form = NestedJSONExportForm(data=request.POST, language_choices=languages)
        if form.is_valid():
            data = export_to_nested_json(
                project,
                path=form.cleaned_data["path"],
                languages=form.cleaned_data["languages"],
                remove_path=form.cleaned_data["remove_path"],
                untranslated_as_source_language=form.cleaned_data[
                    "untranslated_as_source_language"
                ],
                include_outdated=form.cleaned_data["include_outdated"],
                export_empty=form.cleaned_data["export_empty"],
                export_default=form.cleaned_data["export_default"],
                export_language_name=form.cleaned_data["export_language_name"],
                export_plural_rules=form.cleaned_data["export_plural_rules"],
                file_name=form.cleaned_data["file_name"],
                strings_to_export=form.cleaned_data["strings_to_export"],
            )

            buffer = nested_json_as_zip(data, form.cleaned_data["file_name"])
            return FileResponse(buffer, True, filename=f"{slugify(project.name)}.zip")

    else:
        form = NestedJSONExportForm(language_choices=languages)
    context = {
        "project": project,
        "form": form,
    }
    return render(request, "traduko/import-export/export-nested-json.html", context)
