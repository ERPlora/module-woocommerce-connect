from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class WooCommerceConnectConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'woocommerce_connect'
    label = 'woocommerce_connect'
    verbose_name = _('WooCommerce')

    def ready(self):
        pass
