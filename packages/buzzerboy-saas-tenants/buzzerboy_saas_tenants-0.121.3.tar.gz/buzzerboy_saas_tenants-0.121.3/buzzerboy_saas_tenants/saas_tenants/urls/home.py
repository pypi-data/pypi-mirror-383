# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from django.urls import path
from buzzerboy_saas_tenants.saas_tenants.views import home as home_views

# URL Patterns for the application

urlpatterns =[

    # The home page
    # URL: /
    # View: home_views.index
    # This route directs to the home page of the application.
    path('', home_views.index, name='home'),
]

