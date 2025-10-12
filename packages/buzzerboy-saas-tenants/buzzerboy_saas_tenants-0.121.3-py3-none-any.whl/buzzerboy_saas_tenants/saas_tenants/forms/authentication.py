from django import forms
import uuid

from django.contrib.auth.forms import (
    UserCreationForm, 
    AuthenticationForm, 
    PasswordChangeForm, 
    UsernameField, 
    PasswordResetForm, 
    SetPasswordForm
)
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError

from buzzerboy_saas_tenants.saas_tenants.models.accounts import UserProfile
from buzzerboy_saas_tenants.saas_tenants.models.tenant import Tenant
from buzzerboy_saas_tenants.core import shortcuts as CORE_SHORTCUTS


class CustomAuthenticationForm(AuthenticationForm):

    def confirm_login_allowed(self, user):
        """
        Controls whether the given User may log in. This is a policy setting,
        independent of end-user authentication. This default behavior is to
        allow login by active users, and reject login by inactive users.

        If the given user cannot log in, this method should raise a
        ``ValidationError``.

        If the given user may log in, this method should return None.
        """

        user_profile = CORE_SHORTCUTS.GetUserProfile(user, UserProfile)
        if not user.is_active:
            # checks if the inactive user has a user_token which means the user has not activated their account
            if user_profile.user_token:
                raise ValidationError(
                    self.error_messages['not_activated'],
                    code='not_activated',
                )
            else:
                raise ValidationError(
                    self.error_messages["inactive"],
                    code="inactive",
                )

class LoginForm(CustomAuthenticationForm):
    """
    Custom login form that extends Django's built-in AuthenticationForm.
    
    Fields:
        - username: A text field for the user's username.
        - password: A password field for the user's password.
    """
    error_messages = {
        'invalid_login': _(
            "Please enter a correct %(username)s and password. Note that both "
            "fields may be case-sensitive."
        ),
        'inactive': _("Your account has not yet been activated."),
        'not_activated': _("Your account is not activated. Please check your email to activate your account."),
    }

    username = UsernameField(
        label=_("Username"),
        widget=forms.TextInput(attrs={
            "class": "form-control", 
            "placeholder": _("Username")
        })
    )
    # Username field uses a text input with Bootstrap styling and a placeholder.

    password = forms.CharField(
        label=_("Password"),
        strip=False,
        widget=forms.PasswordInput(attrs={
            "class": "form-control", 
            "placeholder": _("Password")
        }),
    )
    # Password field uses a password input, which hides the text for security.
    # The "strip" argument is set to False to preserve any whitespace in the password.

class UserPasswordResetForm(PasswordResetForm):
    """
    Custom password reset form that extends Django's built-in PasswordResetForm.
    
    Fields:
        - email: An email field for the user to enter their registered email address.
    """
    
    email = forms.EmailField(
        label=_("Email"),
        widget=forms.EmailInput(attrs={
            'class': 'form-control', 
            'placeholder': _('Email address')
        })
    )
    # Email field uses an email input with Bootstrap styling and a placeholder.
    # This form will send an email with a password reset link to the user.

class UserSetPasswordForm(SetPasswordForm):
    """
    Custom set password form that extends Django's built-in SetPasswordForm.
    
    Fields:
        - new_password1: A password field for the user to enter their new password.
        - new_password2: A password field for the user to confirm their new password.
    """
    
    new_password1 = forms.CharField(
        max_length=50,
        required=True,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control', 
            'placeholder': _('Confirm New Password')
        }),
        label=_("New Password")
    )
    new_password2 = forms.CharField(
        max_length=50,
        required=True,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control', 
            'placeholder': _('Confirm New Password')
        }),
        label=_("Confirm New Password")
    )

    def clean(self):
        cleaned_data = super().clean()
        new_password1 = cleaned_data.get("new_password1")
        new_password2 = cleaned_data.get("new_password2")

        if new_password1 and new_password2 and new_password1 != new_password2:
            raise forms.ValidationError(_("The two password fields must match."))

        return cleaned_data

class UserPasswordChangeForm(PasswordChangeForm):
    """
    Custom password change form that extends Django's built-in PasswordChangeForm.
    
    Fields:
        - old_password: A password field for the user to enter their current password.
        - new_password1: A password field for the user to enter their new password.
        - new_password2: A password field for the user to confirm their new password.
    """
    
    old_password = forms.CharField(
        max_length=50,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control', 
            'placeholder': _('Old Password')
        }),
        label=_('Old Password'),
        required=True
    )
    # Old password field for the user to enter their current password.
    # This is required to verify the user's identity before changing the password.

    new_password1 = forms.CharField(
        max_length=50,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control', 
            'placeholder': _('New Password')
        }),
        label=_("New Password"),
        required=True
    )
    # New password field, similar to the set password form, but for users changing their password.

    new_password2 = forms.CharField(
        max_length=50,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control', 
            'placeholder': _('Confirm New Password')
        }),
        label=_("Confirm New Password"),
        required=True
    )
    # Confirmation password field to ensure the new password was entered correctly.

