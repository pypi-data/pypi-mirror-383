from django import forms
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from ckeditor.widgets import CKEditorWidget

from buzzerboy_saas_tenants.saas_tenants.models.tenant import Tenant
from buzzerboy_saas_tenants.saas_tenants.models.tenant_setting import BillingDetails, SupportCase






class EmailTemplateForm(forms.ModelForm):
    
    user_invite_template = forms.CharField(
        widget=CKEditorWidget(),
        required=True  # Make the body field required
    )
    user_invite_subject = forms.CharField(
        required=True, 
        widget=forms.TextInput(attrs={'maxlength': 255, "placeholder": _("Enter Subject Title")})
    )

    class Meta:
        model = Tenant
        fields = [
            'user_invite_subject',
            'user_invite_template',
        ]
        labels = {
            'user_invite_subject': _('Invite Email Subject'),
            'user_invite_template': _('Invite Email Template'),
        }

    def __init__(self, *args, **kwargs):
        self.user_profile = kwargs.pop('user_profile', None)  # Extract 'user_profile' from kwargs if present
        super().__init__(*args, **kwargs)
        
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'

        if self.instance:
            self.fields['user_invite_subject'].initial = self.instance.user_invite_subject
            self.fields['user_invite_template'].initial = self.instance.user_invite_template

    def save(self, commit=True):
        instance = super().save(commit=False)

        # Use cleaned_data to access form values
        instance.user_invite_template = self.cleaned_data['user_invite_template']
        instance.user_invite_subject = self.cleaned_data['user_invite_subject']

        if self.user_profile:
            instance.last_updated_by = self.user_profile.user_object  # Set the user who added this instance
        if not instance.pk:
            instance.last_updated = timezone.now()  # Set created timestamp if it's a new instance
        if commit:
            instance.save()
        return instance

class TenantForm(forms.ModelForm):
    company_logo = forms.ImageField(required=False, widget=forms.FileInput(attrs={
        'class': 'file-upload',
        'accept': 'image/*',
        'id': 'company_logo',
    }))
   

    class Meta:
        model = Tenant
        fields = [
            'company_name', 'subdomain', 'support_email_address', 
            'company_slogan', 'website', 'telephone', 'fax', 'contract_status', 
            'primary_account_email', 'primary_account_name', 'company_logo', 
            'beta_features_csv', 'uuid'
        ]
      
        widgets = {
            'company_slogan': forms.Textarea(attrs={'rows': 3}),
            'address': forms.TextInput(attrs={'placeholder': '123 Main St'}),
        }
        labels = {
            'company_name': _('Company Name'),
            'subdomain': _('Subdomain'),
            'support_email_address': _('Support Email'),
            'company_slogan': _('Company Slogan'),
            'website': _('Website URL'),
            'telephone': _('Telephone'),
            'fax': _('Fax'),
            'contract_status': _('Contract Status'),
            'primary_account_email': _('Primary Account Email'),
            'primary_account_name': _('Primary Account Name'),
            'company_logo': _('Company Logo'),
            'beta_features_csv': _('Beta Features (CSV)'),
        }
        

    def __init__(self, *args, **kwargs):
        super(TenantForm, self).__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
          
            field.widget.attrs['placeholder'] = field.label  


    def clean_subdomain(self):
        subdomain = self.cleaned_data.get('subdomain')
        
        if subdomain and not subdomain.isalnum():
            raise forms.ValidationError(_("Subdomain can only contain letters and numbers."))
        return subdomain

class TenantAddressForm(forms.ModelForm):
    class Meta:
        model = Tenant
        fields = [
            'address', 'city', 'postalcode', 'state_province', 'country'
        ]
        widgets = {
            'company_slogan': forms.Textarea(attrs={'rows': 3}),
            'address': forms.TextInput(attrs={'placeholder': '123 Main St'}),
        }
        labels = {
            'address': _('Company Address'),
            'city': _('City'),
            'postalcode': _('Postal Code'),
            'state_province': _('State/Province'),
            'country': _('Country')
        }
        
    def __init__(self, *args, **kwargs):
        super(TenantAddressForm, self).__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
            # field.required = True  # Make all fields required
            field.widget.attrs['placeholder'] = field.label  # Add placeholder with field label


class TenantBillingAndPaymentForm(forms.ModelForm):
    class Meta:
        model = BillingDetails
        fields = [
            'billing_contact_name', 'billing_contact_address', 
            'billing_contact_city', 'billing_contact_postalcode', 
            'billing_contact_country', 'billing_contact_state_province', 
            'billing_contact_email', 'billing_contact_telephone', 
        ]
        labels = {
            'billing_contact_name': _('Billing Contact Name'),
            'billing_contact_address': _('Billing Contact Address'),
            'billing_contact_city': _('Billing Contact City'),
            'billing_contact_postalcode': _('Billing Contact Postal Code'),
            'billing_contact_country': _('Billing Contact Country'),
            'billing_contact_state_province': _('Billing Contact State/Province'),
            'billing_contact_email': _('Billing Contact Email'),
            'billing_contact_telephone': _('Billing Contact Telephone'),
        }
        

    def __init__(self, *args, **kwargs):
        super(TenantBillingAndPaymentForm, self).__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
            # field.required = True  # Make all fields required
            field.widget.attrs['placeholder'] = field.label  # Add placeholder with field label


class SupportCaseForm(forms.ModelForm):
    class Meta:
        model = SupportCase
        fields = ['request_type', 'summary', 'detailed_description']

    # Define explicit form fields
    request_type = forms.ChoiceField(choices=SupportCase.REQUEST_TYPE_CHOICES, label="Request Type")
    summary = forms.CharField(max_length=255, label="Summary", widget=forms.TextInput(attrs={'placeholder': 'Enter a brief summary'}))
    detailed_description = forms.CharField(widget=forms.Textarea(attrs={'placeholder': 'Provide a detailed description of the issue or request'}), label="Detailed Description")

    def __init__(self, *args, **kwargs):
        self.user_profile = kwargs.pop('user_profile', None)  # Extract 'user_profile' from kwargs if present
        super().__init__(*args, **kwargs)
        
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'

    def save(self, commit=True):
        instance = super().save(commit=False)

        if self.user_profile:
            instance.added_by = self.user_profile.user_object  # Set the user who added this instance
        if commit:
            instance.save()
        return instance
