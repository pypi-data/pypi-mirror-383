
# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""
import uuid

#DJANGO Imports
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.db import transaction, DatabaseError   
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt 
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.http import JsonResponse
import json

# Models
from buzzerboy_saas_tenants.saas_tenants.models.accounts import UserProfile
from buzzerboy_saas_tenants.saas_tenants.models.tenant import SubscriptionPlan, Tenant
from buzzerboy_saas_tenants.saas_tenants.models.tenant_setting import BillingDetails, SupportCase
from buzzerboy_saas_tenants.saas_tenants.models.account_settings import (
    NotificationPreferences,
    NotificationChannel,
    NotificationSettings,
    NotificationType
)

# Forms
from buzzerboy_saas_tenants.saas_tenants.forms.tenant_setting import SupportCaseForm, TenantAddressForm, TenantBillingAndPaymentForm, EmailTemplateForm, TenantForm
from buzzerboy_saas_tenants.saas_tenants.forms.tenant import TenantSubscriptionForm
from buzzerboy_saas_tenants.saas_tenants.forms.account_settings import (
    NotificationPreferencesForm,
    NotificationChannelForm,
    NotificationSettingsForm,
    NotificationTypeForm,
    CustomTemplateForm
)

# Utils
from buzzerboy_saas_tenants.core import shortcuts as CORE_SHORTCUTS
from buzzerboy_saas_tenants.core.middleware import HandleHTTPErrorsMiddleware
from buzzerboy_saas_tenants.core.utils import save_audit_log, generate_strong_password
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _, activate as activate_language
from buzzerboy_saas_tenants.saas_tenants.forms.account_settings  import UserProfileForm

middleware = HandleHTTPErrorsMiddleware(get_response=None)

@login_required(login_url="/login/")
def message_templates(request):
    """
    Render the index page for the home view.
    Parameters:
    - request: The HTTP request object.
    Returns:
    - HttpResponse: The rendered HTML template.
    Raises:
    - None.
    """
    try:
        profile = CORE_SHORTCUTS.GetUserProfile(request.user, UserProfile)
        tenant = CORE_SHORTCUTS.GetUserTenant(profile, Tenant)
        
        if request.method == 'POST':
            form = EmailTemplateForm(request.POST, instance=tenant, user_profile=profile)
            if form.is_valid():
                if form.has_changed():  # Check if any fields have been updated
                    # Get list of changed fields
                    changed_fields = form.changed_data  
                    
                    # Save the updated form
                    form.save()
                    request.session['is_successful'] = True
                    messages.success(request, _("Successfully updated email templates."))

                    save_audit_log(tenant=tenant, activity="Updated message template", module="Message Template", performed_by=profile, details=changed_fields)
                else:
                    messages.info(request, _("No changes detected."))
                
                return redirect(reverse_lazy('message_templates'))
            else:
                messages.error(request, _("Please double-check your inputs. It seems some fields have errors."))
                request.session['is_successful'] = False
                print("Form errors:", form.errors)  # Debug line
        else:
            form = EmailTemplateForm(user_profile=profile, instance=tenant)

        context = {
            'form': form,
            'title': _('Settings'),
            'segment': {'text': _('Message Template'), 'url': 'message_templates'},
        }
        return render(request, 'pages/tenant_settings/message-template.html', context)
    except Exception as e:
        if hasattr(e, 'message'):
            message = str(e.message)
            print(message)
        else:
            message = str(e)
            print(message)
        return middleware.handle_http_error(request, status_code=500, message=message)

