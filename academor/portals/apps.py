from django.apps import AppConfig


class PortalsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'portals'
    verbose_name = 'Student portal'

    def ready(self):
        from portals.utils.username_validators import apply_portal_username_validators

        apply_portal_username_validators()
        import portals.signals  # noqa: F401
        import portals.admin  # noqa: F401
