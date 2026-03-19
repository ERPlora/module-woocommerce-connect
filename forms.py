from django import forms
from django.utils.translation import gettext_lazy as _

from .models import WooCommerceConnection, SYNC_DIRECTION_CHOICES


class WooCommerceConnectionForm(forms.ModelForm):
    class Meta:
        model = WooCommerceConnection
        fields = ['name', 'store_url', 'consumer_key', 'consumer_secret', 'api_version']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'input input-sm w-full'}),
            'store_url': forms.URLInput(attrs={'class': 'input input-sm w-full', 'placeholder': 'https://yourstore.com'}),
            'consumer_key': forms.TextInput(attrs={'class': 'input input-sm w-full', 'placeholder': 'ck_...'}),
            'consumer_secret': forms.PasswordInput(attrs={'class': 'input input-sm w-full', 'placeholder': 'cs_...'}),
            'api_version': forms.TextInput(attrs={'class': 'input input-sm w-full'}),
        }


class WooCommerceSettingsForm(forms.Form):
    sync_direction = forms.ChoiceField(
        choices=SYNC_DIRECTION_CHOICES,
        widget=forms.Select(attrs={'class': 'select select-sm w-full'}),
        label=_('Default Sync Direction'),
    )
    source_of_truth = forms.ChoiceField(
        choices=[('erplora', _('ERPlora')), ('woocommerce', _('WooCommerce'))],
        widget=forms.Select(attrs={'class': 'select select-sm w-full'}),
        label=_('Source of Truth'),
    )
    price_includes_tax = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'toggle'}),
        label=_('Price Includes Tax'),
    )
    auto_sync_products = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'toggle'}),
        label=_('Auto-sync Products'),
    )
    auto_sync_orders = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'toggle'}),
        label=_('Auto-sync Orders'),
    )
    auto_sync_customers = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'toggle'}),
        label=_('Auto-sync Customers'),
    )
    auto_sync_inventory = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'toggle'}),
        label=_('Auto-sync Inventory'),
    )
    sync_interval_minutes = forms.IntegerField(
        min_value=5,
        max_value=1440,
        initial=30,
        widget=forms.NumberInput(attrs={'class': 'input input-sm w-full'}),
        label=_('Sync Interval (minutes)'),
    )
