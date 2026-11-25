from dmr.openapi import OpenAPIConfig
from dmr.settings import Settings


def dmr_settings(*, deployed: bool) -> dict:
    return {
        Settings.openapi_config: OpenAPIConfig(
            title="Tradukejo API",
            version="1.0",
            description="API por tradukejo.ikso.net/api",
        ),
        # Response validation costs time, keep it out of deployed environments:
        Settings.validate_responses: not deployed,
    }
