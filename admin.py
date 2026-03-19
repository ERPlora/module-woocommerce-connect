from django.contrib import admin

from .models import (
    WooCommerceConnection,
    WooCommerceSyncMapping,
    WooCommerceSyncQueue,
    WooCommerceSyncLog,
)


@admin.register(WooCommerceConnection)
class WooCommerceConnectionAdmin(admin.ModelAdmin):
    list_display = ['name', 'store_url', 'status', 'sync_enabled', 'last_sync_at', 'created_at']
    search_fields = ['name', 'store_url', 'status']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(WooCommerceSyncMapping)
class WooCommerceSyncMappingAdmin(admin.ModelAdmin):
    list_display = ['connection', 'entity_type', 'local_id', 'remote_id', 'last_synced_at']
    search_fields = ['entity_type', 'remote_id']
    list_filter = ['entity_type', 'sync_direction']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(WooCommerceSyncQueue)
class WooCommerceSyncQueueAdmin(admin.ModelAdmin):
    list_display = ['connection', 'entity_type', 'action', 'status', 'attempts', 'created_at']
    search_fields = ['entity_type', 'action']
    list_filter = ['status', 'entity_type']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(WooCommerceSyncLog)
class WooCommerceSyncLogAdmin(admin.ModelAdmin):
    list_display = ['connection', 'entity_type', 'action', 'status', 'direction', 'created_at']
    search_fields = ['entity_type', 'action', 'error_message']
    list_filter = ['status', 'entity_type', 'action']
    readonly_fields = ['created_at', 'updated_at']
