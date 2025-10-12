# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from django.urls import  path
from buzzerboy_saas_tenants.saas_tenants.views  import invites as invites_views




urlpatterns =[
    path('organization/teams/invite-team-member', invites_views.invite_team_member, name='invite_team_member'),
    path('organization/teams/invites', invites_views.team_invites, name='team_invites'),
    path('invite/<uidb64>/<token>/', invites_views.user_invitation, name='user_invitation'),

    path('team/invites/delete/<str:invite_id>/', invites_views.delete_invite, name='delete_invite'),
    path('team/invites/cancel/<str:invite_id>/', invites_views.cancel_invite, name='cancel_invite'),

]