from django import forms
from ckeditor.widgets import CKEditorWidget
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserChangeForm
from django.utils.translation import gettext_lazy as _



from buzzerboy_saas_tenants.saas_tenants.models.accounts import UserProfile, UserType
from buzzerboy_saas_tenants.saas_tenants.models.localization import Country, StateProvince, SupportedLanguage, Timezone

from buzzerboy_saas_tenants.saas_tenants.models.account_settings import (
    NotificationPreferences,
    NotificationChannel,
    NotificationSettings,
    NotificationType,
    CustomTemplate
)


class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = User
        fields = ('email', 'username', 'first_name', 'last_name', )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Disable the email field
        self.fields['email'].disabled = True
        # Hide the password field
        self.fields['password'].widget = forms.HiddenInput()
        self.fields['first_name'].required = True
        self.fields['last_name'].required = True

        # Add 'form-control' class to all fields
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'

class CustomSelectWithIcon(forms.Select):
    """
    Custom select widget that allows adding icons to options.
    """
    def __init__(self, *args, **kwargs):
        self.option_icons = kwargs.pop('option_icons', {})  # Pop the option_icons dictionary from kwargs
        super().__init__(*args, **kwargs)

    def create_option(self, *args, **kwargs):
        """
        Override the create_option method to add data-icon attribute to options.
        """
        option = super().create_option(*args, **kwargs)
        icon = self.option_icons.get(option['value'], '')  # Get icon associated with the option value
        option['attrs']['data-icon'] = icon  # Add icon to the option's attributes
        return option

    def render_option(self, selected_choices, option, index):
        """
        Override render_option to include the icon in the rendered HTML.
        """
        option_html = super().render_option(selected_choices, option, index)
        icon = option['attrs'].get('data-icon', '')
        if icon:
            option_html = option_html.replace(
                f'value="{option["value"]}"',
                f'value="{option["value"]}" data-icon="{icon}"'
            )
        return option_html

