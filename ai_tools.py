"""AI tools for the WooCommerce Connect module."""
from assistant.tools import AssistantTool, register_tool


@register_tool
class GetWooCommerceConnection(AssistantTool):
    name = "get_woocommerce_connection"
    description = "Get the current WooCommerce connection details and status."
    module_id = "woocommerce_connect"
    required_permission = "woocommerce_connect.view_woocommerceconnection"
    parameters = {"type": "object", "properties": {}, "required": [], "additionalProperties": False}

    def execute(self, args, request):
        from woocommerce_connect.models import WooCommerceConnection
        c = WooCommerceConnection.objects.filter(is_deleted=False).first()
        if not c:
            return {"connection": None, "message": "No WooCommerce connection configured."}
        return {
            "id": str(c.id), "name": c.name, "store_url": c.store_url,
            "status": c.status, "sync_enabled": c.sync_enabled,
            "api_version": c.api_version,
            "last_sync_at": c.last_sync_at.isoformat() if c.last_sync_at else None,
            "last_sync_status": c.last_sync_status,
            "consumer_key_set": bool(c.consumer_key),
            "config": c.config if c.config else {},
        }


@register_tool
class ConnectWooCommerce(AssistantTool):
    name = "connect_woocommerce"
    description = "Connect to a WooCommerce store using API credentials (store URL, consumer key, consumer secret)."
    module_id = "woocommerce_connect"
    required_permission = "woocommerce_connect.add_woocommerceconnection"
    requires_confirmation = True
    parameters = {
        "type": "object",
        "properties": {
            "store_url": {"type": "string", "description": "WooCommerce store URL (e.g. https://yourstore.com)"},
            "name": {"type": "string", "description": "Friendly name for this connection"},
            "consumer_key": {"type": "string", "description": "WooCommerce REST API consumer key (ck_...)"},
            "consumer_secret": {"type": "string", "description": "WooCommerce REST API consumer secret (cs_...)"},
        },
        "required": ["store_url", "consumer_key", "consumer_secret"],
        "additionalProperties": False,
    }

    def execute(self, args, request):
        from woocommerce_connect.models import WooCommerceConnection
        store_url = args['store_url'].rstrip('/')
        name = args.get('name', store_url)
        c = WooCommerceConnection.objects.filter(is_deleted=False).first()
        if c:
            c.store_url = store_url
            c.name = name
            c.consumer_key = args['consumer_key']
            c.consumer_secret = args['consumer_secret']
            c.status = 'connected'
            c.save()
        else:
            c = WooCommerceConnection.objects.create(
                store_url=store_url,
                name=name,
                consumer_key=args['consumer_key'],
                consumer_secret=args['consumer_secret'],
                status='connected',
            )
        return {"id": str(c.id), "name": c.name, "status": c.status, "store_url": c.store_url}


@register_tool
class DisconnectWooCommerce(AssistantTool):
    name = "disconnect_woocommerce"
    description = "Disconnect from the current WooCommerce store. Clears API credentials."
    module_id = "woocommerce_connect"
    required_permission = "woocommerce_connect.change_woocommerceconnection"
    requires_confirmation = True
    parameters = {"type": "object", "properties": {}, "required": [], "additionalProperties": False}

    def execute(self, args, request):
        from woocommerce_connect.models import WooCommerceConnection
        c = WooCommerceConnection.objects.filter(is_deleted=False).first()
        if not c:
            return {"error": "No active WooCommerce connection found."}
        c.status = 'disconnected'
        c.sync_enabled = False
        c.consumer_key = ''
        c.consumer_secret = ''
        c.save()
        return {"id": str(c.id), "name": c.name, "status": c.status}


