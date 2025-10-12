
# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

#DJANGO Imports
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.template import loader
from django.utils.translation import gettext_lazy as _


from buzzerboy_saas_tenants.saas_tenants.models.accounts import UserProfile

from buzzerboy_saas_tenants.saas_tenants.models.tenant import Tenant
from buzzerboy_saas_tenants.saas_tenants.models.analytics import MonthlyAnalytics
from buzzerboy_saas_tenants.core import shortcuts as CORE_SHORTCUTS
from buzzerboy_saas_tenants.core.middleware import HandleHTTPErrorsMiddleware

from buzzerboy_saas_tenants.core.utils import load_csv_file



middleware = HandleHTTPErrorsMiddleware(get_response=None)

# Create your views here.
@login_required(login_url="/login/")
def index(request):
    """
    Render the index page for the home view.
    Parameters:
    - request: The HTTP request object.
    Returns:
    - HttpResponse: The rendered HTML template.
    Raises:
    - None.
    """


    profile = CORE_SHORTCUTS.GetUserProfile(request.user, UserProfile)
    twelve_months = MonthlyAnalytics.get_previous_twelve_months()   
    twelve_months_name = MonthlyAnalytics.get_month_name(twelve_months)
    past_twelve_active_user = MonthlyAnalytics.past_twelve_months_active_users()

    

  
    print(past_twelve_active_user)
    past_active_user = {
        'data': past_twelve_active_user,
        'type': 'bar',
        'name': 'Active Users',
    }
    context = {
        'title': _('Home') 
        ,'segment': {'text': _('Dashboard'), 'url': 'home'},
        'user_analytics': past_active_user,
        'twelve_months': twelve_months_name,
        }
    

    html_template = loader.get_template('pages/index.html')
    return HttpResponse(html_template.render(context, request))
