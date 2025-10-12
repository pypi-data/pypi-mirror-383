import os
import json
from django.core.exceptions import ObjectDoesNotExist

from django.core.management import call_command
from django.core.management import call_command
from django.core.mail import send_mail
from django.template import loader
from pathlib import Path
from django.core.serializers import serialize
from django.forms.models import model_to_dict
from django.conf import settings

from django.contrib.auth import get_user_model
from buzzerboy_saas_tenants.core import settings as CORE_SETTINGS
from buzzerboy_saas_tenants.saas_tenants.models.accounts import UserType

User= get_user_model()

def GetUserProfile(user, UserProfile, token=None, **kwargs):
    """
    Get or create the user profile for the given user and update it with any provided kwargs.
    
    Parameters:
    - user: The user object for which to retrieve or create the profile.
    - UserProfile: The UserProfile model class.
    - kwargs: Additional fields to update in the UserProfile.
    
    Returns:
    - profile: The user profile object.
    
    Comments:
    - This function checks if the given user has a profile attribute. If not, it creates a new profile using the UserProfile model class.
    - Any additional keyword arguments passed to the function are used to update the profile fields.
    - Finally, it returns the user profile object.
    """
    if token:
        profile, created = UserProfile.objects.get_or_create(user_token=token)
    else:
        profile, created = UserProfile.objects.get_or_create(user_object=user)
    
    # Update profile fields based on kwargs
    for key, value in kwargs.items():
        if hasattr(profile, key):
            setattr(profile, key, value)
    if not profile.has_role() or profile.user_object.is_superuser:
        try:
            user_type = UserType.objects.get(pk=1) # 1 == Administrator
        except ObjectDoesNotExist:
            user_type = UserType.objects.create(
                    name_en="Administrator",
                    description_en="Responsible for system management and configuration with full access",
                    has_full_access=True,
                    has_nonstaff_access=True
                )
            
        profile.user_type = user_type
    
    profile.save()

    print(f"Profile Type {profile.user_type}")
    
    return profile

def GetUserTenant(userProfile, Tenant):
    """
    Get the tenant object for the given user.
    
    Parameters:
    - user: The user object for which to retrieve the tenant.
    
    Returns:
    - tenant: The tenant object.
    
    Comments:
    - This function retrieves the tenant object associated with the given user.
    - If the user does not have a tenant, it creates one.
    - Otherwise, it returns the tenant object associated with the user.
    """
    # Update profile fields based on kwargs

    if not userProfile.has_tenant():

        # Check if default tenant is exists
        # Explanation: Since the company name is unique, it might cause constraint errors if not checked.
        try:
            tenant = Tenant.objects.get(company_name="*** TENANT NOT SETUP ***")
        except ObjectDoesNotExist:
            tenant = Tenant.objects.create(
                company_name="*** TENANT NOT SETUP ***",  # Default value
                subdomain=None,                             # Optional
                support_email_address="",                   # Optional
                company_slogan="",                          # Optional
                website=None,                               # Optional
                address=None,                               # Optional
                city=None,                                  # Optional
                postalcode=None,                            # Optional
                state_province=None,                        # Nullable foreign key
                country=None,                               # Nullable foreign key
                telephone="",                               # Optional
                fax="",                                     # Optional
                primary_account_email=None,                 # Nullable
                primary_account_name=None,                  # Nullable
                company_logo=None,                          # Nullable
                beta_features_csv="",                       # Optional
                user_invite_subject="",                     # Optional
                user_invite_template="Please join our team. Click on the link below to create your account. <br><br><a href='{{invite_url}}'>{{invite_url}}</a>",  # Optional
                subscription_plan=1,                     # Nullable foreign key
            )

        
        userProfile.tenant = tenant
        userProfile.save()    

    return userProfile.tenant


