from django.utils.translation import gettext_lazy as _

MODULE_ID = 'woocommerce_connect'
MODULE_NAME = _('WooCommerce')
MODULE_VERSION = '1.0.0'
MODULE_ICON = 'material:store'
MODULE_DESCRIPTION = _('Sync products, inventory, orders and customers with your WooCommerce store')
MODULE_AUTHOR = 'ERPlora'
MODULE_CATEGORY = 'integrations'

MENU = {
    'label': _('WooCommerce'),
    'icon': 'material:store',
    'order': 89,
}

NAVIGATION = [
    {'label': _('Dashboard'), 'icon': 'speedometer-outline', 'id': 'dashboard'},
    {'label': _('Connection'), 'icon': 'link-outline', 'id': 'connection'},
    {'label': _('Sync Log'), 'icon': 'list-outline', 'id': 'log'},
    {'label': _('Mapping'), 'icon': 'git-compare-outline', 'id': 'mapping'},
    {'label': _('Settings'), 'icon': 'settings-outline', 'id': 'settings'},
]

DEPENDENCIES = ['inventory', 'customers', 'ecommerce']

PERMISSIONS = [
    'woocommerce_connect.view_woocommerceconnection',
    'woocommerce_connect.add_woocommerceconnection',
    'woocommerce_connect.change_woocommerceconnection',
    'woocommerce_connect.delete_woocommerceconnection',
    'woocommerce_connect.view_synclog',
    'woocommerce_connect.manage_sync',
    'woocommerce_connect.manage_settings',
]

ROLE_PERMISSIONS = {
    "admin": ["*"],
    "manager": [
        "view_woocommerceconnection",
        "add_woocommerceconnection",
        "change_woocommerceconnection",
        "view_synclog",
        "manage_sync",
    ],
    "employee": [
        "view_woocommerceconnection",
        "view_synclog",
    ],
}