@login_required(login_url="/login/")
def subscription_plans(request):
    """
    Render the index page for the home view.
    Parameters:
    - request: The HTTP request object.
    Returns:
    - HttpResponse: The rendered HTML template.
    Raises:
    - None.
    """
    try:
        profile = CORE_SHORTCUTS.GetUserProfile(request.user, UserProfile)
        tenant = CORE_SHORTCUTS.GetUserTenant(profile, Tenant)
        plans = CORE_SHORTCUTS.GetPlans(SubscriptionPlan)
        if request.method == 'POST':
            form = TenantSubscriptionForm(request.POST, instance=tenant)
            context = {
                'form': form,
                'title': _('Settings'),
                'segment': {'text': _('Subscription Plans'), 'url': 'tenant_subscription_plans'},
                "plans": plans
            }
            if form.is_valid():
                if form.has_changed():  # Check if any fields have been updated
                    # Get list of changed fields
                    changed_fields = form.changed_data

                    # Save the updated form
                    form.save()
                    # Set the session flag to True
                    request.session['is_successful'] = True
                    messages.success(request, _("Successfully changed subscription plan."))

                    save_audit_log(tenant=tenant, activity="Updated subscription plan.", module="Subscription Plans", performed_by=profile, details=changed_fields)
                else:
                    messages.info(request, _("No changes detected."))

                return redirect(reverse_lazy('tenant_subscription_plans'))
            else:
                messages.error(request, _("Please double-check your inputs. It seems some fields have errors."))
                print("Form errors:", form.errors)  # Debug line
                return render(request, 'pages/tenant_settings/subscription-plans.html', context)
        else:
            form = TenantSubscriptionForm(instance=tenant)

        context = {
            'form': form,
            'title': _('Settings'),
            'segment': {'text': _('Subscription Plans'), 'url': 'tenant_subscription_plans'},
            "plans": plans,
            "current_plan": tenant.subscription_plan
        }
        return render(request, 'pages/tenant_settings/subscription-plans.html', context)
    except Exception as e:
        if hasattr(e, 'message'):
            message = str(e.message)
            print(message)
        else:
            message = str(e)
            print(message)
        return middleware.handle_http_error(request, status_code=500, message=message)


@login_required(login_url="/login/")
def billing_and_payment(request):
    """
    Render the index page for the home view.
    Parameters:
    - request: The HTTP request object.
    Returns:
    - HttpResponse: The rendered HTML template.
    Raises:
    - None.
    """
    try:
        profile = CORE_SHORTCUTS.GetUserProfile(request.user, UserProfile)
        tenant = CORE_SHORTCUTS.GetUserTenant(profile, Tenant)

        try:
            billing_details = BillingDetails.objects.get(tenant=tenant)
        except ObjectDoesNotExist:
            billing_details = BillingDetails.objects.create(tenant=tenant)

        # Check for the session flag and pass it to the template
        is_successful = request.session.pop('is_successful', False)
        form = TenantBillingAndPaymentForm(request.POST, instance=billing_details)

        if request.method == 'POST':
            context = {
                'form': form,
                'is_successful': is_successful,
                'title': _('Settings'),
                'segment': {'text': _('Billing and Payment'), 'url': 'tenant_billing_and_payment'},
            }
            if form.is_valid():
                if form.has_changed():  # Check if any fields have been updated
                    # Get list of changed fields
                    changed_fields = form.changed_data  
                    
                    # Save the updated form
                    form.save()
                    # Set the session flag to True
                    request.session['is_successful'] = True
                    messages.success(request, _("Successfully updated billing details."))

                    save_audit_log(tenant=tenant, activity="Updated billing details", module="Billing and Payment", performed_by=profile, details=changed_fields)
                else:
                    messages.info(request, _("No changes detected."))

                
                return redirect(reverse_lazy('tenant_billing_and_payment'))
            else:
                messages.error(request, _("Please double-check your inputs. It seems some fields have errors."))
                print("Form errors:", form.errors)  # Debug line
                return render(request, 'pages/tenant_settings/billing-and-payment.html', context)
        else:
            form = TenantBillingAndPaymentForm(instance=billing_details)

        context = {
            'form': form,
            'title': _('Settings'),
                'segment': {'text': _('Billing and Payment'), 'url': 'tenant_billing_and_payment'},
        }
        return render(request, 'pages/tenant_settings/billing-and-payment.html', context)
    except Exception as e:
        if hasattr(e, 'message'):
            message = str(e.message)
            print(message)
        else:
            message = str(e)
            print(message)
        return middleware.handle_http_error(request, status_code=500, message=message)

