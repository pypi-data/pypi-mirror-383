import uuid

from django.shortcuts import render, redirect
from django.contrib.auth.views import LoginView, PasswordResetView, PasswordChangeView, PasswordResetConfirmView
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import get_user_model
from django.contrib import messages
from django.urls import reverse_lazy, reverse
from django.core.exceptions import ValidationError
from django.template import loader
from django.http import HttpResponse, QueryDict
from django.utils.translation import gettext_lazy as _,activate as activate_language
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode
from django.views.generic import CreateView
from django.contrib.auth import views

from buzzerboy_saas_tenants.core.middleware import HandleHTTPErrorsMiddleware
from buzzerboy_saas_tenants.core import shortcuts as CORE_SHORTCUTS
from buzzerboy_saas_tenants.core import settings as CORE_SETTINGS
from buzzerboy_saas_tenants.core.email_service import EmailService
from buzzerboy_saas_tenants.core.utils import  get_activation_link

from buzzerboy_saas_tenants.saas_tenants.models.accounts import UserProfile, Timezone, SupportedLanguage
from buzzerboy_saas_tenants.saas_tenants.models.authentication import IdentityProvider
from buzzerboy_saas_tenants.saas_tenants.models.tenant  import Tenant

from buzzerboy_saas_tenants.saas_tenants.forms import authentication as forms
from django.contrib.auth import authenticate
middleware = HandleHTTPErrorsMiddleware(get_response=None)
User = get_user_model() # Get the user model from Django's authentication system

# Authentication
class UserLoginView(LoginView):
    """
    Custom login page for users.

    This class handles user login by displaying a login form and processing the user's credentials.
    It extends Django's built-in LoginView, which provides much of the functionality automatically.

    Attributes:
        template_name (str): The path to the HTML template that should be used to display the login form.
        form_class (forms.LoginForm): The form that will be used to collect the user's login details.
    """


    template_name = 'pages/authentication/auth-login-minimal.html'  # Specify the template to use for the login page.
    form_class = forms.LoginForm  # Use the custom LoginForm defined in forms.py.

    def get_success_url(self):
        return reverse('two_factor_email')

    def form_valid(self, form):
        # Call the parent class's form_valid method to log the user in
        response = super().form_valid(form)

        # Set a session flag to indicate that OTP verification is required
        self.request.session['OTP_VERIFICATION_REQUIRED'] = True

        # Send an OTP email after successful login
        user = self.request.user
        profile = user.profile
        
        try:
            if profile.language.language_key:
                activate_language(profile.language.language_key)
            else:
                activate_language('en')
        except Exception as e:
            print(f"Error activating language  {e}")

        # Send the OTP email
        try:
            profile.send_otp_email(subject=_("Your OTP for Login"))
        except Exception as e:
            # Handle potential errors in sending the email
            messages.error(self.request, _("There was an issue sending the OTP email. Please try again."))
            middleware.handle_http_error(self.request, status_code=500, message="There was an issue sending the OTP email. Please try again.")

        return response



# 2FA
@login_required(login_url="/login/")
def two_factor_email_verification(request):
    user_profile = request.user.profile
    if not user_profile.otp_code_secret:
        return redirect('login')

    if request.method == "POST":
        form = forms.OTPVerificationForm(request.POST)
        if form.is_valid():
            otp = form.cleaned_data['otp']
            if not user_profile.is_expired_otp():
                if user_profile.verify_otp(otp):
                    request.session['TWO_FACTOR_AUTHENTICATED'] = True
                    request.session['OTP_VERIFICATION_REQUIRED'] = False

                    user_profile.otp_code = None
                    user_profile.otp_code_secret = None
                    user_profile.otp_generated_at = None
                    user_profile.otp_resend_limit = 3
                    user_profile.save()
                    return redirect('home')
                else:
                    form.add_error(None, 'Invalid OTP. Please try again.')
            else:
                form.add_error(None, 'OTP is expired. Please request new one.')
    else:
        form = forms.OTPVerificationForm()

    context = {
        'form': form,
        'resend_limit': user_profile.otp_resend_limit,
        'is_expired_otp': user_profile.is_expired_otp()
    }
    html_template = loader.get_template('pages/authentication/two-factor-email.html')
    return HttpResponse(html_template.render(context, request))




