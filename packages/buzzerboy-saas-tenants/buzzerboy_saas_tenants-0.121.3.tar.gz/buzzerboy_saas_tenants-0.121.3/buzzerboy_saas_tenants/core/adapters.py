

from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.contrib.auth import get_user_model

from django.urls import reverse
from django.contrib import messages
from allauth.exceptions import ImmediateHttpResponse
from django.http import HttpResponseRedirect


User = get_user_model()

class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):
    def pre_social_login(self, request, sociallogin):
        """
        Prevents social login if the email is not associated with an existing user.
        """
        if sociallogin.is_existing:
            # If this social account is already linked, allow login
            return

        # Extract email from social login response
        email = sociallogin.account.extra_data.get('email') or sociallogin.account.extra_data.get('userPrincipalName')
        if not email:
            # Redirect to login page if no email is provided
            messages.error(request, "Social account does not provide an email address.")
            raise ImmediateHttpResponse(HttpResponseRedirect(reverse("login")))

        # Check if a user with this email exists
        try:
            user = User.objects.get(email=str(email).lower())
            # check if the user is active
            if not user.is_active:
                messages.error(request, "Your account is inactive. Please contact support@goironfort.com")
                raise ImmediateHttpResponse(HttpResponseRedirect(reverse("login")))

        except User.DoesNotExist:
            # Redirect to login page if no user with this email exists
            messages.error(request, "No user with this email in registered in the system. If you believe this is an error, please contact support@goironfort.com")
            raise ImmediateHttpResponse(HttpResponseRedirect(reverse("login")))

        # Link the social account to the existing user
        sociallogin.connect(request, user)

    def populate_user(self, request, sociallogin, data):
#         """
#         Set the username to match the email during user creation.
#         """
        user = super().populate_user(request, sociallogin, data)
        user.username = user.email  # Set the username to the email
        return user 