class UserProfileForm(forms.ModelForm):
    """
    Form for managing user profile information, including personal details,
    job information, social links, notification preferences, and privacy settings.
    """
    first_name = forms.CharField(max_length=30, required=True, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': _('First Name') }))
    last_name = forms.CharField(max_length=30, required=True, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': _('Last Name')}))

    profile_picture = forms.ImageField(required=False, widget=forms.FileInput(attrs={
        'class': 'file-upload',
        'accept': 'image/*',
        'id': 'profile_picture',
    }))
    phone_number = forms.CharField(max_length=25,  required=True, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': _('Phone Number')}))
    address = forms.CharField(max_length=255, required=False, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': _('Address')}))
    city = forms.CharField(max_length=255, required=True, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': _('City')}))
    state_province = forms.ModelChoiceField(queryset=StateProvince.objects.all(),  required=True, widget=forms.Select(attrs={'class': 'form-control'}))
    postalcode = forms.CharField(max_length=7,  required=True, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': _('Postal Code')}))
    country = forms.ModelChoiceField(queryset=Country.objects.all(),  required=True, widget=forms.Select(attrs={'class': 'form-control',}))
    job_title = forms.CharField(max_length=100,  required=False, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': _('Job Title')}))

    company = forms.CharField(max_length=100, required=False, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': _('Company')}))
    website = forms.URLField(max_length=100, required=False, widget=forms.URLInput(attrs={'class': 'form-control', 'placeholder': _('Website')}))
    linkedin_profile = forms.URLField(max_length=100, required=False, widget=forms.URLInput(attrs={'class': 'form-control', 'placeholder': _('LinkedIn Profile')}))
    github_profile = forms.URLField(max_length=100, required=False, widget=forms.URLInput(attrs={'class': 'form-control', 'placeholder': _('GitHub Profile')}))
    language = forms.ModelChoiceField(queryset=SupportedLanguage.objects.all(), required=False, widget=forms.Select(attrs={'class': 'form-control'}))
    timezone = forms.ModelChoiceField(queryset=Timezone.objects.all(), required=False, widget=forms.Select(attrs={'class': 'form-control'}))

    user_type = forms.ModelChoiceField(queryset=UserType.objects.all(), required=False, widget=forms.Select(attrs={'class': 'form-control'}))

    bio = forms.CharField(required=False, widget=CKEditorWidget())
    interests = forms.CharField(required=False, widget=CKEditorWidget())
    skills = forms.CharField(required=False, widget=CKEditorWidget())
    education = forms.CharField(required=False, widget=CKEditorWidget())
    experience = forms.CharField(required=False, widget=CKEditorWidget())

    # Notification preferences fields
    email_notifications = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}))
    sms_notifications = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}))
    push_notifications = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}))

    
    # Privacy Settings fields
    search_engine_indexing = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}))
    data_sharing = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}))
    profile_visibility = forms.ChoiceField(
        choices=[
            ('public', 'Public'),
            ('friends', 'Friends'),
            ('private', 'Private'),
        ],
        required=True,
        widget=CustomSelectWithIcon(
            option_icons={
                'public': 'feather-globe',
                'friends': 'feather-user',
                'private': 'feather-lock',
            },
            attrs={
                'class': 'form-select form-control fw-12',
                'data-select2-selector': 'visibility'
            }
        )
    )

    class Meta:
        model = UserProfile
        fields = [
            'first_name', 'last_name', 
            'profile_picture', 'profile_picture_as_path', 'phone_number', 'address', 'user_type',
            'city', 'state_province', 'postalcode', 'country', 'job_title', 'company', 'website',
            'linkedin_profile', 'github_profile', 'language', 'timezone',
            'email_notifications', 'sms_notifications', 'push_notifications',
            'profile_visibility', 
            'search_engine_indexing', 'data_sharing',
            'bio', 'interests', 'skills', 'education', 'experience'
        ]
        labels = {
            'first_name': _('First Name'),
            'last_name': _('Last Name'),
            'profile_picture': _('Profile Picture'),
            'phone_number': _('Phone Number'),
            'address': _('Address'),
            'city': _('City'),
            'state_province': _('State/Province'),
            'postalcode': _('Postal Code'),
            'country': _('Country'),
            'job_title': _('Job Title'),
            'company': _('Company'),
            'website': _('Website'),
            'linkedin_profile': _('LinkedIn Profile'),
            'github_profile': _('GitHub Profile'),
            'language': _('Language'),
            'timezone': _('Timezone'),
            'email_notifications': _('Email Notifications'),
            'sms_notifications': _('SMS Notifications'),
            'push_notifications': _('Push Notifications'),
            'profile_visibility': _('Profile Visibility'),
            'search_engine_indexing': _('Search Engine Indexing'),
            'data_sharing': _('Data Sharing'),
            'bio': _('Bio'),
            'interests': _('Interests'),
            'skills': _('Skills'),
            'education': _('Education'),
            'experience': _('Experience'),
        }

    def __init__(self, *args, **kwargs):
        """
        Initialize the form with existing user profile data and preferences.
        """
        super(UserProfileForm, self).__init__(*args, **kwargs)
        
        if self.instance and self.instance.user_object:
            # Populate form fields with existing user data
            self.fields['first_name'].initial = self.instance.user_object.first_name
            self.fields['last_name'].initial = self.instance.user_object.last_name

            # Initialize notification preferences with defaults
            notification_preferences = self.instance.notification_preferences or {
                "sms_notifications": True,
                "push_notifications": True,
                "email_notifications": True
            }
            self.fields['email_notifications'].initial = notification_preferences.get('email_notifications', True)
            self.fields['sms_notifications'].initial = notification_preferences.get('sms_notifications', True)
            self.fields['push_notifications'].initial = notification_preferences.get('push_notifications', True)

            # Initialize privacy settings with defaults
            privacy_settings = self.instance.privacy_settings or {
                "data_sharing": True,
                "profile_visibility": "public",
                "search_engine_indexing": True
            }
            self.fields['profile_visibility'].initial = privacy_settings.get('profile_visibility', 'public')
            self.fields['search_engine_indexing'].initial = privacy_settings.get('search_engine_indexing', True)
            self.fields['data_sharing'].initial = privacy_settings.get('data_sharing', True)
            self.fields['job_title'].required = False

            self.fields['profile_picture_as_path'].widget.attrs['id'] = 'id_logo_as_path'
            print("===================================")
            print(self.fields['profile_picture_as_path'].widget.attrs['id'])
           


    def save(self, commit=True):
        """
        Save the user profile form data to the database.
        """
        user_profile = super(UserProfileForm, self).save(commit=False)
        user = user_profile.user_object
        
        # Save user's first and last name
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']

        # Update Notification Preferences
        user_profile.notification_preferences = {
            'email_notifications': self.cleaned_data['email_notifications'],
            'sms_notifications': self.cleaned_data['sms_notifications'],
            'push_notifications': self.cleaned_data['push_notifications'],
        }

        # Update Privacy Settings
        user_profile.privacy_settings = {
            'profile_visibility': self.cleaned_data['profile_visibility'],
            'search_engine_indexing': self.cleaned_data['search_engine_indexing'],
            'data_sharing': self.cleaned_data['data_sharing'],
        }

        if commit:
            user.save()  # Save the User model
            user_profile.save()  # Save the UserProfile model
        
        return user_profile  # Return the saved UserProfile object