def logout_view(request):
    """
    Log out the current user.

    This function logs out the user and redirects them to the login page.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: A redirect to the login page.
    """
    logout(request)  # Log out the user.
    return redirect('login')  # Redirect to the login page.



class UserRegisterView(CreateView):
    """
    View for user registration.

    This class allows new users to register by creating a new account.
    It uses a form to collect the necessary details and processes the input to create a new user.

    Attributes:
        form_class (Form): The form class that handles the user's registration input.
        template_name (str): The path to the HTML template for the registration page.
        success_url (str): The URL to redirect the user to after a successful registration.
    """
    form_class = forms.UserRegisterForm
    template_name = 'pages/authentication/register.html'  # Path to your registration template
    success_url = reverse_lazy('login')  # Redirect to the login page after successful registration

    def form_valid(self, form):
        """
        If the form is valid, save the new user and log them in.

        Args:
            form (Form): The valid form instance.

        Returns:
            HttpResponse: A response that redirects the user to the success URL.
        """
        
        tenant_key = form.cleaned_data.get('tenant_key')
        email = form.cleaned_data.get('email')
        email = str(email).lower()

    
        
        tenant_uuid = uuid.UUID(tenant_key) 
        tenant = Tenant.objects.get(uuid=tenant_uuid)  

        # After successful tenant retrieval, save the new user
        
        user = form.save()  # Save the new user
        user.email = email  # Ensure the email is in lowercase
        user.username = email # Set the username to the user's email address
        user.is_active = False  # Deactivate the user until they verify their email
        user.first_name = form.cleaned_data.get('firstname') # Set the user's first name
        user.last_name = form.cleaned_data.get('lastname') # Set the user's last name
        user = form.save()  # update the user object with the new username
        
        user_profile = CORE_SHORTCUTS.GetUserProfile(user, UserProfile)
        timezone = Timezone.objects.get(pk=1)
        default_language = SupportedLanguage.objects.get(pk=1)
        

        user_profile.tenant = tenant
        user_profile.status = UserProfile.UserProfileStatus.DISABLED  
        user_profile.company = tenant.company_name  
        user_profile.address  = tenant.address 
        user_profile.city = tenant.city 
        user_profile.state_province= tenant.state_province  
        user_profile.country = tenant.country 
        user_profile.phone_number = tenant.telephone
        user_profile.postalcode = tenant.postalcode
        user_profile.website = tenant.website
        user_profile.timezone = timezone
        user_profile.language =  default_language


        user_profile.user_token = uuid.uuid4() 
        user_profile.save()

        activation_url = get_activation_link(user, request=self.request)
        
        # Send email based on the selected template
        template = CORE_SHORTCUTS.GetEmailTemplate('account_activation.html', {"activation_url" : activation_url})
        subject = _("Account Activation")
        full_message = f"{template}"


        context = {
            'activation_url': activation_url,
        }

        EmailService.send_template_email(full_message, context, subject, CORE_SETTINGS.DEFAULT_FROM_EMAIL , [email],)

        # Log in the user after registration
        #login(self.request, user)
        messages.success(self.request, _('A confirmation email has been sent to your inbox. Please check your email to activate your account.'))
        return redirect('login')  # Redirect to the success URL

    

class UserPasswordResetView(PasswordResetView):
    """
    Password reset view for users who forgot their password.

    This view displays a form where users can request a password reset email. It extends Django's
    built-in PasswordResetView, which handles the process of sending the reset email.

    Attributes:
        template_name (str): The path to the HTML template that should be used for the password reset form.
        form_class (forms.UserPasswordResetForm): The form class that collects the user's email address.
    """
    template_name = 'accounts/password_reset.html'  # Specify the template to use for the password reset page.
    form_class = forms.UserPasswordResetForm  # Use the custom UserPasswordResetForm.

