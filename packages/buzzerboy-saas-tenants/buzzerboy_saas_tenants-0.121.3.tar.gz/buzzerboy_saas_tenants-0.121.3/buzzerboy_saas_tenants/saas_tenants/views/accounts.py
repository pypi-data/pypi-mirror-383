
# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.template import loader

from buzzerboy_saas_tenants.saas_tenants.models.accounts import UserProfile, Tenant
from buzzerboy_saas_tenants.core import shortcuts as CORE_SHORTCUTS
from buzzerboy_saas_tenants.core.middleware import HandleHTTPErrorsMiddleware

from django.utils.translation import gettext_lazy as _


middleware = HandleHTTPErrorsMiddleware(get_response=None)

@login_required(login_url="/login/")
def profile(request):
    """
    View function for user profile page.
    Requires the user to be logged in. If the user is not logged in, they will be redirected to the login page.
    Parameters:
    - request: The HTTP request object.
    Returns:
    - HttpResponse: The rendered HTML template for the user profile page.
    """
    try:
        profile = CORE_SHORTCUTS.GetUserProfile(request.user, UserProfile)
        tenant = CORE_SHORTCUTS.GetUserTenant(profile, Tenant)

        context = {'title': _('Profile') ,'segment': {'text': _('Profile Details'), 'url': 'profile'}, 'profile': profile}

        html_template = loader.get_template('pages/accounts/index.html')
        return HttpResponse(html_template.render(context, request))
    
    except Exception as e:
        if hasattr(e, 'message'):
            message = str(e.message)
            print(message)
        else:
            message = str(e)
            print(message)
        return middleware.handle_http_error(request, status_code=500, message=message)
