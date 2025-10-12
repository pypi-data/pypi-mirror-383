from django import forms
from django.utils.translation import gettext_lazy as _

from buzzerboy_saas_tenants.saas_tenants.models.tenant import SubscriptionPlan, Tenant

class TenantSubscriptionForm(forms.ModelForm):
    class Meta:
        model = Tenant
        fields = ['subscription_plan']  # Change to a list

    subscription_plan = forms.ModelChoiceField(
        queryset=SubscriptionPlan.objects.all(),
        required=False,  # Change to True if you want to make it required
        label="",  # Empty label will hide the label
        help_text=None,  # Set help_text to None to hide it
        widget=forms.Select(attrs={'class': 'd-none'})  # Add your CSS class here
    )