class UserPasswordResetConfirmView(PasswordResetConfirmView):
    """
    View for setting a new password after receiving a reset link.

    This view is used when the user clicks the link in their password reset email.
    It allows the user to enter a new password.

    Attributes:
        template_name (str): The path to the HTML template for the password reset confirmation page.
        form_class (forms.UserSetPasswordForm): The form used for setting the new password.
    """
    template_name = 'accounts/password_reset_confirm.html'  # Specify the template to use for password reset confirmation.
    form_class = forms.UserSetPasswordForm  # Use the custom UserSetPasswordForm.

class UserPasswordChangeView(LoginRequiredMixin, PasswordChangeView):
    """
    View for changing the user's password.

    This class allows users to change their passwords securely. It ensures that only authenticated users can access this view,
    and handles the entire process of password change, from displaying the form to processing it.

    Attributes:
        template_name (str): The path to the HTML template that will be used to render the password change page.
        form_class (Form): The form class that will handle the user's input for changing the password.
        success_url (str): The URL to redirect the user to after a successful password change. In this case, it redirects back to the same page.
    """

    template_name = 'pages/account_settings/change-password.html'  # Specify the template to use for the password change page.
    form_class = forms.UserPasswordChangeForm  # Use a custom form class for changing the password.
    success_url = reverse_lazy('change_password')  # After a successful password change, redirect back to the same page.

    def get_context_data(self, **kwargs):
        """
        Provides additional context data for rendering the view.

        This method adds extra information to the template's context, such as the page title and whether
        the password was successfully changed, to customize the user experience.

        Args:
            **kwargs: Additional keyword arguments that might be passed to the view.

        Returns:
            dict: A dictionary containing context data for rendering the template.
        """

        context = super().get_context_data(**kwargs)  # Get the default context data from the parent class.
        context['title'] = _('Account Settings')  # Set the title of the page.
        context['segment'] = {'text': _('Change Password'), 'url': 'change_password'}  # Define the current segment of the site.
        context['password_changed'] = 'password_changed' in self.request.GET  # Check if the password was successfully changed.
        return context  # Return the updated context to be used in the template.

    def form_valid(self, form):
        """
        Handles the form submission and processes the password change.

        This method is called when the user submits the password change form. If the form is valid, the password is changed,
        and the user is redirected to the same page with a confirmation message.

        Args:
            form (Form): The form instance that contains the user's input.

        Returns:
            HttpResponse: A response object that redirects the user after a successful password change.
        """
        
        response = super().form_valid(form)  # Call the parent class's form_valid method to handle the password change.
        self.success_url += '?password_changed=True'  # Append a flag to the URL to indicate the password was changed.
        return response  # Return the response to complete the process.

def create_password_invite(request, token):
    try:
        profile = CORE_SHORTCUTS.GetUserProfile(request.user, UserProfile, token)

        form = forms.UserSetPasswordForm(profile.user_object)

        if request.method == 'POST':
            form = forms.UserSetPasswordForm(profile.user_object, request.POST)
            try:
                if form.is_valid():
                    form.save()

                    profile.user_token = None
                    profile.save()
                    
                    print('Your password has been set successfully.')
                    return redirect('password_create_complete')  # Redirect to the login page or another page of your choice
                else:
                    print('There was an error setting your password. Please try again.')
            except ValidationError as e:
                print(f'Error: {", ".join(e.messages)}')
            
        context = {
            'form': form,
            'token': token
        }
        
        return render(request, 'pages/authentication/password-create.html', context)
    
    except Exception as e:
        if hasattr(e, 'message'):
            message = str(e.message)
            print(message)
        else:
            message = str(e)
            print(message)
        return middleware.handle_http_error(request, status_code=500, message=message)


