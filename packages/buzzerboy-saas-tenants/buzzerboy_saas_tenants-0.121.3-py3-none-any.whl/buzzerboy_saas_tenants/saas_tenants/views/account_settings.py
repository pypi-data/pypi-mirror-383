
# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

#DJANGO Imports

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import PasswordChangeView
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _, activate as activate_language


from buzzerboy_saas_tenants.saas_tenants.models.accounts  import UserProfile
from buzzerboy_saas_tenants.saas_tenants.models.tenant import Tenant


from buzzerboy_saas_tenants.saas_tenants.forms.account_settings  import CustomUserChangeForm, UserProfileForm
from buzzerboy_saas_tenants.saas_tenants.forms import authentication as AUTH_FORMS

from buzzerboy_saas_tenants.core import shortcuts as CORE_SHORTCUTS
from buzzerboy_saas_tenants.core.middleware import HandleHTTPErrorsMiddleware
from buzzerboy_saas_tenants.core.utils import save_audit_log


middleware = HandleHTTPErrorsMiddleware(get_response=None)
# Create your views here.
@login_required(login_url="/login/")
def edit_profile_settings(request):
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
        form = UserProfileForm(request.POST, request.FILES, instance=profile)
        is_profile_complete = CORE_SHORTCUTS.is_profile_complete(profile)
       
        if request.method == 'POST':
            context = {
                'form': form,
                'title': _('Account Settings'),
                'segment': {'text': _('Edit Profile'), 'url': 'edit_profile_settings'},
               
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
                        if profile.language and profile.language.language_key:
                            activate_language(profile.language.language_key)
                    except Exception as e:
                        print(f"Error activating language {profile.language.language_key}: {e}")
                        
                    # Save the updated form
                    form.save()
                    # Set the session flag to True
                    request.session['is_successful'] = True
                    messages.success(request, _("User profile updated successfully."))
                    is_profile_complete = CORE_SHORTCUTS.is_profile_complete(profile)
                    save_audit_log(tenant=tenant, activity="Updated user profile", module="User Profile", performed_by=profile, details=changed_fields)
                else:
                    messages.info(request, _("No changes detected."))
                    
                return redirect(reverse_lazy('edit_profile_settings'))
            else:
                print("Form errors:", form.errors)  # Debug line
                return render(request, 'pages/accounts/edit-profile.html', context)
        else:
            form = UserProfileForm(instance=profile)

        context = {
            'form': form,
            'title': _('Account Settings'),
            'segment': {'text': _('Edit Profile'), 'url': 'edit_profile_settings'},
            'is_profile_complete': is_profile_complete,
        }
        return render(request, 'pages/account_settings/edit-profile.html', context)
    except Exception as e:
        if hasattr(e, 'message'):
            message = str(e.message)
            print(message)
        else:
            message = str(e)
            print(message)
        return middleware.handle_http_error(request, status_code=500, message=message)


@login_required(login_url="/login/")
def user_information(request):
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
            form = CustomUserChangeForm(request.POST, instance=request.user)
            if form.is_valid():
                if form.has_changed():  # Check if any fields have been updated
                    # Get list of changed fields
                    changed_fields = form.changed_data  
                    
                    # Save the updated form
                    form.save()
                    messages.success(request, _("Successfully updated user information."))

                    save_audit_log(tenant=tenant, activity="Updated user information", module="User Information", performed_by=profile, details=changed_fields)
                else:
                    messages.info(request, _("No changes detected."))

                return redirect(reverse_lazy('user_information'))  # Replace 'profile' with your desired redirect URL
            else:
                request.session['is_successful'] = False
                print("Form errors:", form.errors)  # Debug line
        else:
            form = CustomUserChangeForm(instance=request.user)


        context = {
            'form': form,
            'title': _('Account Settings'),
            'segment': {'text': _('User Information'), 'url': 'user_information'},
        }

        return render(request, 'pages/account_settings/user-info.html', context)
    except Exception as e:
        if hasattr(e, 'message'):
            message = str(e.message)
            print(message)
        else:
            message = str(e)
            print(message)
        return middleware.handle_http_error(request, status_code=500, message=message)


class UserPasswordChangeView(LoginRequiredMixin, PasswordChangeView):
    """
    View for changing the user's password.
    Inherits from LoginRequiredMixin and PasswordChangeView.
    Attributes:
        template_name (str): The name of the template to be rendered.
        form_class (Form): The form class to be used for password change.
        success_url (str): The URL to redirect to after successful password change.
    Methods:
        get_context_data(**kwargs): Returns the context data for rendering the template.
        form_valid(form): Handles the form submission and updates the session variable.
    """

    template_name = 'pages/account_settings/change-password.html'
    form_class = AUTH_FORMS.UserPasswordChangeForm
    success_url = reverse_lazy('change_password')
  
    def get_context_data(self, **kwargs):
        """
        Returns the context data for rendering the template.
        Args:
            **kwargs: Additional keyword arguments.
        Returns:
            dict: The context data.
        """
        context = super().get_context_data(**kwargs)
        context['password_changed'] = self.request.session.pop('password_changed', False)
        context['title'] = _('Account Settings')
        context['segment'] = {'text': _('Change Password'), 'url': 'change_password'}

        # Retrieve profile and tenant
        profile = CORE_SHORTCUTS.GetUserProfile(self.request.user, UserProfile)
        tenant = CORE_SHORTCUTS.GetUserTenant(profile, Tenant)
        context['profile'] = profile
        context['tenant'] = tenant
        print("helllo =================")
        return context

    def form_valid(self, form):
        """
        Handles the form submission and updates the session variable.
        Args:
            form (Form): The form instance.
        Returns:
            HttpResponseRedirect: The HTTP response redirecting to the success URL.
        """
        profile = CORE_SHORTCUTS.GetUserProfile(self.request.user, UserProfile)
        tenant = CORE_SHORTCUTS.GetUserTenant(profile, Tenant)

        if form.has_changed():  # Check if any fields have been updated
            # Get list of changed fields
            changed_fields = form.changed_data  
            
            # Save the updated form
            form.save()
            
            # Add success message
            messages.success(self.request, _("Password successfully changed."))
            
            # Log the audit
            save_audit_log(tenant=tenant, activity="Changed user password", module="Change Password", performed_by=profile, details=changed_fields)
        else:
            messages.info(self.request, _("No changes detected."))

        self.request.session['password_changed'] = True
        return super().form_valid(form)