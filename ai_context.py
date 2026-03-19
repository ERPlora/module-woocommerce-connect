"""
AI context for the WooCommerce Connect module.
Loaded into the assistant system prompt when this module's tools are active.
"""

CONTEXT = """
## Module Knowledge: WooCommerce Connect

### Models

**WooCommerceConnection**
- `store_url` (CharField, max 255) — WooCommerce store URL (e.g. https://yourstore.com)
- `name` (CharField) — human-readable connection name
- `status` (CharField) — choices: connected, disconnected, error, syncing
- `consumer_key` (CharField) — WooCommerce REST API consumer key (ck_...)
- `consumer_secret` (CharField) — WooCommerce REST API consumer secret (cs_...)
- `webhook_secret` (CharField) — secret for validating incoming webhooks
- `api_version` (CharField, default 'wc/v3') — WooCommerce API version
- `config` (JSONField) — sync_direction, source_of_truth, price_includes_tax, auto_sync settings, etc.
- `sync_enabled` (BooleanField) — whether automatic sync is active
- `last_sync_at` (DateTimeField, nullable) — when data was last synchronized
- `last_sync_status` (CharField) — status of the last sync operation

**WooCommerceSyncMapping**
- Maps local ERPlora entities to WooCommerce remote IDs
- `entity_type` — products, categories, customers, orders, inventory
- `local_id` (UUID) — ERPlora record ID
- `remote_id` (CharField) — WooCommerce record ID
- `sync_direction` — bidirectional, to_woocommerce, from_woocommerce

**WooCommerceSyncQueue**
- Queue of pending sync operations
- `entity_type`, `action`, `payload`, `status` (pending/processing/completed/failed)
- `priority`, `attempts`, `max_attempts`, `error_message`

**WooCommerceSyncLog**
- History of all sync operations
- `entity_type`, `action`, `status`, `direction`, `details`, `error_message`, `duration_ms`

### Key flows

1. **Connect**: User provides store URL + consumer key + consumer secret (WooCommerce REST API keys). No OAuth — just API key auth. Status becomes 'connected'.
2. **Sync**: Trigger sync for entity types (products, orders, customers, inventory). Creates queue items processed asynchronously.
3. **Mapping**: Each synced entity gets a mapping record linking local UUID to WooCommerce remote ID.
4. **Webhooks**: WooCommerce can push updates via webhooks (order created, product updated, etc.).
5. **Disconnect**: Clears API credentials, disables sync. Mapping data is preserved.

### Configuration (stored in connection.config JSON)
- `sync_direction`: bidirectional, to_woocommerce, from_woocommerce
- `source_of_truth`: erplora or woocommerce (conflict resolution)
- `price_includes_tax`: boolean
- `auto_sync_products/orders/customers/inventory`: booleans
- `sync_interval_minutes`: sync frequency (5-1440)

### Relationships
- Depends on: inventory (products/stock), customers, ecommerce (orders)
- One connection per hub (singleton-like usage)
- Mappings link to inventory.Product, customers.Customer, orders.Order via UUID
"""
