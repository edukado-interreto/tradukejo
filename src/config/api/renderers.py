import csv
from django.template import loader

from django.http.response import FileResponse, HttpResponse
from django.utils.text import slugify
from rest_framework import renderers


class BrowsableAPIRenderer(renderers.BrowsableAPIRenderer):
    def get_context(self, data, accepted_media_type, renderer_context):
        context = super().get_context(data, accepted_media_type, renderer_context)
        context["params_form"] = self.get_params_form(data, context["view"])
        return context

    def get_params_form(self, data, view):
        if not hasattr(view, "get_form"):
            return ""
        form = view.get_form(view.get_object())
        template = loader.get_template("api/filter_form.html")
        context = {"form": form, "exclude_fields": view.body_fields}
        return template.render(context)


class BaseRenderer(renderers.BaseRenderer):
    def get_filename(self, context=None):
        stem = context["kwargs"].get("stem", slugify(context["view"].project.name))
        extension = context["kwargs"].get("format", self.format)
        return f"{stem}.{extension}"

    def render(self, data, accepted_media_type=None, renderer_context=None):
        filename = self.get_filename(context=renderer_context)
        return FileResponse(data, as_attachment=True, filename=filename)


class CsvRenderer(BaseRenderer):
    media_type = "text/csv"
    format = "csv"

    def render(self, data, accepted_media_type=None, renderer_context=None):
        filename = self.get_filename(context=renderer_context)
        headers = {"Content-Disposition": f'attachment; filename="{filename}"'}
        response = HttpResponse(content_type=self.media_type, headers=headers)

        writer = csv.DictWriter(response, fieldnames=data["fieldnames"])
        writer.writeheader()
        for row in data["csv_data"]:
            writer.writerow(row)

        return response


class PoRenderer(BaseRenderer):
    media_type = "application/po"
    format = "po"


class TarGzRenderer(BaseRenderer):
    media_type = "application/x-compressed-tar"
    format = "tar.gz"


class ZipFileRenderer(BaseRenderer):
    media_type = "application/zip"
    format = "zip"
