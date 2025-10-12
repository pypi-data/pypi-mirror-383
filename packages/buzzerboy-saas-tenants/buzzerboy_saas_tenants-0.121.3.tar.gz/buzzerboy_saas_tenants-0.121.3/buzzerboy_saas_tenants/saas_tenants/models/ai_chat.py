import uuid
import logging
from django.db import models
from ckeditor.fields import RichTextField
from buzzerboy_saas_tenants.core.bedrock import BedrockClient
from buzzerboy_saas_tenants.core.models import AuditableBaseModel
from buzzerboy_saas_tenants.saas_tenants.models import Tenant



logger = logging.getLogger(__name__)

class ComplianceFramework(models.Model):
    "Model to represent different compliance frameworks (NIST, FedRAMP , ITSG-33, etc...)"
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    version = models.CharField(max_length=50, blank=True, null=True)
    def __str__(self):
        return f"{self.name} {self.version or ''}"
class AIChat(AuditableBaseModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255)
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name="aiChats")
    compliance_framework = models.ForeignKey(
        ComplianceFramework,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="chats"
    )
    context = models.TextField(blank=True, null=True, help_text="Additional context about the system being assessed")
    def __str__(self):
        return self.title
    def getAIResponse(self, user, prompt):
        """
        Generate an AI response using AWS Bedrock.
        """
        try:
            # Create the interaction with a placeholder
            interaction = ChatInteraction.objects.create(
                ai_chat=self,
                tenant=self.tenant,
                user=user,
                prompt=prompt,
                response="Processing..."
            )
            # Initialize Bedrock client
            bedrock_client = BedrockClient()
            # Get the AI response
            previous_interactions = self.chatInteractions.all().order_by('-created')[:5]
            response, control_refs = bedrock_client.invoke_model(
                prompt=prompt,
                ai_chat=self,
                previous_interactions=previous_interactions
            )
            # Update the interaction
            interaction.response = response
            if control_refs:
                interaction.control_references = control_refs
            interaction.save()
            return interaction
        except Exception as e:
            # Create an interaction with the error message
            # error_msg = f"Error generating response: {str(e)}"
            logger.error(f"Error generating response: {str(e)}")
            error_msg = "Ops something went wrong. Please try again later."
            interaction = ChatInteraction.objects.create(
                ai_chat=self,
                tenant=self.tenant,
                user=user,
                prompt=prompt,
                response=error_msg
            )
            return interaction
    def generate_bedrock_response(self, prompt, interaction):
        # This will be implemented with AWS Bedrock
        # For now, returning a placeholder
        return "This is where the AWS Bedrock response will go"
    def createInteraction(self, username, prompt):
        """
        Create a new chat interaction without a response.
        Returns the created interaction object.
        """
        # Create a new interaction with empty response
        interaction = ChatInteraction.objects.create(
            ai_chat=self,
            tenant=self.tenant,
            user=username,
        prompt=prompt,
        response=""  # Empty response initially
    )
        return interaction
    def streamAIResponse(self, username, prompt, interaction):
        """
        Stream the AI response tokens as they are generated.
        Yields tokens one by one.
        """
        try:
            # Initialize Bedrock client
            bedrock_client = BedrockClient()
            # Get previous interactions for context
            previous_interactions = self.chatInteractions.all().order_by('-created')[:5]
            # This is where you'd implement streaming from your AI provider
            # For now, we'll simulate streaming with the existing method
            # Get the complete response first (replace this with actual streaming implementation)
            full_response, control_refs = bedrock_client.invoke_model(
                prompt=prompt,
                ai_chat=self,
                previous_interactions=previous_interactions
            )
            # Store control references if any
            if control_refs:
                interaction.control_references = control_refs
                interaction.save()
            # Simulate streaming by yielding one character at a time
            for char in full_response:
                yield char
            # The full response will be saved by the view function
            return full_response
        except Exception as e:
            # Log the error
            logger.error(f"Error streaming response: {str(e)}")
            error_msg = "Oops something went wrong. Please try again later."
            # Stream the error message
            for char in error_msg:
                yield char
            return error_msg
        


class ChatInteraction(AuditableBaseModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.CharField(max_length=255)
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name="chatInteractions")
    ai_chat = models.ForeignKey(AIChat, on_delete=models.CASCADE, related_name="chatInteractions")
    prompt = RichTextField(default="Default prompt")
    response = RichTextField()
    control_references = models.TextField(blank=True, null=True, help_text="Security controls referenced in this interaction")
    def __str__(self):
        return f"Interaction by {self.user} with {self.ai_chat.title}"