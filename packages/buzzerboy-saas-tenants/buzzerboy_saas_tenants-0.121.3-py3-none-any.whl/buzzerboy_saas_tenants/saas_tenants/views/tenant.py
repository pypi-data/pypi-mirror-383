
# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

#DJANGO Imports
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.utils.translation import gettext_lazy as _

from buzzerboy_saas_tenants.saas_tenants.models.accounts import UserProfile
from buzzerboy_saas_tenants.saas_tenants.models.tenant import Tenant

from buzzerboy_saas_tenants.core import shortcuts as CORE_SHORTCUTS
from buzzerboy_saas_tenants.core.middleware import HandleHTTPErrorsMiddleware



middleware = HandleHTTPErrorsMiddleware(get_response=None)

@login_required(login_url="/login/")
def team_member_list(request):
    """
    View function for user profile page.
    Requires the user to be logged in. If the user is not logged in, they will be redirected to the login page.
    Parameters:
    - request: The HTTP request object.
    Returns:
    - HttpResponse: The rendered HTML template for the user profile page.
    """
    
    my_user_profile = CORE_SHORTCUTS.GetUserProfile(request.user, UserProfile)
    tenant = CORE_SHORTCUTS.GetUserTenant(my_user_profile, Tenant)

    try:        
        team_mates = tenant.team.all()    
        context = {
            'title': _("Team"),
            'segment': {
                'text': _("Team Member List"), 
                'url': 'team_member_list'
            }, 
            'team_member_list': team_mates 
        }

        return render(request, 'pages/teams/index.html', context)
    except Exception as e:
        if hasattr(e, 'message'):
            message = str(e.message)
            print(message)
        else:
            message = str(e)
            print(message)
        return middleware.handle_http_error(request, status_code=500, message=message)