@login_required(login_url="/login/")
def user_management(request):
    """
    Render the index page for the home view.
    Parameters:
    - request: The HTTP request object.
    Returns:
    - HttpResponse: The rendered HTML template.
    Raises:
    - None.
    """
    try:
        profile = CORE_SHORTCUTS.GetUserProfile(request.user, UserProfile)
        tenant = CORE_SHORTCUTS.GetUserTenant(profile, Tenant)
        team_mates = tenant.team.all() 

        if request.method == 'POST':
            
            form = EmailTemplateForm(request.POST, instance=tenant, user_profile=profile)
            if form.is_valid():
                form.save()
                request.session['is_successful'] = True
                return redirect(reverse_lazy('tenant_user_management'))
            else:
                request.session['is_successful'] = False
                print("Form errors:", form.errors)  # Debug line
        else:
            form = EmailTemplateForm(user_profile=profile, instance=tenant)

        context = {
            'form': form,
            'tenant': tenant,
            'title': _('Settings'),
            'segment': {'text': _('User Management'), 'url': 'tenant_user_management'},
            'team_member_list': team_mates 
        }
        return render(request, 'pages/tenant_settings/user-management/list.html', context)
    except Exception as e:
        if hasattr(e, 'message'):
            message = str(e.message)
            print(message)
        else:
            message = str(e)
            print(message)
        return middleware.handle_http_error(request, status_code=500, message=message)

@login_required(login_url="/login/")
def audit_trail(request):
    """
    Render the index page for the home view.
    Parameters:
    - request: The HTTP request object.
    Returns:
    - HttpResponse: The rendered HTML template.
    Raises:
    - None.
    """
    try:
        profile = CORE_SHORTCUTS.GetUserProfile(request.user, UserProfile)
        tenant = CORE_SHORTCUTS.GetUserTenant(profile, Tenant)
        audit_logs = tenant.tenant_audit_logs.all().order_by('-timestamp')

        if request.method == 'POST':
            form = EmailTemplateForm(request.POST, instance=tenant, user_profile=profile)
            if form.is_valid():
                form.save()
                request.session['is_successful'] = True
                return redirect(reverse_lazy('tenant_audit_trail'))
            else:
                request.session['is_successful'] = False
                print("Form errors:", form.errors)  # Debug line
        else:
            form = EmailTemplateForm(user_profile=profile, instance=tenant)

        context = {
            'form': form,
            'title': _('Settings'),
            'segment': {'text': _('Audit Trail'), 'url': 'tenant_audit_trail'},
            'audit_logs': audit_logs 
        }
        return render(request, 'pages/tenant_settings/audit-trail.html', context)
    except Exception as e:
        if hasattr(e, 'message'):
            message = str(e.message)
            print(message)
        else:
            message = str(e)
            print(message)
        return middleware.handle_http_error(request, status_code=500, message=message)

@login_required(login_url="/login/")
def notifications(request):
    """
    Render the index page for the home view.
    Parameters:
    - request: The HTTP request object.
    Returns:
    - HttpResponse: The rendered HTML template.
    Raises:
    - None.
    """
    try:
        profile = CORE_SHORTCUTS.GetUserProfile(request.user, UserProfile)
        tenant = CORE_SHORTCUTS.GetUserTenant(profile, Tenant)

        # Get or create related objects
        preferences, created = NotificationPreferences.objects.get_or_create(user=request.user)
        channels, created = NotificationChannel.objects.get_or_create(user=request.user)
        settings, created = NotificationSettings.objects.get_or_create(user=request.user)
        types, created = NotificationType.objects.get_or_create(user=request.user)
        
        if request.method == 'POST':
            # Initialize forms with POST data and existing instances
            preferences_form = NotificationPreferencesForm(request.POST, instance=preferences)
            channels_form = NotificationChannelForm(request.POST, instance=channels)
            settings_form = NotificationSettingsForm(request.POST, instance=settings)
            types_form = NotificationTypeForm(request.POST, instance=types)
            
            # For Custom Templates, handle separately if needed
            # For simplicity, we'll assume adding a single template
            custom_template_form = CustomTemplateForm(request.POST)

            if (preferences_form.is_valid() and channels_form.is_valid() and settings_form.is_valid() and types_form.is_valid()):
                if (preferences_form.has_changed() or channels_form.has_changed() or settings_form.has_changed() or types_form.has_changed()):  # Check if any fields have been updated
                    # Get list of changed fields
                    changed_fields = {
                        'preferences': preferences_form.changed_data,
                        'channels': channels_form.changed_data,
                        'settings': settings_form.changed_data,
                        'types': types_form.changed_data
                    }
                    
                    preferences_form.save()
                    channels_form.save()
                    settings_form.save()
                    types_form.save()

                    messages.success(request, 'Your notification settings have been updated.')

                    save_audit_log(tenant=tenant, activity="Modified notification settings", module="Notifications", performed_by=profile, details=changed_fields)
                else:
                    messages.info(request, _("No changes detected."))
                return redirect(reverse_lazy('tenant_notifications'))
            else:
                messages.error(request, 'Please correct the errors below.')
        else:
            # Initialize forms with existing instances
            preferences_form = NotificationPreferencesForm(instance=preferences)
            channels_form = NotificationChannelForm(instance=channels)
            settings_form = NotificationSettingsForm(instance=settings)
            types_form = NotificationTypeForm(instance=types)

        context = {
            'title': _('Settings'),
            'segment': {'text': _('Notifications'), 'url': 'tenant_notifications'},
            'preferences_form': preferences_form,
            'channels_form': channels_form,
            'settings_form': settings_form,
            'types_form': types_form
        }
        return render(request, 'pages/tenant_settings/notifications.html', context)
    except Exception as e:
        if hasattr(e, 'message'):
            message = str(e.message)
            print(message)
        else:
            message = str(e)
            print(message)
        return middleware.handle_http_error(request, status_code=500, message=message)

