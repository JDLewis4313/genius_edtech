# apps/interactions/apps.py
from django.apps import AppConfig
import apps.interactions.templatetags.utils  # 👈 Force registration

class InteractionsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.interactions'