class NotificationPreferencesForm(forms.ModelForm):
    class Meta:
        model = NotificationPreferences
        fields = ['email_notifications', 'sms_notifications', 'push_notifications']
        widgets = {
            'email_notifications': forms.CheckboxInput(),
            'sms_notifications': forms.CheckboxInput(),
            'push_notifications': forms.CheckboxInput(),
        }
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        for field_name, field in self.fields.items():
            if not isinstance(field.widget, (forms.RadioSelect, forms.CheckboxInput)):
                field.widget.attrs['class'] = 'form-control'

class NotificationChannelForm(forms.ModelForm):
    class Meta:
        model = NotificationChannel
        fields = ['email_address', 'phone_number', 'device_token']
        widgets = {
            'email_address': forms.EmailInput(attrs={'placeholder': 'Enter your email'}),
            'phone_number': forms.TextInput(attrs={'placeholder': 'Enter your phone number'}),
            'device_token': forms.TextInput(attrs={'placeholder': 'Enter your device token'}),
        }
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        for field_name, field in self.fields.items():
            if not isinstance(field.widget, (forms.RadioSelect, forms.CheckboxInput)):
                field.widget.attrs['class'] = 'form-control'

class NotificationSettingsForm(forms.ModelForm):
    class Meta:
        model = NotificationSettings
        fields = [
            'frequency',
            'enabled',
            'quiet_hours_start',
            'quiet_hours_end',
            'preferred_language'
        ]
        widgets = {
            'frequency': forms.Select(choices=NotificationSettings._meta.get_field('frequency').choices),
            'enabled': forms.CheckboxInput(),
            'quiet_hours_start': forms.TimeInput(format='%H:%M', attrs={'type': 'time'}),
            'quiet_hours_end': forms.TimeInput(format='%H:%M', attrs={'type': 'time'}),
            'preferred_language': forms.Select(choices=[
                ('en', 'English'),
                ('fr', 'French'),
                # Add more languages as needed
            ]),
        }
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        for field_name, field in self.fields.items():
            if not isinstance(field.widget, (forms.RadioSelect, forms.CheckboxInput)):
                field.widget.attrs['class'] = 'form-control'

class NotificationTypeForm(forms.ModelForm):
    class Meta:
        model = NotificationType
        fields = ['system_alerts', 'promotional_messages', 'user_activity']
        widgets = {
            'system_alerts': forms.CheckboxInput(),
            'promotional_messages': forms.CheckboxInput(),
            'user_activity': forms.CheckboxInput(),
        }
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        for field_name, field in self.fields.items():
            if not isinstance(field.widget, (forms.RadioSelect, forms.CheckboxInput)):
                field.widget.attrs['class'] = 'form-control'

class CustomTemplateForm(forms.ModelForm):
    class Meta:
        model = CustomTemplate
        fields = ['template_name', 'subject', 'body']
        widgets = {
            'template_name': forms.TextInput(attrs={'placeholder': 'Template Name'}),
            'subject': forms.TextInput(attrs={'placeholder': 'Email Subject'}),
            'body': forms.Textarea(attrs={'placeholder': 'Email Body'}),
        }
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        for field_name, field in self.fields.items():
            if not isinstance(field.widget, (forms.RadioSelect, forms.CheckboxInput)):
                field.widget.attrs['class'] = 'form-control'