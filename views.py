"""
WooCommerce Connect Module Views
"""
import json

from django.core.paginator import Paginator
from django.db.models import Q, Count
from django.http import HttpResponse, JsonResponse
from django.urls import reverse
from django.shortcuts import get_object_or_404, render as django_render
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from apps.accounts.decorators import login_required, permission_required
from apps.core.htmx import htmx_view
from apps.modules_runtime.navigation import with_module_nav

from .models import WooCommerceConnection, WooCommerceSyncLog, WooCommerceSyncMapping, WooCommerceSyncQueue
from .forms import WooCommerceConnectionForm, WooCommerceSettingsForm


# ======================================================================
# Dashboard
# ======================================================================

@login_required
@with_module_nav('woocommerce_connect', 'dashboard')
@htmx_view('woocommerce_connect/pages/index.html', 'woocommerce_connect/partials/dashboard_content.html')
def dashboard(request):
    hub_id = request.session.get('hub_id')
    connection = WooCommerceConnection.objects.filter(hub_id=hub_id, is_deleted=False).first()
    recent_logs = WooCommerceSyncLog.objects.filter(
        hub_id=hub_id, is_deleted=False,
    ).order_by('-created_at')[:5] if connection else []
    total_mappings = WooCommerceSyncMapping.objects.filter(hub_id=hub_id, is_deleted=False).count()
    pending_queue = WooCommerceSyncQueue.objects.filter(hub_id=hub_id, is_deleted=False, status='pending').count()

    return {
        'connection': connection,
        'recent_logs': recent_logs,
        'total_mappings': total_mappings,
        'pending_queue': pending_queue,
    }


# ======================================================================
# Connection
# ======================================================================

@login_required
@permission_required('woocommerce_connect.view_woocommerceconnection')
@with_module_nav('woocommerce_connect', 'connection')
@htmx_view('woocommerce_connect/pages/connection.html', 'woocommerce_connect/partials/connection_content.html')
def connection_detail(request):
    hub_id = request.session.get('hub_id')
    connection = WooCommerceConnection.objects.filter(hub_id=hub_id, is_deleted=False).first()
    form = WooCommerceConnectionForm(instance=connection) if connection else WooCommerceConnectionForm()
    return {
        'connection': connection,
        'form': form,
    }


@login_required
@permission_required('woocommerce_connect.add_woocommerceconnection')
@require_POST
def connection_connect(request):
    hub_id = request.session.get('hub_id')
    connection = WooCommerceConnection.objects.filter(hub_id=hub_id, is_deleted=False).first()

    store_url = request.POST.get('store_url', '').strip().rstrip('/')
    name = request.POST.get('name', '').strip()
    consumer_key = request.POST.get('consumer_key', '').strip()
    consumer_secret = request.POST.get('consumer_secret', '').strip()
    api_version = request.POST.get('api_version', 'wc/v3').strip()

    if not store_url or not consumer_key or not consumer_secret:
        return HttpResponse(status=400)

    if connection:
        connection.store_url = store_url
        connection.name = name or store_url
        connection.consumer_key = consumer_key
        connection.consumer_secret = consumer_secret
        connection.api_version = api_version
        connection.status = 'connected'
        connection.save()
    else:
        connection = WooCommerceConnection.objects.create(
            hub_id=hub_id,
            store_url=store_url,
            name=name or store_url,
            consumer_key=consumer_key,
            consumer_secret=consumer_secret,
            api_version=api_version,
            status='connected',
        )

    response = HttpResponse(status=204)
    response['HX-Redirect'] = reverse('woocommerce_connect:connection')
    return response


@login_required
@permission_required('woocommerce_connect.change_woocommerceconnection')
@require_POST
def connection_disconnect(request):
    hub_id = request.session.get('hub_id')
    connection = WooCommerceConnection.objects.filter(hub_id=hub_id, is_deleted=False).first()
    if connection:
        connection.status = 'disconnected'
        connection.sync_enabled = False
        connection.consumer_key = ''
        connection.consumer_secret = ''
        connection.save()

    response = HttpResponse(status=204)
    response['HX-Redirect'] = reverse('woocommerce_connect:connection')
    return response


# ======================================================================
# Sync Log
# ======================================================================

@login_required
@permission_required('woocommerce_connect.view_synclog')
@with_module_nav('woocommerce_connect', 'log')
@htmx_view('woocommerce_connect/pages/log.html', 'woocommerce_connect/partials/sync_log_content.html')
def sync_log_list(request):
    hub_id = request.session.get('hub_id')
    search_query = request.GET.get('q', '').strip()
    page_number = request.GET.get('page', 1)
    per_page = int(request.GET.get('per_page', 24))
    entity_filter = request.GET.get('entity_type', '')
    status_filter = request.GET.get('status', '')

    qs = WooCommerceSyncLog.objects.filter(hub_id=hub_id, is_deleted=False)

    if search_query:
        qs = qs.filter(
            Q(entity_type__icontains=search_query) |
            Q(action__icontains=search_query) |
            Q(error_message__icontains=search_query)
        )
    if entity_filter:
        qs = qs.filter(entity_type=entity_filter)
    if status_filter:
        qs = qs.filter(status=status_filter)

    qs = qs.order_by('-created_at')

    paginator = Paginator(qs, per_page)
    page_obj = paginator.get_page(page_number)

    if request.htmx and request.htmx.target == 'datatable-body':
        return django_render(request, 'woocommerce_connect/partials/sync_log_list.html', {
            'logs': page_obj, 'page_obj': page_obj,
            'search_query': search_query, 'entity_filter': entity_filter,
            'status_filter': status_filter, 'per_page': per_page,
        })

    return {
        'logs': page_obj,
        'page_obj': page_obj,
        'search_query': search_query,
        'entity_filter': entity_filter,
        'status_filter': status_filter,
        'per_page': per_page,
    }