@login_required(login_url="/login/")
def organization_details(request):
    """
    Render the index page for the home view.
    Parameters:
    - request: The HTTP request object.
    Returns:
    - HttpResponse: The rendered HTML template.
    Raises:
    - None.
    """

    profile = CORE_SHORTCUTS.GetUserProfile(request.user, UserProfile)
    tenant = CORE_SHORTCUTS.GetUserTenant(profile, Tenant)

    # Check for the session flag and pass it to the template
    is_successful = request.session.pop('is_successful', False)
    form = TenantForm(request.POST, request.FILES, instance=tenant)
    address_form = TenantAddressForm(request.POST, instance=tenant)

    if request.method == 'POST':
        context = {
            'form': form,
             'address_form': address_form,
            'is_successful': is_successful,
            'title': _('Settings'),
            'segment': {'text': _('Organization Details'), 'url': 'organization_details'},
        }
        if form.is_valid() and address_form.is_valid():
            if form.has_changed() or address_form.has_changed() :  # Check if any fields have been updated
                # Get list of changed fields
                changed_fields = form.changed_data  
                changed_fields += address_form.changed_data  
                form.save()
                address_form.save()

                # Set the session flag to True
                request.session['is_successful'] = True
                messages.success(request, _("Successfully updated organization details."))

                save_audit_log(tenant=tenant, activity="Updated organization details", module="Organization Details", performed_by=profile, details=changed_fields)
       
            else:
                messages.info(request, _("No changes detected."))
                
            return redirect(reverse_lazy('organization_details'))
        else:
            messages.error(request, _("Please double-check your inputs. It seems some fields have errors."))
            print("Form errors:", form.errors)  # Debug line
            return render(request, 'pages/tenant_settings/organization-details.html', context)
    else:
        form = TenantForm(instance=tenant)
        address_form = TenantAddressForm(instance=tenant)

    context = {
        'form': form,
         'address_form': address_form,
        'title': _('Settings'),
        'segment': {'text': _('Organization Details'), 'url': 'organization_details'},
    }
    return render(request, 'pages/tenant_settings/organization-details.html', context)
   

@login_required(login_url="/login/")
def address(request):
    """
    Render the index page for the home view.
    Parameters:
    - request: The HTTP request object.
    Returns:
    - HttpResponse: The rendered HTML template.
    Raises:
    - None.
    """
    try:
        profile = CORE_SHORTCUTS.GetUserProfile(request.user, UserProfile)
        tenant = CORE_SHORTCUTS.GetUserTenant(profile, Tenant)

        # Check for the session flag and pass it to the template
        is_successful = request.session.pop('is_successful', False)
        form = TenantAddressForm(request.POST, instance=tenant)
     

        if request.method == 'POST':
            context = {
                'form': form,
                
                'is_successful': is_successful,
                'title': _('Settings'),
                'segment': {'text': _('Address'), 'url': 'tenant_address'},
            }
            if form.is_valid():
                if form.has_changed():  # Check if any fields have been updated
                    # Get list of changed fields
                    changed_fields = form.changed_data  
                    
                    # Save the updated form
                    form.save()
                    # Set the session flag to True
                    request.session['is_successful'] = True
                    messages.success(request, _("Successfully updated tenant address."))

                    save_audit_log(tenant=tenant, activity="Updated tenant address", module="Address", performed_by=profile, details=changed_fields)
                else:
                    messages.info(request, _("No changes detected."))
               
                return redirect(reverse_lazy('tenant_address'))
            else:
                messages.error(request, _("Please double-check your inputs. It seems some fields have errors."))
                print("Form errors:", form.errors)  # Debug line
                return render(request, 'pages/tenant_settings/address.html', context)
        else:
            form = TenantAddressForm(instance=tenant)
            

        context = {
            'form': form,
           
            'title': _('Settings'),
            'segment': {'text': _('Address'), 'url': 'tenant_address'},
        }
        return render(request, 'pages/tenant_settings/address.html', context)
    except Exception as e:
        if hasattr(e, 'message'):
            message = str(e.message)
            print(message)
        else:
            message = str(e)
            print(message)
        return middleware.handle_http_error(request, status_code=500, message=message)