def GetPlans(SubscriptionPlan):
    """
    Get the list of subscription plans.

    Parameters:
    - SubscriptionPlan: The SubscriptionPlan model class.
    - plans: The list of subscription plans.
    - fixture_path: The path to the fixture file containing the subscription plans.

    Returns:
    - plans: The list of subscription plans.

    Comments:
    - This function retrieves the list of subscription plans from the database.
    - If no plans are found, it loads the plans from the fixture file.
    - Finally, it returns the list of subscription plans.
    """
    plans = SubscriptionPlan.objects.all()
    if not plans.exists():
        # Load data from fixtures if no plans are found
        fixture_path = os.path.join('fixtures', 'plans.json')
        call_command('loaddata', fixture_path)

    # Fetch the updated list of subscription plans
    plans = SubscriptionPlan.objects.all()

    return plans


def GetEmailTemplate(template_name, variablesDict):
    """
    Get the email template with the given name and replace the variables with the provided values.
    
    Parameters:
    - template_name: The name of the email template file.

    Returns:
    - template: The email template with the variables replaced. 
    """

    filename = os.path.join(settings.BASE_DIR, 'email_templates', template_name)


    #read contents of file name into template
    with open(filename, 'r') as file:
        template = file.read()
        print(template)
        file.close()

    #replace variables in template with values from variablesDict
    for key, value in variablesDict.items():
        template = template.replace('{{'+key+'}}', value.__str__())

    return template

def send_email (subject, message, recipient_list, from_email=CORE_SETTINGS.DEFAULT_FROM_EMAIL, **kwargs):
    """
    Send an email to the specified recipients with the given subject and message.
    
    Parameters:
    - subject: The subject of the email.
    - message: The message content of the email.
    - recipient_list: A list of email addresses to which the email should be sent.
    - from_email: The email address from which the email should be sent.
    - kwargs: Additional keyword arguments to pass to the send_mail function.


    Comments:
    - This function sends an email to the specified recipients with the given subject and message.
    - The from_email parameter specifies the email address from which the email should be sent.
    - Additional keyword arguments can be passed to the send_mail function.
    """

    #send html message
    kwargs['html_message'] = message
    send_mail(subject, message, from_email, recipient_list, **kwargs)


def LoadChoicesFromFile(file_name):
    """
    Load choices from a JSON file and return a list of tuples.

    Args:
    - file_name: The name of the JSON file containing the choices.

    Returns:
    - CHOICES: A list of tuples containing the choices.

    Comments:
    - This function loads choices from a JSON file and returns a list of tuples.
    - The JSON file should contain an array of objects with 'value' and 'label' keys.
    - The 'value' key should contain the value of the choice, and the 'label' key should contain the display label.

    Example JSON file:
    [
        {"value": "1", "label": "Choice 1"},
        {"value": "2", "label": "Choice 2"},
        ...
    ]

    Example usage:
    - CHOICES = LoadChoicesFromFile('choices.json')
    - choice_field = forms.ChoiceField(choices=CHOICES)
        
    """
    CHOICE_FILE = Path(__file__).resolve().parent.parent / f'fixtures/{file_name}.json'
    with open(CHOICE_FILE) as file:
        choice_data = json.load(file)
    CHOICES = [(row['value'], row['label']) for row in choice_data]
    return CHOICES

def generate_object_json(obj):
    """
    Generates JSON representation of a single object.
    
    Args:
        obj: Any Django model instance
        
    Returns:
        str: JSON string representation of the object
    """
    try:
        # Convert model instance to dictionary
        obj_dict = model_to_dict(obj)
        
        # Convert to JSON string, removing metadata fields
        json_data = json.dumps(obj_dict, default=str)
        
        # Parse back to dictionary to modify
        data_dict = json.loads(json_data)
        
        # Remove model and pk [you remove other metadata in here]
        data_dict.pop('model', None)
        data_dict.pop('pk', None)
        
        return json.dumps(data_dict)
    except Exception as e:
        return json.dumps({'error': str(e)})


def get_tenant_users(tenant):
    """
    Get all users associated with a tenant.
    
    Args:
        tenant: Tenant instance
        
    Returns:
        list: List of user instances associated with the tenant
    """

    users = User.objects.filter(profile__tenant=tenant)
    return users


def is_profile_complete(profile):
    """
    Checks if all required fields in the profile are filled.
    """
    required_fields = [
    profile.phone_number,
    profile.address,
    profile.city,
    profile.state_province,
    profile.postalcode,
    profile.country,
    ]

    return all(required_fields)

