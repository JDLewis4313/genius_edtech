from django.apps import AppConfig

class InteractionsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.social.interactions'
    label = 'interactions'
    verbose_name = 'Engagement Extensions'  # optional, admin UI friendly

    def ready(self):
        # Load custom template tags if needed
        try:
            import apps.extensions.interactions.templatetags.utils
        except ImportError:
            pass
