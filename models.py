from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.core.models.base import HubBaseModel

CONN_STATUS = [
    ('connected', _('Connected')),
    ('disconnected', _('Disconnected')),
    ('error', _('Error')),
    ('syncing', _('Syncing')),
]

SYNC_DIRECTION_CHOICES = [
    ('bidirectional', _('Bidirectional')),
    ('to_woocommerce', _('To WooCommerce')),
    ('from_woocommerce', _('From WooCommerce')),
]

ENTITY_TYPE_CHOICES = [
    ('products', _('Products')),
    ('categories', _('Categories')),
    ('customers', _('Customers')),
    ('orders', _('Orders')),
    ('inventory', _('Inventory')),
]

SYNC_STATUS_CHOICES = [
    ('pending', _('Pending')),
    ('processing', _('Processing')),
    ('completed', _('Completed')),
    ('failed', _('Failed')),
    ('skipped', _('Skipped')),
]

QUEUE_STATUS_CHOICES = [
    ('pending', _('Pending')),
    ('processing', _('Processing')),
    ('completed', _('Completed')),
    ('failed', _('Failed')),
]


class WooCommerceConnection(HubBaseModel):
    store_url = models.CharField(max_length=255, verbose_name=_('Store URL'))
    name = models.CharField(max_length=255, verbose_name=_('Store Name'))
    status = models.CharField(max_length=20, default='disconnected', choices=CONN_STATUS, verbose_name=_('Status'))
    consumer_key = models.CharField(max_length=255, blank=True, verbose_name=_('Consumer Key'))
    consumer_secret = models.CharField(max_length=255, blank=True, verbose_name=_('Consumer Secret'))
    webhook_secret = models.CharField(max_length=255, blank=True, verbose_name=_('Webhook Secret'))
    api_version = models.CharField(max_length=10, default='wc/v3', verbose_name=_('API Version'))
    config = models.JSONField(default=dict, blank=True, verbose_name=_('Config'))
    sync_enabled = models.BooleanField(default=False, verbose_name=_('Sync Enabled'))
    last_sync_at = models.DateTimeField(null=True, blank=True, verbose_name=_('Last Sync At'))
    last_sync_status = models.CharField(max_length=20, blank=True, verbose_name=_('Last Sync Status'))

    class Meta(HubBaseModel.Meta):
        db_table = 'woocommerce_connect_connection'

    def __str__(self):
        return self.name


class WooCommerceSyncMapping(HubBaseModel):
    connection = models.ForeignKey(
        WooCommerceConnection, on_delete=models.CASCADE, related_name='mappings',
        verbose_name=_('Connection'),
    )
    entity_type = models.CharField(max_length=30, choices=ENTITY_TYPE_CHOICES, verbose_name=_('Entity Type'))
    local_id = models.UUIDField(verbose_name=_('Local ID'))
    remote_id = models.CharField(max_length=100, verbose_name=_('Remote ID'))
    remote_data_hash = models.CharField(max_length=64, blank=True, verbose_name=_('Remote Data Hash'))
    last_synced_at = models.DateTimeField(null=True, blank=True, verbose_name=_('Last Synced At'))
    sync_direction = models.CharField(
        max_length=30, default='bidirectional', choices=SYNC_DIRECTION_CHOICES,
        verbose_name=_('Sync Direction'),
    )

    class Meta(HubBaseModel.Meta):
        db_table = 'woocommerce_connect_syncmapping'
        unique_together = [('connection', 'entity_type', 'local_id'), ('connection', 'entity_type', 'remote_id')]

    def __str__(self):
        return f'{self.entity_type}: {self.local_id} <-> {self.remote_id}'


class WooCommerceSyncQueue(HubBaseModel):
    connection = models.ForeignKey(
        WooCommerceConnection, on_delete=models.CASCADE, related_name='queue_items',
        verbose_name=_('Connection'),
    )
    entity_type = models.CharField(max_length=30, choices=ENTITY_TYPE_CHOICES, verbose_name=_('Entity Type'))
    action = models.CharField(max_length=20, verbose_name=_('Action'))
    payload = models.JSONField(default=dict, blank=True, verbose_name=_('Payload'))
    status = models.CharField(max_length=20, default='pending', choices=QUEUE_STATUS_CHOICES, verbose_name=_('Status'))
    priority = models.IntegerField(default=0, verbose_name=_('Priority'))
    attempts = models.IntegerField(default=0, verbose_name=_('Attempts'))
    max_attempts = models.IntegerField(default=3, verbose_name=_('Max Attempts'))
    error_message = models.TextField(blank=True, verbose_name=_('Error Message'))
    scheduled_at = models.DateTimeField(null=True, blank=True, verbose_name=_('Scheduled At'))
    processed_at = models.DateTimeField(null=True, blank=True, verbose_name=_('Processed At'))

    class Meta(HubBaseModel.Meta):
        db_table = 'woocommerce_connect_syncqueue'
        ordering = ['-priority', 'created_at']

    def __str__(self):
        return f'{self.entity_type}/{self.action} [{self.status}]'


class WooCommerceSyncLog(HubBaseModel):
    connection = models.ForeignKey(
        WooCommerceConnection, on_delete=models.CASCADE, related_name='sync_logs',
        verbose_name=_('Connection'),
    )
    entity_type = models.CharField(max_length=30, choices=ENTITY_TYPE_CHOICES, verbose_name=_('Entity Type'))
    action = models.CharField(max_length=20, verbose_name=_('Action'))
    status = models.CharField(max_length=20, choices=SYNC_STATUS_CHOICES, verbose_name=_('Status'))
    local_id = models.UUIDField(null=True, blank=True, verbose_name=_('Local ID'))
    remote_id = models.CharField(max_length=100, blank=True, verbose_name=_('Remote ID'))
    direction = models.CharField(max_length=30, blank=True, verbose_name=_('Direction'))
    details = models.JSONField(default=dict, blank=True, verbose_name=_('Details'))
    error_message = models.TextField(blank=True, verbose_name=_('Error Message'))
    duration_ms = models.IntegerField(null=True, blank=True, verbose_name=_('Duration (ms)'))

    class Meta(HubBaseModel.Meta):
        db_table = 'woocommerce_connect_synclog'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.entity_type}/{self.action} - {self.status}'
