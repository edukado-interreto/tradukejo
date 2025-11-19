from typing import Any, Type


from rest_framework import viewsets
from rest_framework.exceptions import NotAcceptable, ValidationError
from rest_framework.renderers import JSONRenderer, BrowsableAPIRenderer
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.serializers import Serializer

from traduko import export_functions as export
from traduko.forms import ExportForm, NestedJSONExportForm, POExportForm
from traduko.import_functions import get_languages_for_export

from traduko.models import Project


class BaseExportViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = Serializer  # dummy
    accept_formats = ["json"]
    form_class = ExportForm
    body_fields = ["strings_to_export"]
    params = {}

    def get_queryset(self):
        return Project.objects.all()

    def get_form_class(self, format=None) -> Type[ExportForm]:
        if format:
            if form_class := {"po": POExportForm}.get(format):
                return form_class
        return self.form_class

    def get_form(self, project, format=None) -> ExportForm:
        data = self.request.query_params.copy()  # Make it mutable
        data.update(self.request.data)

        language_choices = get_languages_for_export(project)

        self.form = self.get_form_class(format)(
            data=data, language_choices=language_choices
        )
        return self.form

    def validate_form(self, project) -> dict[str, Any]:
        form = self.get_form(project)
        if form.is_valid():
            return form.cleaned_data
        else:
            raise ValidationError(form.errors)  # type: ignore

    def retrieve(self, request: Request, pk: int, stem: str | None = None, format=None):
        self.project = self.get_object()  # May raise NotFound

        self.params = self.validate_form(self.project)  # May raise ValidationError

        if isinstance(request.accepted_renderer, BrowsableAPIRenderer):
            # Dummy response for the browsable API
            return Response(dict(get_languages_for_export(self.project)))

        handler = self.get_format_handler()
        return handler(request, stem, format)

    def get_format_handler(self):
        media_type = self.request.accepted_media_type.split(";", 1)[0]
        format = {r.media_type: r.format for r in self.renderer_classes}.get(
            media_type, "json"
        )
        if format not in self.accept_formats:
            raise self.not_implemented(format)
        return getattr(self, f"_{format.replace('.', '')}")

    def finalize_response(self, request, response, *args, **kwargs):
        """Render as JSON if an exception occurred."""

        response = super().finalize_response(request, response, *args, **kwargs)
        if getattr(response, "exception", False):
            response.accepted_renderer = JSONRenderer()
            response.accepted_media_type = "application/json"
        return response

    def get_renderer_context(self):
        return {
            **super().get_renderer_context(),
            "params": self.params,
            "instance": self.get_object(),
        }

    def not_implemented(self, format):
        return NotAcceptable(
            f"{format.upper()} export not implemented for {self.__class__.__name__}"
        )

    def get_one_language(self):
        if len(self.params["languages"]) > 1:
            raise ValidationError("Only one ?languages=<code> is accepted")
        try:
            return self.params["languages"][0]
        except IndexError:
            raise ValidationError("?languages=<code> is required")


class ExportSimple(BaseExportViewSet):
    accept_formats = ["json", "csv", "po"]

    def _json(self, request, stem, format):
        return Response(export.export_to_json(self.project, **self.params))

    def _csv(self, request, stem, format):
        return Response(export.export_to_csv(self.project, **self.params))

    def _po(self, request, stem, format):
        lang = self.get_one_language()  # May raise ValidationError
        po_file = export.export_to_po(self.project, **self.params)[lang]
        return Response(po_file)


class ExportPo(BaseExportViewSet):
    accept_formats = ["po", "zip", "tar.gz"]
    form_class = POExportForm

    def _po(self, request, stem, format):
        lang = self.get_one_language()  # May raise ValidationError
        po_file = export.export_to_po(self.project, **self.params)[lang]
        return Response(po_file)

    def _zip(self, request, stem, format):
        lang_file_name = self.params["file_name"]
        data = export.export_to_po(self.project, **self.params)
        buffer = export.po_as_zip(data, lang_file_name)
        return Response(buffer)

    def _targz(self, request, stem, format):
        lang_file_name = self.params["file_name"]
        data = export.export_to_po(self.project, **self.params)
        buffer = export.po_as_tar_gz(data, lang_file_name)
        return Response(buffer)


class ExportNested(BaseExportViewSet):
    accept_formats = ["json", "zip", "tar.gz"]
    form_class = NestedJSONExportForm

    def _json(self, request, stem, format):
        return Response(export.export_to_nested_json(self.project, **self.params))

    def _zip(self, request, stem, format):
        lang_file_name = self.params["file_name"]
        data = export.export_to_nested_json(self.project, **self.params)
        buffer = export.nested_json_as_zip(data, lang_file_name)
        return Response(buffer)

    def _targz(self, request, stem, format):
        lang_file_name = self.params["file_name"]
        data = export.export_to_nested_json(self.project, **self.params)
        buffer = export.nested_json_as_tar_gz(data, lang_file_name)
        return Response(buffer)


ViewSetClass = type[BaseExportViewSet]
