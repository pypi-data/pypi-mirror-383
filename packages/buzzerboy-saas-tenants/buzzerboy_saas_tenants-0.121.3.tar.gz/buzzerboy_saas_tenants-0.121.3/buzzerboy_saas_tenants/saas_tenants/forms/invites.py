from django import forms
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import User
from django.conf import settings

from buzzerboy_saas_tenants.saas_tenants.models.accounts import UserProfile
from buzzerboy_saas_tenants.saas_tenants.models.invites import Invites
from buzzerboy_saas_tenants.core.email_service import EmailService

from buzzerboy_saas_tenants.core import shortcuts as CORE_SHORTCUTS
from buzzerboy_saas_tenants.core.utils import generate_invitation_link


class InvitesForm(forms.ModelForm):
    class Meta:
        model = Invites
        fields = [
            'access_role',
            'email',
            'first_name',
            'last_name',
            'notes',
            'expired_at'
        ]
        widgets = {
            'access_role': forms.Select(attrs={'class': 'form-control', 'placeholder': _('Select Access Role')}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': _('Enter email address') }),
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': _('Enter first name') }),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': _('Enter last name') }),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': _('Enter notes') }),
            'expired_at': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }
        labels = {
            'access_role': _('Access Role'),
            'email': _('Email Address'),
            'first_name': _('First Name'),
            'last_name': _('Last Name'),
            'notes': _('Notes'),
            'expired_at': _('Expiration Date'),
        }

    def __init__(self, *args, **kwargs):
        tenant = kwargs.pop('tenant', None)
        super(InvitesForm, self).__init__(*args, **kwargs)
        self.tenant = tenant  # Store tenant in the form instance

        # Make the template field required
        self.fields['access_role'].required = True
        self.fields['email'].required = True
        self.fields['first_name'].required = True
        self.fields['last_name'].required = True
        self.fields['expired_at'].required = True

    def save(self, commit=True):
        instance = super(InvitesForm, self).save(commit=False)
        invite_exist = Invites.objects.filter(email=instance.email, status='pending').exclude(pk=instance.pk).exists()
        # Ensure that the template and email are unique for the same invite type
        if instance.email:
            if invite_exist:
                raise forms.ValidationError(_("An invite with this email already exists."))

        # Create or get the user based on email
        user, created = User.objects.get_or_create(
            email=self.cleaned_data['email'],
            defaults={
                'username': self.cleaned_data['email'].lower(),
                'first_name': self.cleaned_data['first_name'],
                'last_name': self.cleaned_data['last_name'],
                'is_active': False,
            }
        )

        if hasattr(user, 'profile'):
            profile = user.profile
            # Ensure the profile has a tenant
            if profile.tenant:
                # Check if the tenant of the profile matches the current user's tenant
                if profile.tenant.id == self.tenant.id:
                    raise forms.ValidationError(_("User is already part of the team."))

       
        # Send email based on the selected template
        template = self.tenant.user_invite_template
        subject = self.tenant.user_invite_subject if self.tenant.user_invite_subject else _("Team Member Invitation")
        full_message = f"{template}"
        
        invite_url = generate_invitation_link(user)

        context = {
            'invite_url': invite_url,
        }

        EmailService.send_template_email(full_message, context, subject, settings.DEFAULT_FROM_EMAIL, [self.cleaned_data['email']],)

        # Retrieve or create the UserProfile for the invited user
        profile = CORE_SHORTCUTS.GetUserProfile(user, UserProfile)
        # Update the user_type in UserProfile based on access_role
        if self.cleaned_data['access_role']:
            profile.user_type = self.cleaned_data['access_role']
            profile.tenant = self.tenant
            profile.save()

        # Update tenant in UserProfile if available
        if self.tenant:
            instance.tenant = self.tenant
            profile.tenant = self.tenant
            

        # Save the instance if commit is True
        if commit:
            instance.save()
        return instance
