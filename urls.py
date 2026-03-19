from django.urls import path
from . import views

app_name = 'woocommerce_connect'

urlpatterns = [
    # Dashboard
    path('', views.dashboard, name='dashboard'),

    # Navigation tab aliases
    path('connection/', views.connection_detail, name='connection'),
    path('log/', views.sync_log_list, name='log'),
    path('mapping/', views.mapping_list, name='mapping'),

    # Connection actions
    path('connection/connect/', views.connection_connect, name='connection_connect'),
    path('connection/disconnect/', views.connection_disconnect, name='connection_disconnect'),

    # Sync
    path('sync/trigger/', views.trigger_sync, name='trigger_sync'),

    # Webhook
    path('webhook/', views.webhook_handler, name='webhook_handler'),

    # Settings
    path('settings/', views.settings_view, name='settings'),
]
