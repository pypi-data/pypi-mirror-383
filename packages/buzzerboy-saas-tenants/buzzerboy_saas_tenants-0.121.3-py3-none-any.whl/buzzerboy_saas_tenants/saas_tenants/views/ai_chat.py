import json
from django.utils.translation import gettext as _
from django.http import JsonResponse, StreamingHttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from buzzerboy_saas_tenants.saas_tenants.models.ai_chat import AIChat, ComplianceFramework


from buzzerboy_saas_tenants.saas_tenants.models import UserProfile
from buzzerboy_saas_tenants.saas_tenants.models import Tenant
from buzzerboy_saas_tenants.core import shortcuts as CORE_SHORTCUTS

# Chat Management Views
def create_new_ai_chat(request):
    """Creates a new AI chat instance for the authenticated user."""
    profile = CORE_SHORTCUTS.GetUserProfile(request.user, UserProfile)
    tenant = CORE_SHORTCUTS.GetUserTenant(profile, Tenant)
    
    if request.method == "POST":
        new_chat = AIChat.objects.create(title=_("New Chat"), tenant=tenant, added_by=request.user)
        return JsonResponse({"id": new_chat.id, "title": new_chat.title}, status=201)
    return JsonResponse({"error": "Invalid request method"}, status=400)

def get_ai_chats(request):
    """Retrieves all AI chat records for the authenticated user's tenant."""
    profile = CORE_SHORTCUTS.GetUserProfile(request.user, UserProfile)
    tenant = CORE_SHORTCUTS.GetUserTenant(profile, Tenant)
    
    chats = AIChat.objects.filter(tenant=tenant)
    return JsonResponse({"chats": [{"id": chat.id, "title": chat.title} for chat in chats]}, status=200)

def update_ai_chat(request, chat_id):
    """Updates an existing AI chat's title and settings."""
    profile = CORE_SHORTCUTS.GetUserProfile(request.user, UserProfile)
    tenant = CORE_SHORTCUTS.GetUserTenant(profile, Tenant)
    
    try:
        chat = AIChat.objects.get(id=chat_id, tenant=tenant)
    except AIChat.DoesNotExist:
        return JsonResponse({"error": "Chat not found"}, status=404)
    
    if request.method == "PUT":
        data = json.loads(request.body)
        chat.title = data.get("title")
        
        # Optional: Update compliance framework if provided
        if data.get("compliance_framework_id"):
            try:
                framework = ComplianceFramework.objects.get(id=data.get("compliance_framework_id"))
                chat.compliance_framework = framework
            except ComplianceFramework.DoesNotExist:
                pass
        
        # Optional: Update context if provided
        if data.get("context"):
            chat.context = data.get("context")
            
        chat.save()
        
        response_data = {
            "id": chat.id, 
            "title": chat.title
        }
        
        # Include optional fields if present
        if chat.compliance_framework:
            response_data["compliance_framework"] = {
                "id": chat.compliance_framework.id,
                "name": chat.compliance_framework.name,
                "version": chat.compliance_framework.version
            }
        
        if chat.context:
            response_data["context"] = chat.context
            
        return JsonResponse(response_data, status=200)
    
    return JsonResponse({"error": "Invalid request method"}, status=400)

def get_ai_chat_response(request, chat_id):
    """Retrieves chat history for a specific chat."""
    profile = CORE_SHORTCUTS.GetUserProfile(request.user, UserProfile)
    tenant = CORE_SHORTCUTS.GetUserTenant(profile, Tenant)
    
    try:
        chat = AIChat.objects.get(id=chat_id, tenant=tenant)
    except AIChat.DoesNotExist:
        return JsonResponse({"error": "Chat not found"}, status=404)
        
    interactions = chat.chatInteractions.all()
    response_data = [
        {
            "id": interaction.id, 
            "prompt": interaction.prompt, 
            "response": interaction.response,
            "control_references": interaction.control_references if hasattr(interaction, 'control_references') else None,
            "created_at": interaction.created.isoformat() if hasattr(interaction, 'created') else None
        } 
        for interaction in interactions
    ]
    
    return JsonResponse({"response": response_data}, status=200)

