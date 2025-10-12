# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from django.urls import path
from buzzerboy_saas_tenants.saas_tenants.views import tenant_setting as tenant_settings_views

# URL Patterns for the application

urlpatterns =[
    path('tenant/settings/message-templates', tenant_settings_views.message_templates, name='message_templates'),
    path('tenant/settings/subscription-plans', tenant_settings_views.subscription_plans, name='tenant_subscription_plans'),
    path('tenant/settings/billing-and-payment', tenant_settings_views.billing_and_payment, name='tenant_billing_and_payment'),
    
    # User Management Routes
    path('tenant/settings/user-management', tenant_settings_views.user_management, name='tenant_user_management'),
    path('tenant/settings/user-management/<int:pk>/user-profile', tenant_settings_views.tenant_user_management_userprofile, name='tenant_user_management_userprofile_with_tenant'),
    path('tenant/settings/user-management/<int:pk>/user-profile/edit', tenant_settings_views.tenant_user_management_edit_userprofile, name='tenant_user_management_edit_userprofile_with_tenant'),
    path('tenant/settings/user-management/<uuid:pk>/deactivate', tenant_settings_views.deactivate_user_management, name='tenant_deactivate_user_management_with_tenant'),
    path('tenant/settings/user-management/<uuid:pk>/activate', tenant_settings_views.activate_user_management, name='tenant_activate_user_management_with_tenant'),
    path('tenant/settings/user-management/reset-password', tenant_settings_views.user_management_reset_user_password, name='tenant_user_management_reset_user_password_with_tenant'),


    path('tenant/settings/audit-trail', tenant_settings_views.audit_trail, name='tenant_audit_trail'),
    path('tenant/settings/notifications', tenant_settings_views.notifications, name='tenant_notifications'),
    path('tenant/settings/oganization-details', tenant_settings_views.organization_details, name='organization_details'),
    path('tenant/settings/address', tenant_settings_views.address, name='tenant_address'),
    path('tenant/settings/support', tenant_settings_views.support, name='tenant_support'),
]