
from django.shortcuts import render, redirect
from buzzerboy_saas_tenants.core import settings as CORE_SETTINGS
from buzzerboy_saas_tenants.core import shortcuts as CORE_SHORTCUTS
from django.urls import reverse

class ProfileCompletionMiddleware:
    """
    Middleware to ensure users have completed their profile before accessing any other page.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Skip checks for staff/admin users
        # Skip checks for admin paths
        if request.path.startswith('/admin/'):
            return self.get_response(request)
        
        if request.user.is_authenticated and request.session.get('TWO_FACTOR_AUTHENTICATED', False):
            # Replace 'is_profile_complete' with the actual method/property for checking profile status
            if not hasattr(request.user, "profile") or not CORE_SHORTCUTS.is_profile_complete(request.user.profile):
                edit_profile_url = reverse('edit_profile_settings')  # Replace with your profile edit view name
                
                
                # Allow access to the profile edit page and exempted URLs only
                exempt_urls = [
                    edit_profile_url,
                    reverse('logout'),
                    reverse('login'),
                    reverse('password_reset'),
                    
                ]
                
                if request.path not in exempt_urls:
                    return redirect(edit_profile_url)

        response = self.get_response(request)
        return response

class HandleHTTPErrorsMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        
        if CORE_SETTINGS.DEBUG:
            return response

        # Check if the response is a 404
        if response.status_code == 400:
            return self.handle_http_error(request, status_code=response.status_code)

        elif response.status_code == 403:
            return self.handle_http_error(request, status_code=response.status_code)

        elif response.status_code == 404:
            return self.handle_http_error(request, status_code=response.status_code)

        elif response.status_code == 500:
            return self.handle_http_error(request, status_code=response.status_code)
        
        return response

    def handle_http_error(self, request, status_code, message = None):
        # You can customize the response for undefined URLs here


        return render(request, f"pages/states/errors/{status_code}.html", { "message": message}, status=status_code)

      


class OTPVerificationMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # List of URLs that should be accessible without OTP verification
        allowed_urls = [
            reverse('cancel_login'),
            reverse('two_factor_email'),
            reverse('resend_otp'),
            reverse('renew_otp'),
        ]

        if request.user.is_authenticated and request.session.get('OTP_VERIFICATION_REQUIRED', False):
            if not request.session.get('TWO_FACTOR_AUTHENTICATED', False):
                if request.path not in allowed_urls:
                   
                    return redirect('two_factor_email')    
        response = self.get_response(request)
        return response

class RedirectAuthenticatedUserMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # List of URL names to check
        redirect_urls = [
            'login', 
            # 'register', # As Fahad suggested, the Register page can remain accessible to allow registering another user.
            # 'change_password', # Uncommented this to fix issue #704
            'password_reset', 
            'password_reset_done', 
            'password_reset_complete', 
            # 'resend_otp', 
            # 'renew_otp', 
            'sso_login', 
        ]
        
        # Reverse the URLs once and store them in a list
        reversed_urls = [reverse(url) for url in redirect_urls]
        
        # Check if the user is authenticated and the current path is in the reversed_urls
        if request.user.is_authenticated and any(request.path == url for url in reversed_urls):
            return redirect(reverse('home'))  
        
        response = self.get_response(request)
        return response