def cancel_login(request):
    """
    Cancel the login process and log out the user.

    This function logs out the user and redirects them to the login page.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: A redirect to the login page.
    """
    if 'TWO_FACTOR_AUTHENTICATED' in request.session:
        del request.session['TWO_FACTOR_AUTHENTICATED']
    logout(request)
    return redirect('login')


def resent_activation_email(request):
    """
    Resend the activation email to the user.

    This function allows users to request a new activation email if they did not receive the initial one.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: A redirect to the login page.
    """

    if request.method == 'POST':
            email = request.POST.get('email')
            user = User.objects.filter(email=email).first()
            if user:
                profile = CORE_SHORTCUTS.GetUserProfile(user, UserProfile)
                if profile.user_token:
                    activation_url = get_activation_link(user, request=request)
                    template = CORE_SHORTCUTS.GetEmailTemplate('account_activation.html', {"activation_url" : activation_url})
                    subject = _("Account Activation")
                    full_message = f"{template}"
                    context = {
                        'activation_url': activation_url,
                    }
                    EmailService.send_template_email(full_message, context, subject, CORE_SETTINGS.DEFAULT_FROM_EMAIL , [email],)
                    messages.success(request, _('A new activation email has been sent to your inbox. Please check your email to activate your account.'))
                else:
                    messages.error(request, _('Your account is already activated. Please login.'))
            else:
                messages.error(request, _('No user found with this email. Please try again.'))
    
    return redirect('login')


def activate_account(request, uidb64, token):
    try:
        # Decode user ID
        uid = force_str(urlsafe_base64_decode(uidb64))
        
        # Fetch the user object
        user = User.objects.get(pk=uid)
        
        # Fetch the user profile
        profile = CORE_SHORTCUTS.GetUserProfile(user, UserProfile)
        
        # Check if the token matches
        if profile.user_token == token:
            # Activate user or perform actions
            user.is_active = True
            user.save()
            
            profile.status = UserProfile.UserProfileStatus.ENABLED
            profile.save()

            messages.success(request, _('Account successfully activated. You can now log in.'))
        else:
            messages.success(request, _('Invalid user token.'))
        
        return redirect('login')
    
    except (TypeError, ValueError, OverflowError, User.DoesNotExist) as e:
        if hasattr(e, 'message'):
            message = str(e.message)
            print(message)
        else:
            message = str(e)
            print(message)

        return middleware.handle_http_error(request, status_code=500, message=message)
    except UserProfile.DoesNotExist:
        print(_("User Profile not exist"))
        return middleware.handle_http_error(request, status_code=500, message=message)

def sso_login(request):
    from buzzerboy_saas_tenants.core.saml_config import get_saml_config
    from django.conf import settings
    from buzzerboy_saas_tenants.main.utils import is_subdomain
    
    """
    Captures the user's company domain and maps it to the appropriate Identity Provider (IdP).
    """
    if request.method == "POST":
        domain = request.POST.get("company_domain")

        if not domain:
            messages.error(request, "Please provide a valid company domain.")
            return redirect("sso_login")

        # Normalize the domain by removing protocol and any trailing slashes
        domain = domain.lower().strip().replace('https://', '').replace('http://', '').rstrip('/')
        
        if is_subdomain(domain):
            extracted_domain = '.'.join(domain.split('.')[-2:])
            idp = IdentityProvider.objects.filter(domain=extracted_domain).first()
        else:
            idp = IdentityProvider.objects.filter(domain=domain).first()

        if not idp:
            messages.error(request, f"No Identity Provider found for the domain: {domain}")
            return redirect("sso_login")

        # Update the SAML configuration with the Identity Provider details
        try:
            requested_host = request.get_host()
            settings.SAML_CONFIG = get_saml_config(idp, domain, requested_host)
            return redirect("saml2_login")  # Redirect to the SAML login view

        except Exception as e:
            messages.error(request, f"An error occurred while setting up SAML for the domain: {domain}. Please contact support.")
            return redirect("sso_login")

    # Render the SSO login page
    context = {}
    html_template = loader.get_template('pages/authentication/sso/sso-login.html')
    return HttpResponse(html_template.render(context, request))