@login_required(login_url="/login/")
def support(request):
    """
    Render the index page for the home view.
    Parameters:
    - request: The HTTP request object.
    Returns:
    - HttpResponse: The rendered HTML template.
    Raises:
    - None.
    """
    try:
        profile = CORE_SHORTCUTS.GetUserProfile(request.user, UserProfile)
        tenant = CORE_SHORTCUTS.GetUserTenant(profile, Tenant)
        support_cases = SupportCase.objects.filter(added_by=profile.user_object)
        
        if request.method == 'POST':
            form = SupportCaseForm(request.POST, user_profile=profile)
            if form.is_valid():
                if form.has_changed():  # Check if any fields have been updated
                    # Get list of changed fields
                    changed_fields = form.changed_data  
                    
                    # Save the updated form
                    form.save()
                    # Set the session flag to True
                    request.session['is_successful'] = True
                    messages.success(request, _("Successfully submitted support case."))

                    save_audit_log(tenant=tenant, activity="Submitted support case.", module="Support Case", performed_by=profile, details=changed_fields)
                else:
                    messages.info(request, _("No changes detected."))
                return redirect(reverse_lazy('tenant_support'))
            else:
                request.session['is_successful'] = False
                print("Form errors:", form.errors)  # Debug line
        else:
            form = SupportCaseForm(user_profile=profile)

        context = {
            'form': form,
            'title': _('Settings'),
            'segment': {'text': _('Support Case'), 'url': 'tenant_support'},
            'support_cases': support_cases
        }
        return render(request, 'pages/tenant_settings/support.html', context)
    except Exception as e:
        if hasattr(e, 'message'):
            message = str(e.message)
            print(message)
        else:
            message = str(e)
            print(message)
        return middleware.handle_http_error(request, status_code=500, message=message)




@login_required(login_url="/login/")
def tenant_user_management_userprofile(request, pk, tenant_id=None):
    try:
        
        profile = request.user.profile
        tenant = CORE_SHORTCUTS.GetUserTenant(profile, Tenant)
        
        if tenant_id: 
            tenant = get_object_or_404(Tenant, uuid=tenant_id)

        team_mate = User.objects.get(pk=pk).profile

        context = { 
            'is_diff_tenant': bool(tenant_id),
            'tenant': tenant,
            'title': _('Settings'),
            'parent': {'text': _('User Management'), 'url': 'tenant_user_management'},
            'segment': {'text': _('User Management'), 'url': 'tenant_user_management'},
            'team_mate': team_mate ,
            'profile':  team_mate
        }

        return render(request, 'pages/tenant_settings/user-management/view.html', context)
    
    except Exception as e:
        if hasattr(e, 'message'):
            message = str(e.message)
            print(message)
        else:
            message = str(e)
            print(message)
        return middleware.handle_http_error(request, status_code=500, message=message)

