# WooCommerce Connect

## Overview

| Property | Value |
|----------|-------|
| **Module ID** | `woocommerce_connect` |
| **Version** | `1.0.0` |
| **Icon** | `material:store` |
| **Category** | `integrations` |
| **Dependencies** | `inventory`, `customers`, `ecommerce` |
| **Pricing** | Subscription, 12.99 EUR/month |

## Description

Sync products, inventory, orders and customers between ERPlora and your WooCommerce store. Uses WooCommerce REST API with consumer key/secret authentication.

## Models

### `WooCommerceConnection`
Store connection credentials and sync configuration. One connection per hub.

### `WooCommerceSyncMapping`
Maps local ERPlora entity UUIDs to WooCommerce remote IDs for products, categories, customers, orders, and inventory.

### `WooCommerceSyncQueue`
Queue of pending sync operations processed asynchronously.

### `WooCommerceSyncLog`
History of all sync operations with status, duration, and error details.

## Navigation

| View | ID |
|------|----|
| Dashboard | `dashboard` |
| Connection | `connection` |
| Sync Log | `log` |
| Mapping | `mapping` |
| Settings | `settings` |
