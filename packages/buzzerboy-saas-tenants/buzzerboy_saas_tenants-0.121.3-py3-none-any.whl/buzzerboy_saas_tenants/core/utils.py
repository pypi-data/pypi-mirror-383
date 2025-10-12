# Standard library imports
import os
import json
from pathlib import Path

# Third-party imports
import pandas as pd
import pyotp
import secrets
import string

# Django imports
from django.conf import settings
from django.urls import reverse
from django.utils import timezone
from django.utils.crypto import get_random_string
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode


# Local app imports
from buzzerboy_saas_tenants.saas_tenants.models.accounts import UserProfile
from buzzerboy_saas_tenants.saas_tenants.models.tenant_setting import AuditLog
from buzzerboy_saas_tenants.core import settings as CORE_SETTINGS

from django.utils import timezone

def generate_time_based_otp(secret, interval=30):
    """
    Generates a time-based One-Time Password (TOTP).

    Args:
        secret (str): The shared secret key used to generate the OTP.
        interval (int): The time interval in seconds for which the OTP is valid. Default is 30 seconds.

    Returns:
        str: A TOTP as a string.
    """
    totp = pyotp.TOTP(secret, interval=interval)
    return totp.now() 

def generate_user_token():
    return get_random_string(length=255)  # Adjust length as needed

def create_or_update_user_profile(user):
    profile, created = UserProfile.objects.get_or_create(user_object=user)
    if created or not profile.user_token:
        profile.user_token = generate_user_token()
        profile.save()
    return profile

def generate_invitation_link(user):
    profile = create_or_update_user_profile(user)
    token = profile.user_token
    uid = urlsafe_base64_encode(force_bytes(user.pk))  # Encode user ID
    relative_url = reverse('user_invitation', kwargs={'uidb64': uid, 'token': token})
    full_url = f"{settings.SITE_URL}{relative_url}"  # Prepend domain from settings
    return full_url
    

def save_audit_log(tenant, performed_by, activity, module, details):
    AuditLog.objects.create(tenant=tenant, activity=activity, module=module, details=details, performed_by=performed_by, timestamp=timezone.now())



def create_or_update_user_profile(user):
    profile, created = UserProfile.objects.get_or_create(user_object=user)
    if created or not profile.user_token:
        profile.user_token = generate_user_token()
        profile.save()
    return profile


def get_activation_link(user, request = None):
    profile = create_or_update_user_profile(user)
    token = profile.user_token
    uid = urlsafe_base64_encode(force_bytes(user.pk))  # Encode user ID
    relative_url = reverse('activate_account', kwargs={'uidb64': uid, 'token': token})

    # Use request to determine hostname
    host = request.get_host()
    protocol = 'https' if request.is_secure() else 'http'
    
    full_url = f"{protocol}://{host}{relative_url}"  # Prepend protocol and host
    return full_url

def generate_otp_code(user, request = None):
    secret = CORE_SETTINGS.SECRET_KEY
    profile = create_or_update_user_profile(user)
    otp_code = generate_time_based_otp(secret, 300)

    profile.otp_code = otp_code

    print(f"Generated OTP code: {otp_code}")
    profile.save()

    return otp_code

def load_csv_file(file):
    """
    Load a CSV file and return the data as a list of dictionaries.
    
    Args:
        file (File): The CSV file to load.
    
    Returns:
        list: The data from the CSV file as a list of dictionaries.
    """

    file = Path(__file__).resolve().parent.parent.parent / f'buzzerboy_saas_tenants/{file}'    
    return pd.read_csv(file)

def load_json_file(file):
    """
    Load a JSON file and return the data as a Python object.
    
    Args:
        file (str): The JSON file to load.
    
    Returns:
        dict or list: The data from the JSON file as a Python object.
    """

    file = Path(__file__).resolve().parent.parent / f'fixtures/{file}'
    with open(file, 'r', encoding='utf-8') as f:
        return json.load(f)


def list_all_files(storage, base_path):
    """Recursively list all files under a given base path in the storage."""
    try:
        dirs, files = storage.listdir(base_path)
        all_files = []

        # Add files in the current directory
        for file in files:
            file_path = os.path.join(base_path, file)
            url = storage.url(file_path)
            all_files.append(url)

        # Recursively process subdirectories
        for directory in dirs:
            dir_path = os.path.join(base_path, directory)
            all_files.extend(list_all_files(storage, dir_path))

        return all_files
    except Exception as e:
        print(f"Error listing files in {base_path}: {e}")
        return []
    

def generate_strong_password(length=16, use_special_chars=True):
    """
    Generate a cryptographically secure strong password.
    """
    if length < 8:
        raise ValueError("Password length should be at least 8 characters.")

    alphabet = string.ascii_letters + string.digits
    if use_special_chars:
        alphabet += "!@#$%^&*()-_=+[]{}|;:,.<>?/"

    while True:
        password = ''.join(secrets.choice(alphabet) for _ in range(length))
        if (any(c.islower() for c in password) and
            any(c.isupper() for c in password) and
            any(c.isdigit() for c in password) and
            (not use_special_chars or any(c in "!@#$%^&*()-_=+[]{}|;:,.<>?/" for c in password))):
            return password