@login_required(login_url="/login/")
def tenant_user_management_edit_userprofile(request, pk, tenant_id=None):
    try:
        user = User.objects.get(pk=pk)
        profile = CORE_SHORTCUTS.GetUserProfile(user , UserProfile)
        tenant = CORE_SHORTCUTS.GetUserTenant(profile, Tenant)
        is_profile_complete = CORE_SHORTCUTS.is_profile_complete(profile)
        
        if request.method == 'POST':
            form = UserProfileForm(request.POST, request.FILES, instance=profile)
            
            context = {
                'form': form,
                'title': _('Account Settings'),
                'segment': {'text': _('User Management'), 'url': 'tenant_user_management'},
                'is_profile_complete': is_profile_complete,
            }
            
            if form.is_valid():
                if form.has_changed():  # Check if any fields have been updated
                    # Get list of changed fields
                    changed_fields = form.changed_data
                
                    if "profile_picture_as_path" in changed_fields:
                        profile.profile_picture = None
                    elif "profile_picture" in changed_fields:
                        profile.profile_picture_as_path = None
                    
                    profile.save()

                    try:
                        activate_language(profile.language.language_key)
                    except Exception as e:
                        print(f"Error activating language {profile.language.language_key}: {e}")
                        
                    form.save()
                    # Set the session flag to True
                    request.session['is_successful'] = True
                    messages.success(request, _("User profile updated successfully."))
                    is_profile_complete = CORE_SHORTCUTS.is_profile_complete(profile)
                    save_audit_log(tenant=tenant, activity="Updated user profile", module="User Profile", performed_by=profile, details=changed_fields)
                else:
                    messages.info(request, _("No changes detected."))
                    
                return redirect(reverse_lazy('tenant_user_management_edit_userprofile_with_tenant', kwargs={'pk': pk,} ))
            else:
                print("Form errors:", form.errors)  
                return render(request, 'pages/tenant_settings/user-management/edit.html', context)
        else:
            form = UserProfileForm(instance=profile)
            context = {
                'form': form,
                'title': _('Account Settings'),
                'segment': {'text': _('User Management'), 'url': 'tenant_user_management'},
                'is_profile_complete': is_profile_complete,
            }

        return render(request, 'pages/tenant_settings/user-management/edit.html', context)
        
    except Exception as e:
        # Initialize a basic context for error cases
        context = {
            'form': UserProfileForm(),  #
            'title': _('Account Settings'),
            'segment': {'text': _('Edit Profile'), 'url': 'edit_profile_settings'},
            'is_profile_complete': False,
        }
        
        if hasattr(e, 'message'):
            message = str(e.message)
        else:
            message = str(e)
        print(f"Error in tenant_user_management_edit_userprofile: {message}")
        
       
        messages.error(request, _("An error occurred while processing your request."))
        
        return render(request, 'pages/tenant_settings/user-management/edit.html', context)
                   

@login_required(login_url="/login/")
def deactivate_user_management(request, pk):
    try:
 
        user_profile = get_object_or_404(UserProfile, pk=pk)
        user = user_profile.user_object

 
        with transaction.atomic():
            user.is_active = False
            user.save()

            user_profile.status = UserProfile.UserProfileStatus.DISABLED
            user_profile.save()
            
    except DatabaseError:
        print(request, _('An error occurred while trying to deactivate the user account. Please try again later.'))
    except Exception as e:
        print(request, f'An unexpected error occurred: {e}')
    return redirect('tenant_user_management')

@login_required(login_url="/login/")
def activate_user_management(request, pk):
    try:
  
        user_profile = get_object_or_404(UserProfile, pk=pk)
        user = user_profile.user_object


        with transaction.atomic():
            user.is_active = True
            user.save()

            user_profile.status = UserProfile.UserProfileStatus.ENABLED
            user_profile.save()
            
    except DatabaseError:
        print(request, _('An error occurred while trying to activate the user account. Please try again later.'))
    except Exception as e:
        print(request, f'An unexpected error occurred: {e}')
    return redirect('tenant_user_management')




@require_POST
@csrf_exempt
def user_management_reset_user_password(request):
    # try:
   

    data = json.loads(request.body)
    identifier = data.get("id")

    if not identifier:
        return JsonResponse({"success": False, "message": "Invalid User ID."}, status=400)

    try:
        user = User.objects.get(id=identifier)
    except ObjectDoesNotExist:
        raise ValueError("User not found.")

    new_password = generate_strong_password()
    user.set_password(new_password)
    user.save()

    return JsonResponse({
        "success": True,
        "message": f"Password reset for user: {user.username}.",
        "new_password": new_password
    })

    # except ValueError as e:
    #     return JsonResponse({"success": False, "message": str(e)}, status=404)
    # except Exception as e:
    #     return JsonResponse({"success": False, "message": "Internal server error."}, status=500)