class UserRegisterForm(UserCreationForm):
    """
    Custom registration form that extends Django's built-in UserCreationForm.
    
    Fields:
        - username: A text field for the user's username.
        - email: An email field for the user's email address.
        - password1: A password field for the user's password.
        - password2: A password field to confirm the user's password.
    """
    tenant_key = forms.CharField(
        label=_("Tenant Key"),
        widget=forms.TextInput(attrs={
            "class": "form-control", 
            "placeholder": _("Enter Tenant Key")
        })
    )

    firstname = forms.CharField(
        label=_("First Name"),
        widget=forms.TextInput(attrs={
            "class": "form-control", 
            "placeholder": _("First Name")
        })
    )

    lastname = forms.CharField(
        label=_("Last Name"),
        widget=forms.TextInput(attrs={
            "class": "form-control", 
            "placeholder": _("Last Name")
        })
    )
    
    email = forms.EmailField(
        label=_("Email"),
        widget=forms.EmailInput(attrs={
            'class': 'form-control', 
            'placeholder': _('Email address')
        })
    )
    password1 = forms.CharField(
        label=_("Password"),
        strip=False,
        widget=forms.PasswordInput(attrs={
            "class": "form-control", 
            "placeholder": _("Password")
        }),
    )
    password2 = forms.CharField(
        label=_("Confirm Password"),
        strip=False,
        widget=forms.PasswordInput(attrs={
            "class": "form-control", 
            "placeholder": _("Confirm Password")
        }),
    )

    class Meta:
        model = User
        fields = ['firstname', 'lastname', 'email', 'password1', 'password2']
    
    def clean_email(self):
        """Validate email uniqueness"""
        email = self.cleaned_data.get('email')
        if email:
            email = email.lower()
            if User.objects.filter(email=email).exists():
                raise forms.ValidationError(_('A user with this email already exists. Please use a different email.'))
        return email
    
    def clean_tenant_key(self):
        """Validate tenant key"""
        tenant_key = self.cleaned_data.get('tenant_key')
        if tenant_key:
            try:
                tenant_uuid = uuid.UUID(tenant_key)
                tenant = Tenant.objects.get(uuid=tenant_uuid)
                # Store the tenant for later use in form_valid
                self.tenant = tenant
                return tenant_key
            except (ValueError, Tenant.DoesNotExist):
                raise forms.ValidationError(_('Invalid tenant key. Please provide a valid tenant key.'))
        return tenant_key
    
  
    

class OTPVerificationForm(forms.Form):
    otp_1 = forms.CharField(max_length=1, widget=forms.NumberInput(attrs={'id': 'first', 'class': 'm-2 text-center form-control rounded', 'maxlength': '1', 'required': 'true', 'autocomplete': 'off'}))
    otp_2 = forms.CharField(max_length=1, widget=forms.NumberInput(attrs={'id': 'second', 'class': 'm-2 text-center form-control rounded', 'maxlength': '1', 'required': 'true', 'autocomplete': 'off'}))
    otp_3 = forms.CharField(max_length=1, widget=forms.NumberInput(attrs={'id': 'third', 'class': 'm-2 text-center form-control rounded', 'maxlength': '1', 'required': 'true', 'autocomplete': 'off'}))
    otp_4 = forms.CharField(max_length=1, widget=forms.NumberInput(attrs={'id': 'fourth', 'class': 'm-2 text-center form-control rounded', 'maxlength': '1', 'required': 'true', 'autocomplete': 'off'}))
    otp_5 = forms.CharField(max_length=1, widget=forms.NumberInput(attrs={'id': 'fifth', 'class': 'm-2 text-center form-control rounded', 'maxlength': '1', 'required': 'true', 'autocomplete': 'off'}))
    otp_6 = forms.CharField(max_length=1, widget=forms.NumberInput(attrs={'id': 'sixth', 'class': 'm-2 text-center form-control rounded', 'maxlength': '1', 'required': 'true', 'autocomplete': 'off'}))

    def clean(self):
        cleaned_data = super().clean()
        otp = ''.join([cleaned_data.get(f'otp_{i}') for i in range(1, 7)])
        cleaned_data['otp'] = otp  # Combine the OTP digits into one field
        return cleaned_data