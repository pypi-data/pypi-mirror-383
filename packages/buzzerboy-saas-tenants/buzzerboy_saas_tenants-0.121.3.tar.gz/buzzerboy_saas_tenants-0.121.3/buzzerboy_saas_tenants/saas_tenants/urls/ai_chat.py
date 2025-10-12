from django.urls import path


from buzzerboy_saas_tenants.saas_tenants.views.ai_chat import (
    create_compliance_framework, 
    list_compliance_frameworks, 
    create_new_ai_chat, 
    get_ai_chats, 
    update_ai_chat, 
    get_ai_chat_response, 
    delete_ai_chat, 
    create_new_chat_interaction,
    stream_chat_interaction
)

# URL Patterns for the application
urlpatterns = [
    # Chat management endpoints
    path('ai_chat/create/', create_new_ai_chat, name='create_new_ai_chat'),
    path('ai_chat/list/', get_ai_chats, name='get_ai_chats'),
    path('ai_chat/update/<uuid:chat_id>/', update_ai_chat, name='update_ai_chat'),
    path('ai_chat/response/<uuid:chat_id>/', get_ai_chat_response, name='get_ai_chat_response'),
    path('ai_chat/delete/<uuid:chat_id>/', delete_ai_chat, name='delete_ai_chat'),

    # Chat interaction endpoint
    path('ai_chat/<uuid:chat_id>/interaction/', create_new_chat_interaction, name='create_new_chat_interaction'),

    # Compliance framework endpoints
    path('ai_chat/frameworks/', list_compliance_frameworks, name='list_compliance_frameworks'),
    path('ai_chat/frameworks/create/', create_compliance_framework, name='create_compliance_framework'),
    path('ai_chat/<uuid:chat_id>/stream/', stream_chat_interaction, name='stream_chat_interaction'), 
]