@login_required(login_url="/login/")
def two_factor_email_verification(request):
    user_profile = request.user.profile

    if not user_profile.otp_code_secret:
        return redirect('login')


    if request.method == "POST":
        form = forms.OTPVerificationForm(request.POST)
        if form.is_valid():
            otp = form.cleaned_data['otp']
            if not user_profile.is_expired_otp():
                if user_profile.verify_otp(otp):
                    request.session['TWO_FACTOR_AUTHENTICATED'] = True
                    request.session['OTP_VERIFICATION_REQUIRED'] = False

                    user_profile.otp_code = None
                    user_profile.otp_code_secret = None
                    user_profile.otp_generated_at = None
                    user_profile.otp_resend_limit = 3
                    user_profile.save()

                    print('You have successfully logged in.')
                    return redirect('home')
                else:
                    form.add_error(None, 'Invalid OTP. Please try again.')
            else:
                form.add_error(None, 'OTP is expired. Please request new one.')
    else:
        form = forms.OTPVerificationForm()

    context = {
        'form': form,
        'resend_limit': user_profile.otp_resend_limit,
        'is_expired_otp': user_profile.is_expired_otp()
    }
    html_template = loader.get_template('pages/authentication/two-factor-email.html')
    return HttpResponse(html_template.render(context, request))


def resend_otp(request):
    user_profile = request.user.profile  # Get the user's profile
    print(f"REsending OTP")
    print()
    print()
    print(f"Resend {user_profile.can_resend_otp()   }")
    user_profile.resend_otp(subject="Your OTP for Login")

    if not user_profile.otp_code_secret: # redirect to login if OTP secret is None
        return redirect('login') 

    # Check if the user can resend the OTP
    if user_profile.can_resend_otp():
        try:
            # Send the OTP email
            user_profile.resend_otp(subject="Your OTP for Login")

            messages.success(request, "OTP has been resent successfully. Please check your email.")
        except Exception as e:
            messages.error(request, "There was an issue resending the OTP. Please try again.")
    else:
        # If the OTP cannot be resent, show a message
        if not user_profile.otp_resend_limit:
            messages.error(request, "You have reached the maximum limit for OTP resends.")
        else:
            messages.error(request, "OTP has expired. Please request a new one.")
    
    return redirect("two_factor_email")  # Redirect back to the page where OTP is entered


def renew_otp(request):
    user_profile = request.user.profile  # Get the user's profile
    print(F"Renew OTP")
    if not user_profile.otp_code_secret: # redirect to login if OTP secret is None
        return redirect('login') 

    try:
        # Send the OTP email
        user_profile.send_otp_email(subject="Your OTP for Login")

        messages.success(request, "New OTP has been sent successfully. Please check your email.")
    except Exception as e:
        messages.error(request, "There was an issue creating new OTP. Please try again.")
    
    return redirect("two_factor_email")  # Redirect back to the page where OTP is entered


def redirect_social_login(request):
    """
    Redirects any requests to the default Allauth login page
    to your custom login page.
    """
    return redirect(reverse('login'))


def redirect_social_signup(request):
    """
    Redirects any requests to the default Allauth signup page
    to your custom registration page.
    """
    return redirect(reverse('register'))



class PasswordResetView(views.PasswordResetView):
    """
    Custom Password Reset View
    """
    success_url = reverse_lazy("password_reset_done")

    def form_valid(self, form):
        
        email = form.cleaned_data['email']
        self.request.session['password_reset_email'] = email
        messages.success(self.request, f"Password reset email sent to {email}")
        return super().form_valid(form)


class PasswordResetDoneView(views.PasswordResetDoneView):
    """
    Custom Password Reset Done View
    """
    template_name = 'pages/authentication/password-reset-done.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['password_reset_email'] = self.request.session.get('password_reset_email', '')
        return context