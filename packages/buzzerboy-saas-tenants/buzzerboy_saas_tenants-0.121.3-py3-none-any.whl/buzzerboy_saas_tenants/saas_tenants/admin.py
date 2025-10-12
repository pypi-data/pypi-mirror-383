from django.contrib import admin

# Register your models here.
from django.contrib import admin
from translated_fields import TranslatedFieldAdmin

from buzzerboy_saas_tenants.saas_tenants.models.account_settings import (
    NotificationPreferences, NotificationChannel, NotificationSettings, NotificationType)

from buzzerboy_saas_tenants.saas_tenants.models.accounts import  UserType, UserTypeAccess, UserProfile

from buzzerboy_saas_tenants.saas_tenants.models.accounts import (
    UserType, UserTypeAccess, UserProfile
)

from buzzerboy_saas_tenants.saas_tenants.models.invites import Invites
from buzzerboy_saas_tenants.saas_tenants.models.localization import  StateProvince, SupportedLanguage
from buzzerboy_saas_tenants.saas_tenants.models.tenant import Tenant, TenantLanguages, ContractStatus, SubscriptionPlan
from buzzerboy_saas_tenants.saas_tenants.models.tenant_setting import AuditLog, BillingDetails, SupportCase

from buzzerboy_saas_tenants.saas_tenants.models.ai_chat import AIChat, ChatInteraction



# Account Settings Admin Models
admin.site.register(NotificationPreferences)
admin.site.register(NotificationChannel)
admin.site.register(NotificationSettings)
admin.site.register(NotificationType)

# AI Chat Admin Models
admin.site.register(AIChat)
admin.site.register(ChatInteraction)
admin.site.register(SupportedLanguage)

# Account Admin Models
class UserProfileAdmin(admin.ModelAdmin):
    """
    Custom admin interface for the UserProfile model.
    - list_display: Specifies the fields to display in the admin list view.
    - list_filter: Adds filtering options for the specified fields.
    """
    list_display = ("user_object", "tenant", "user_type",)
    list_filter = ("user_type", "tenant")

class UserTypeAccessAdmin(admin.ModelAdmin):
    """
    Custom admin interface for the UserTypeAccess model.
    - list_display: Specifies the fields to display in the admin list view.
    - list_filter: Adds filtering options for the specified fields.
    """
    list_display = ("user_type", "request_path", "access_key")
    list_filter = ("user_type", "request_path", "access_key")

@admin.register(UserType)
class UserTypeAdmin(TranslatedFieldAdmin, admin.ModelAdmin):
    list_display = (
        'pk'  ,
        *UserType.name.fields,
        *UserType.description.fields,
        "has_full_access",
        "has_nonstaff_access",
    )
    list_filter = ("has_full_access", "has_nonstaff_access")
    search_fields = (
        *UserType.name.fields,
        *UserType.description.fields,
    )
    fieldsets = (
        (None, {"fields": (*UserType.name.fields, *UserType.description.fields)}),
        ("Access Controls", {"fields": ("has_full_access", "has_nonstaff_access")}),
    )
admin.site.register(UserProfile, UserProfileAdmin)
admin.site.register(UserTypeAccess, UserTypeAccessAdmin)


# For Custom Admin Interface | Not Required | Not Registered
class TenantAdmin(admin.ModelAdmin):
    """
    Custom admin interface for the Tenant model.
    - list_display: Specifies the fields to display in the admin list view.
    - list_filter: Adds filtering options for the specified fields.
    - search_fields: Allows searching by specified fields.
    """
    list_display = ("company_name", "contract_status", "primary_account_name", "primary_account_email")
    list_filter = ("contract_status",)
    search_fields = ("company_name",)

class UserProfileAdmin(admin.ModelAdmin):
    """
    Custom admin interface for the UserProfile model.
    - list_display: Specifies the fields to display in the admin list view.
    - list_filter: Adds filtering options for the specified fields.
    """
    list_display = ("user_object", "tenant", "user_type",)
    list_filter = ("user_type", "tenant")

class TenantLanguageAdmin(admin.ModelAdmin):
    """
    Custom admin interface for the TenantLanguages model.
    - list_display: Specifies the fields to display in the admin list view.
    - list_filter: Adds filtering options for the specified fields.
    """
    list_display = ("tenant", "language",)
    list_filter = ("language", "tenant")

class UserTypeAccessAdmin(admin.ModelAdmin):
    """
    Custom admin interface for the UserTypeAccess model.
    - list_display: Specifies the fields to display in the admin list view.
    - list_filter: Adds filtering options for the specified fields.
    """
    list_display = ("user_type", "request_path", "access_key")
    list_filter = ("user_type", "request_path", "access_key")



# For Invite Entity
admin.site.register(Invites)

# For localization
class StateProvinceAdmin(admin.ModelAdmin):
    """
    Custom admin interface for the StateProvince model.
    - list_display: Specifies the fields to display in the admin list view.
    - list_filter: Adds filtering options for the specified fields.
    - search_fields: Allows searching by specified fields.
    """
    list_display = ("location_name", "country")
    list_filter = ("country",)
    search_fields = ("location_name", "country")

admin.site.register(StateProvince, StateProvinceAdmin)



# Tenant Admin Models
class TenantAdmin(admin.ModelAdmin):
    """
    Custom admin interface for the Tenant model.
    - list_display: Specifies the fields to display in the admin list view.
    - list_filter: Adds filtering options for the specified fields.
    - search_fields: Allows searching by specified fields.
    """
    list_display = ("company_name", "contract_status", "primary_account_name", "primary_account_email")
    list_filter = ("contract_status",)
    search_fields = ("company_name",)

class TenantLanguageAdmin(admin.ModelAdmin):
    """
    Custom admin interface for the TenantLanguages model.
    - list_display: Specifies the fields to display in the admin list view.
    - list_filter: Adds filtering options for the specified fields.
    """
    list_display = ("tenant", "language",)
    list_filter = ("language", "tenant")

admin.site.register(Tenant, TenantAdmin)
admin.site.register(TenantLanguages, TenantLanguageAdmin)
admin.site.register(ContractStatus)
admin.site.register(SubscriptionPlan)


# Tenant Setting Admin Models

admin.site.register(BillingDetails)
admin.site.register(AuditLog)
admin.site.register(SupportCase)