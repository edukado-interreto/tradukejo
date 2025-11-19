REST_FRAMEWORK = {
    "DEFAULT_RENDERER_CLASSES": [
        "rest_framework.renderers.JSONRenderer",
        "tradukejo.api.renderers.BrowsableAPIRenderer",
        "tradukejo.api.renderers.CsvRenderer",
        "tradukejo.api.renderers.PoRenderer",
        "tradukejo.api.renderers.TarGzRenderer",
        "tradukejo.api.renderers.ZipFileRenderer",
    ],
    "EXCEPTION_HANDLER": "drf_standardized_errors.handler.exception_handler",
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
}

SPECTACULAR_SETTINGS = {
    "TITLE": "Tradukejo API",
    "DESCRIPTION": "API por tradukejo.ikso.net/api",
    "VERSION": "1.0",
    "SERVE_INCLUDE_SCHEMA": False,
}