# ======================================================================
# Mapping
# ======================================================================

@login_required
@permission_required('woocommerce_connect.view_woocommerceconnection')
@with_module_nav('woocommerce_connect', 'mapping')
@htmx_view('woocommerce_connect/pages/mapping.html', 'woocommerce_connect/partials/mapping_content.html')
def mapping_list(request):
    hub_id = request.session.get('hub_id')
    search_query = request.GET.get('q', '').strip()
    page_number = request.GET.get('page', 1)
    per_page = int(request.GET.get('per_page', 24))
    entity_filter = request.GET.get('entity_type', '')

    qs = WooCommerceSyncMapping.objects.filter(hub_id=hub_id, is_deleted=False)

    if search_query:
        qs = qs.filter(
            Q(entity_type__icontains=search_query) |
            Q(remote_id__icontains=search_query)
        )
    if entity_filter:
        qs = qs.filter(entity_type=entity_filter)

    qs = qs.order_by('-last_synced_at')

    paginator = Paginator(qs, per_page)
    page_obj = paginator.get_page(page_number)

    # Stats by entity type
    mapping_stats = WooCommerceSyncMapping.objects.filter(
        hub_id=hub_id, is_deleted=False,
    ).values('entity_type').annotate(count=Count('id'))

    if request.htmx and request.htmx.target == 'datatable-body':
        return django_render(request, 'woocommerce_connect/partials/mapping_list.html', {
            'mappings': page_obj, 'page_obj': page_obj,
            'search_query': search_query, 'entity_filter': entity_filter,
            'per_page': per_page, 'mapping_stats': mapping_stats,
        })

    return {
        'mappings': page_obj,
        'page_obj': page_obj,
        'search_query': search_query,
        'entity_filter': entity_filter,
        'per_page': per_page,
        'mapping_stats': mapping_stats,
    }


# ======================================================================
# Settings
# ======================================================================

@login_required
@permission_required('woocommerce_connect.manage_settings')
@with_module_nav('woocommerce_connect', 'settings')
@htmx_view('woocommerce_connect/pages/settings.html', 'woocommerce_connect/partials/settings_content.html')
def settings_view(request):
    hub_id = request.session.get('hub_id')
    connection = WooCommerceConnection.objects.filter(hub_id=hub_id, is_deleted=False).first()

    if request.method == 'POST' and connection:
        form = WooCommerceSettingsForm(request.POST)
        if form.is_valid():
            config = connection.config or {}
            config.update({
                'sync_direction': form.cleaned_data['sync_direction'],
                'source_of_truth': form.cleaned_data['source_of_truth'],
                'price_includes_tax': form.cleaned_data['price_includes_tax'],
                'auto_sync_products': form.cleaned_data['auto_sync_products'],
                'auto_sync_orders': form.cleaned_data['auto_sync_orders'],
                'auto_sync_customers': form.cleaned_data['auto_sync_customers'],
                'auto_sync_inventory': form.cleaned_data['auto_sync_inventory'],
                'sync_interval_minutes': form.cleaned_data['sync_interval_minutes'],
            })
            connection.config = config
            connection.save(update_fields=['config', 'updated_at'])

            if request.htmx:
                return django_render(request, 'woocommerce_connect/partials/settings_content.html', {
                    'connection': connection,
                    'form': WooCommerceSettingsForm(initial=connection.config),
                    'saved': True,
                })
    else:
        initial = connection.config if connection and connection.config else {}
        form = WooCommerceSettingsForm(initial=initial)

    return {
        'connection': connection,
        'form': form,
    }


# ======================================================================
# Sync Trigger
# ======================================================================

@login_required
@permission_required('woocommerce_connect.manage_sync')
@require_POST
def trigger_sync(request):
    hub_id = request.session.get('hub_id')
    connection = WooCommerceConnection.objects.filter(hub_id=hub_id, is_deleted=False, status='connected').first()
    if not connection:
        return HttpResponse(status=400)

    entity_type = request.POST.get('entity_type', 'products')

    # Create a queue item for async processing
    WooCommerceSyncQueue.objects.create(
        hub_id=hub_id,
        connection=connection,
        entity_type=entity_type,
        action='full_sync',
        status='pending',
    )

    connection.status = 'syncing'
    connection.save(update_fields=['status', 'updated_at'])

    response = HttpResponse(status=204)
    response['HX-Redirect'] = reverse('woocommerce_connect:log')
    return response


# ======================================================================
# Webhook Handler
# ======================================================================

@csrf_exempt
@require_POST
def webhook_handler(request):
    """Handle incoming WooCommerce webhooks."""
    try:
        payload = json.loads(request.body)
    except (json.JSONDecodeError, ValueError):
        return JsonResponse({'error': 'Invalid JSON'}, status=400)

    # Webhook processing would happen here
    # For now, just acknowledge receipt
    return JsonResponse({'status': 'ok'})