def delete_ai_chat(request, chat_id):
    """Deletes an AI chat instance."""
    profile = CORE_SHORTCUTS.GetUserProfile(request.user, UserProfile)
    tenant = CORE_SHORTCUTS.GetUserTenant(profile, Tenant)
    
    try:
        chat = AIChat.objects.get(id=chat_id, tenant=tenant)
    except AIChat.DoesNotExist:
        return JsonResponse({"error": "Chat not found"}, status=404)
    
    if request.method == "DELETE":
        chat.delete()
        return JsonResponse({}, status=204)
    return JsonResponse({"error": "Invalid request method"}, status=400)

# Chat Interaction Views
@csrf_exempt
@require_http_methods(["POST"])
def create_new_chat_interaction(request, chat_id):
    """Creates a new chat interaction and generates an AI response."""
    try:
        profile = CORE_SHORTCUTS.GetUserProfile(request.user, UserProfile)
        tenant = CORE_SHORTCUTS.GetUserTenant(profile, Tenant)
        
        # Get the chat or return 404
        try:
            chat = AIChat.objects.get(id=chat_id, tenant=tenant)
        except AIChat.DoesNotExist:
            return JsonResponse({"error": "Chat not found"}, status=404)
        
        # Parse the request body
        try:
            data = json.loads(request.body)
            prompt = data.get('prompt', '')
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON"}, status=400)
        
        if not prompt:
            return JsonResponse({"error": "Prompt is required"}, status=400)
        
        # Create the interaction and get the AI response
        interaction = chat.getAIResponse(request.user.username, prompt)
        
        # Return the interaction data
        return JsonResponse({
            "id": interaction.id, 
            "prompt": interaction.prompt, 
            "response": interaction.response,
            "control_references": interaction.control_references if hasattr(interaction, 'control_references') else None,
            "created_at": interaction.created.isoformat() if hasattr(interaction, 'created') else None
        }, status=200)
    
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

# Compliance Framework Views
def list_compliance_frameworks(request):
    """Lists all available compliance frameworks."""
    frameworks = ComplianceFramework.objects.all()
    
    framework_data = [{
        "id": framework.id,
        "name": framework.name,
        "version": framework.version,
        "description": framework.description
    } for framework in frameworks]
    
    return JsonResponse({"frameworks": framework_data}, status=200)

@csrf_exempt
@require_http_methods(["POST"])
def create_compliance_framework(request):
    """Creates a new compliance framework (admin only)."""
    try:
        # Check if user has permission (admin only)
        profile = CORE_SHORTCUTS.GetUserProfile(request.user, UserProfile)
        if not profile.is_admin:
            return JsonResponse({"error": "Permission denied"}, status=403)
        
        # Parse request data
        data = json.loads(request.body)
        name = data.get('name')
        version = data.get('version')
        description = data.get('description')
        
        if not name:
            return JsonResponse({"error": "Framework name is required"}, status=400)
        
        # Create the framework
        framework = ComplianceFramework.objects.create(
            name=name,
            version=version,
            description=description
        )
        
        return JsonResponse({
            "id": framework.id,
            "name": framework.name,
            "version": framework.version,
            "description": framework.description
        }, status=201)
        
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def stream_chat_interaction(request, chat_id):
    """Creates a new chat interaction and streams the AI response as it's generated."""
    try:
        profile = CORE_SHORTCUTS.GetUserProfile(request.user, UserProfile)
        tenant = CORE_SHORTCUTS.GetUserTenant(profile, Tenant)
        # Get the chat or return 404
        try:
            chat = AIChat.objects.get(id=chat_id, tenant=tenant)
        except AIChat.DoesNotExist:
            return JsonResponse({"error": "Chat not found"}, status=404)
        # Parse the request body
        try:
            data = json.loads(request.body)
            prompt = data.get('prompt', '')
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON"}, status=400)
        if not prompt:
            return JsonResponse({"error": "Prompt is required"}, status=400)
        # Create the interaction for tracking purposes
        interaction = chat.createInteraction(request.user.username, prompt)
        def stream_response():
            # Start the JSON response
            yield '{"id":"' + str(interaction.id) + '","response":"'
            # Stream the AI response tokens
            full_response = ""
            for token in chat.streamAIResponse(request.user.username, prompt, interaction):
                # Escape quotes and backslashes for JSON safety
                safe_token = token.replace('\\', '\\\\').replace('"', '\\"')
                yield safe_token
                full_response += token
            # Close the JSON response
            yield '","prompt":"' + prompt.replace('\\', '\\\\').replace('"', '\\"') + '"}'
            # Save the complete response to the interaction
            interaction.response = full_response
            interaction.save()
        return StreamingHttpResponse(
            stream_response(),
            content_type="application/json"
        )
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)