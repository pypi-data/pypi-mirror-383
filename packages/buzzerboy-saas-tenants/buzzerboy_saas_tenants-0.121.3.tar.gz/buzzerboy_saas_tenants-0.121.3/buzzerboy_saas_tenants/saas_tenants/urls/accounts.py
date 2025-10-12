# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from django.urls import  path
from buzzerboy_saas_tenants.saas_tenants.views import accounts as accounts_views




# URL Patterns for the application

urlpatterns =[
    path ('accounts/profile/', accounts_views.profile, name='profile'),
    path('accounts/profile/details', accounts_views.profile, name='profile'),
]
