def setup_bugsink(config):
    import sentry_sdk
    from sentry_sdk.integrations.django import DjangoIntegration

    sentry_sdk.init(
        dsn=config.BUGSINK_DSN,
        release=config.COMMIT_HASH,
        server_name=config.HOSTNAME,
        environment=config.ENVIRONMENT,
        integrations=[DjangoIntegration(signals_spans=False)],
        send_default_pii=True,
        max_request_body_size="always",
        # Don't event types which are not supported by Bugsink:
        traces_sample_rate=0,
        send_client_reports=False,
        auto_session_tracking=False,
    )
