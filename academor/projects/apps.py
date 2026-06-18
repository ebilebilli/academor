from django.apps import AppConfig


class ProjectsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'projects'

    def ready(self):
        import projects.signals  # noqa: F401
        import projects.admin  # noqa: F401 — register all ModelAdmin classes
