import csv
from http import HTTPStatus
from io import BytesIO, StringIO
from typing import Annotated, Any, ClassVar, Final

from django.core.exceptions import NON_FIELD_ERRORS
from django.http import FileResponse
from django.shortcuts import get_object_or_404
from django.utils.text import slugify
from dmr import APIError, Controller, Path, modify, validate
from dmr.errors import ErrorType
from dmr.exceptions import ValidationError
from dmr.files import FileBody, FileResponseSpec
from dmr.headers import HeaderSpec
from dmr.metadata import ResponseSpec
from dmr.negotiation import conditional_type, request_renderer
from dmr.plugins.msgspec import MsgspecJsonRenderer, MsgspecSerializer
from dmr.renderers import FileRenderer

from traduko import export_functions as export
from traduko.api.schemas import LanguageSchema, ProjectPath
from traduko.forms import ExportForm, NestedJSONExportForm, POExportForm
from traduko.import_functions import get_languages_for_export
from traduko.models import Language, Project

MEDIA_TYPES: Final = {
    "json": "application/json",
    "csv": "text/csv",
    "po": "application/po",
    "zip": "application/zip",
    "tar.gz": "application/x-compressed-tar",
}
FORMATS: Final = {media: fmt for fmt, media in MEDIA_TYPES.items()}

# Attachments add these headers, but only file responses have them:
FILE_HEADERS: Final = {
    "Content-Length": HeaderSpec(required=False, skip_validation=True),
    "Content-Disposition": HeaderSpec(required=False, skip_validation=True),
}


def error_detail(message: str, *, loc: str | None = None) -> dict[str, Any]:
    """One item of the ``detail`` list, as DMR renders it."""
    detail: dict[str, Any] = {"msg": message, "type": str(ErrorType.value_error)}
    if loc is not None:
        detail["loc"] = [loc]
    return detail


def as_json(error: Exception) -> Exception:
    """
    Render the error as JSON, even when a file format was negotiated.

    File renderers cannot render error bodies,
    and ``global_error_handler`` reads ``renderer`` from the error.
    """
    error.renderer = MsgspecJsonRenderer()  # type: ignore[attr-defined]
    return error


def _csv_bytes(data: dict[str, Any]) -> bytes:
    buffer = StringIO()
    writer = csv.DictWriter(buffer, fieldnames=data["fieldnames"])
    writer.writeheader()
    writer.writerows(data["csv_data"])
    return buffer.getvalue().encode("utf-8")


class LanguageListController(Controller[MsgspecSerializer]):
    """Languages of the project, source language included."""

    responses = (
        ResponseSpec(Controller.error_model, status_code=HTTPStatus.NOT_FOUND),
    )

    def get(self, parsed_path: Path[ProjectPath]) -> list[LanguageSchema]:
        pk = parsed_path.pk
        get_object_or_404(Project, pk=pk)
        qs_source = Language.objects.filter(project__pk=pk)
        qs_lv = Language.objects.filter(languageversion__project__pk=pk)
        languages = (qs_source | qs_lv).distinct().order_by("code")
        return [LanguageSchema.from_language(language) for language in languages]


class ExportController(Controller[MsgspecSerializer]):
    """
    Shared logic of the export endpoints.

    The format is taken from the ``.<format>`` URL suffix when present,
    otherwise from the negotiated ``Accept`` header.
    """

    form_class: ClassVar[type[ExportForm]] = ExportForm
    accept_formats: ClassVar[tuple[str, ...]] = ("json",)
    # Errors are always JSON, even when a file format was negotiated:
    validate_negotiation = False
    responses = (
        ResponseSpec(Controller.error_model, status_code=HTTPStatus.BAD_REQUEST),
        ResponseSpec(Controller.error_model, status_code=HTTPStatus.NOT_FOUND),
    )

    def export_format(self) -> str:
        fmt = self.kwargs.get("format")
        if fmt is None:
            fmt = FORMATS[request_renderer(self.request, strict=True).content_type]
        if fmt not in self.accept_formats:
            raise as_json(
                APIError(
                    self.format_error(
                        f"{fmt.upper()} export not implemented for {type(self).__name__}",
                        error_type=ErrorType.user_msg,
                    ),
                    status_code=HTTPStatus.NOT_ACCEPTABLE,
                ),
            )
        return fmt

    def export_params(self, project: Project) -> dict[str, Any]:
        form = self.form_class(
            data=self.request.GET,
            language_choices=get_languages_for_export(project),
        )
        if form.is_valid():
            return form.cleaned_data
        raise as_json(
            ValidationError(
                [
                    error_detail(
                        message,
                        loc=None if field == NON_FIELD_ERRORS else field,
                    )
                    for field, messages in form.errors.items()
                    for message in messages
                ],
                status_code=HTTPStatus.BAD_REQUEST,
            ),
        )

    def one_language(self, params: dict[str, Any]) -> str:
        languages = params["languages"]
        if len(languages) > 1:
            message = "Only one ?languages=<code> is accepted"
        elif not languages:
            message = "?languages=<code> is required"
        else:
            return languages[0]
        raise as_json(
            ValidationError(
                [error_detail(message, loc="languages")],
                status_code=HTTPStatus.BAD_REQUEST,
            ),
        )

    def attachment(self, content: bytes, project: Project, fmt: str) -> FileResponse:
        stem = self.kwargs.get("stem") or slugify(project.name)
        return FileResponse(
            BytesIO(content),
            as_attachment=True,
            filename=f"{stem}.{fmt}",
            content_type=MEDIA_TYPES[fmt],
        )