@register_tool
class TriggerWooCommerceSync(AssistantTool):
    name = "trigger_woocommerce_sync"
    description = "Trigger a sync operation with the connected WooCommerce store for a specific entity type."
    module_id = "woocommerce_connect"
    required_permission = "woocommerce_connect.manage_sync"
    requires_confirmation = True
    parameters = {
        "type": "object",
        "properties": {
            "entity_type": {
                "type": "string",
                "description": "Entity type to sync",
                "enum": ["products", "categories", "customers", "orders", "inventory"],
            },
        },
        "required": ["entity_type"],
        "additionalProperties": False,
    }

    def execute(self, args, request):
        from woocommerce_connect.models import WooCommerceConnection, WooCommerceSyncQueue
        c = WooCommerceConnection.objects.filter(is_deleted=False, status='connected').first()
        if not c:
            return {"error": "No active WooCommerce connection. Connect first."}
        q = WooCommerceSyncQueue.objects.create(
            connection=c,
            entity_type=args['entity_type'],
            action='full_sync',
            status='pending',
        )
        c.status = 'syncing'
        c.save(update_fields=['status', 'updated_at'])
        return {"queue_id": str(q.id), "entity_type": args['entity_type'], "status": "pending"}


@register_tool
class GetWooCommerceSyncStatus(AssistantTool):
    name = "get_woocommerce_sync_status"
    description = "Get the current sync status and pending queue items for WooCommerce."
    module_id = "woocommerce_connect"
    required_permission = "woocommerce_connect.view_synclog"
    parameters = {"type": "object", "properties": {}, "required": [], "additionalProperties": False}

    def execute(self, args, request):
        from woocommerce_connect.models import WooCommerceConnection, WooCommerceSyncQueue
        c = WooCommerceConnection.objects.filter(is_deleted=False).first()
        if not c:
            return {"connection": None}
        pending = WooCommerceSyncQueue.objects.filter(connection=c, is_deleted=False, status='pending').count()
        processing = WooCommerceSyncQueue.objects.filter(connection=c, is_deleted=False, status='processing').count()
        return {
            "connection_status": c.status,
            "sync_enabled": c.sync_enabled,
            "last_sync_at": c.last_sync_at.isoformat() if c.last_sync_at else None,
            "last_sync_status": c.last_sync_status,
            "pending_items": pending,
            "processing_items": processing,
        }


@register_tool
class ListWooCommerceSyncLog(AssistantTool):
    name = "list_woocommerce_sync_log"
    description = "List recent WooCommerce sync log entries. Optionally filter by entity type or status."
    module_id = "woocommerce_connect"
    required_permission = "woocommerce_connect.view_synclog"
    parameters = {
        "type": "object",
        "properties": {
            "entity_type": {"type": "string", "description": "Filter by entity type (products, orders, etc.)"},
            "status": {"type": "string", "description": "Filter by status (completed, failed, etc.)"},
            "limit": {"type": "integer", "description": "Number of entries to return (default 20)"},
        },
        "required": [],
        "additionalProperties": False,
    }

    def execute(self, args, request):
        from woocommerce_connect.models import WooCommerceSyncLog
        qs = WooCommerceSyncLog.objects.filter(is_deleted=False).order_by('-created_at')
        if args.get('entity_type'):
            qs = qs.filter(entity_type=args['entity_type'])
        if args.get('status'):
            qs = qs.filter(status=args['status'])
        limit = args.get('limit', 20)
        logs = qs[:limit]
        return {
            "logs": [
                {
                    "id": str(l.id),
                    "entity_type": l.entity_type,
                    "action": l.action,
                    "status": l.status,
                    "direction": l.direction,
                    "error_message": l.error_message,
                    "duration_ms": l.duration_ms,
                    "created_at": l.created_at.isoformat(),
                }
                for l in logs
            ],
            "total": qs.count(),
        }


@register_tool
class GetWooCommerceMappingStats(AssistantTool):
    name = "get_woocommerce_mapping_stats"
    description = "Get statistics about synced entity mappings between ERPlora and WooCommerce."
    module_id = "woocommerce_connect"
    required_permission = "woocommerce_connect.view_woocommerceconnection"
    parameters = {"type": "object", "properties": {}, "required": [], "additionalProperties": False}

    def execute(self, args, request):
        from django.db.models import Count
        from woocommerce_connect.models import WooCommerceSyncMapping
        stats = WooCommerceSyncMapping.objects.filter(is_deleted=False).values('entity_type').annotate(count=Count('id'))
        total = WooCommerceSyncMapping.objects.filter(is_deleted=False).count()
        return {
            "total_mappings": total,
            "by_entity_type": {s['entity_type']: s['count'] for s in stats},
        }