class ExportSimpleController(ExportController):
    """All strings of the project, as JSON, CSV or a single PO file."""

    form_class = ExportForm
    accept_formats = ("json", "csv", "po")
    renderers = (
        MsgspecJsonRenderer(),
        FileRenderer(MEDIA_TYPES["csv"]),
        FileRenderer(MEDIA_TYPES["po"]),
    )

    @modify(headers=FILE_HEADERS)
    def get(
        self,
        parsed_path: Path[ProjectPath],
    ) -> Annotated[
        list[dict[str, Any]],
        conditional_type(
            {
                MEDIA_TYPES["json"]: list[dict[str, Any]],
                MEDIA_TYPES["csv"]: FileBody,
                MEDIA_TYPES["po"]: FileBody,
            }
        ),
    ]:
        project = get_object_or_404(Project, pk=parsed_path.pk)
        params = self.export_params(project)
        match self.export_format():
            case "csv":
                content = _csv_bytes(export.export_to_csv(project, **params))
                return self.attachment(content, project, "csv")
            case "po":
                lang = self.one_language(params)
                po_file = export.export_to_po(project, **params)[lang]
                return self.attachment(str(po_file).encode("utf-8"), project, "po")
            case _:
                return export.export_to_json(project, **params)


class ExportPoController(ExportController):
    """PO files of one or more languages, packed in a ZIP or tar.gz archive."""

    form_class = POExportForm
    accept_formats = ("po", "zip", "tar.gz")
    renderers = (
        MsgspecJsonRenderer(),
        FileRenderer(MEDIA_TYPES["po"]),
        FileRenderer(MEDIA_TYPES["zip"]),
        FileRenderer(MEDIA_TYPES["tar.gz"]),
    )

    @validate(
        FileResponseSpec(
            as_attachment=True,
            limit_to_content_types={
                MEDIA_TYPES["po"],
                MEDIA_TYPES["zip"],
                MEDIA_TYPES["tar.gz"],
            },
        ),
    )
    def get(self, parsed_path: Path[ProjectPath]) -> FileResponse:
        project = get_object_or_404(Project, pk=parsed_path.pk)
        params = self.export_params(project)
        fmt = self.export_format()
        if fmt == "po":
            lang = self.one_language(params)
            po_file = export.export_to_po(project, **params)[lang]
            return self.attachment(str(po_file).encode("utf-8"), project, "po")

        po_data = export.export_to_po(project, **params)
        if fmt == "zip":
            buffer = export.po_as_zip(po_data, params["file_name"])
        else:
            buffer = export.po_as_tar_gz(po_data, params["file_name"])
        return self.attachment(buffer.getvalue(), project, fmt)


class ExportNestedController(ExportController):
    """Nested JSON files of one or more languages, as JSON or an archive."""

    form_class = NestedJSONExportForm
    accept_formats = ("json", "zip", "tar.gz")
    renderers = (
        MsgspecJsonRenderer(),
        FileRenderer(MEDIA_TYPES["zip"]),
        FileRenderer(MEDIA_TYPES["tar.gz"]),
    )

    @modify(headers=FILE_HEADERS)
    def get(
        self,
        parsed_path: Path[ProjectPath],
    ) -> Annotated[
        dict[str, Any],
        conditional_type(
            {
                MEDIA_TYPES["json"]: dict[str, Any],
                MEDIA_TYPES["zip"]: FileBody,
                MEDIA_TYPES["tar.gz"]: FileBody,
            }
        ),
    ]:
        project = get_object_or_404(Project, pk=parsed_path.pk)
        params = self.export_params(project)
        match self.export_format():
            case "zip":
                data = export.export_to_nested_json(project, **params)
                buffer = export.nested_json_as_zip(data, params["file_name"])
                return self.attachment(buffer.getvalue(), project, "zip")
            case "tar.gz":
                data = export.export_to_nested_json(project, **params)
                buffer = export.nested_json_as_tar_gz(data, params["file_name"])
                return self.attachment(buffer.getvalue(), project, "tar.gz")
            case _:
                return export.export_to_nested_json(project, **params)
