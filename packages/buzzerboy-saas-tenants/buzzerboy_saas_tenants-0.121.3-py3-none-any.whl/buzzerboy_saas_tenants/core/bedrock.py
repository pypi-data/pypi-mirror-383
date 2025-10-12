import boto3
import json
import re
import hashlib
from botocore.exceptions import ClientError
from botocore.config import Config

from django.conf import settings
from buzzerboy_saas_tenants.core import platformConnectors
from buzzerboy_saas_tenants.core.utils import load_json_file

# Load initial prompts or fallback to default
try:
    INITIAL_PROMPT = load_json_file('bedrock_prompts.json')
except FileNotFoundError:
    INITIAL_PROMPT = {
        "default": {
            "description": "You are a friendly AI assistant for Buzzerboy. Respond naturally to user questions and engage in conversation about the company, its mission, and team.",
            "topics": [
                "About Buzzerboy and its mission",
                "Company background and services", 
                "Mission and vision",
                "Team roles and introductions",
                "How we turn ideas into businesses",
                "Specific questions about our work",
                "General conversation and engagement"
            ],
            "guidelines": "Keep your tone conversational and natural. Don't give long introductions unless specifically asked. Focus on answering the user's actual question. If they ask about specific aspects of Buzzerboy, focus on those details rather than giving a full company overview every time. Be engaging and ask follow-up questions when appropriate.",
            "context": {
                "about": "Buzzerboy is a company that turns ideas into businesses. We take a careful and methodical approach to translating ideas into products, products into software, and software into profitable businesses.",
                "mission_and_vision": "Develop low-cost disruptive solutions to forgotten problems in the real world.",
                "meet_the_team": [
                    {
                        "handle": "@Fahad Zain Jawaid",
                        "role": "Founder, Chief Product Architect"
                    },
                    {
                        "handle": "@Jiu Axl Tabilla", 
                        "role": "Product Developer"
                    },
                    {
                        "handle": "@Khent Mark Dahay",
                        "role": "Product Engineer"
                    },
                    {
                        "handle": "@Mohammed Ali Abdullah",
                        "role": "Product Engineer"
                    },
                    {
                        "handle": "@vince.maquilang",
                        "role": "Product Front-end Engineer"
                    },
                    {
                        "handle": "@edgar.flores",
                        "role": "Product Front-end Engineer"
                    },
                    {
                        "handle": "@jenerose.rabor",
                        "role": "Product Support"
                    }
                ]
            }
        },
        "conversational": {
            "description": "You are a friendly team member at Buzzerboy, chatting casually with visitors or potential clients.",
            "guidelines": "Be natural and conversational. Answer questions directly and briefly unless more detail is requested. Ask follow-up questions to keep the conversation flowing.",
            "context": {
                "about": "Buzzerboy is a company that turns ideas into businesses. We take a careful and methodical approach to translating ideas into products, products into software, and software into profitable businesses.",
                "mission_and_vision": "Develop low-cost disruptive solutions to forgotten problems in the real world.",
                "meet_the_team": [
                    {
                        "handle": "@Fahad Zain Jawaid",
                        "role": "Founder, Chief Product Architect"
                    },
                    {
                        "handle": "@Jiu Axl Tabilla", 
                        "role": "Product Developer"
                    },
                    {
                        "handle": "@Khent Mark Dahay",
                        "role": "Product Engineer"
                    },
                    {
                        "handle": "@Mohammed Ali Abdullah",
                        "role": "Product Engineer"
                    },
                    {
                        "handle": "@vince.maquilang",
                        "role": "Product Front-end Engineer"
                    },
                    {
                        "handle": "@edgar.flores",
                        "role": "Product Front-end Engineer"
                    },
                    {
                        "handle": "@jenerose.rabor",
                        "role": "Product Support"
                    }
                ]
            }
        }
    }


class BedrockClient:
    """
    Client for interacting with AWS Bedrock AI models.
    Handles authentication, model selection, retries, and message formatting.
    """

    def __init__(self, model_id=None, region=None):
        self.model_id = model_id or settings.BEDROCK_MODEL_ID
        self.region = region or settings.BEDROCK_REGION_NAME
        
        # Credentials
        self.aws_access_key = (
            getattr(settings, 'AWS_ACCESS_KEY', None)
            or platformConnectors.getAWSAccessKey()
        )
        self.aws_secret_access_key = (
            getattr(settings, 'AWS_SECRET_KEY', None)
            or platformConnectors.getAWSSecretKey()
        )

        # Inference parameters
        self.bedrock_max_tokens = int(
            getattr(settings, 'BEDROCK_MAX_TOKENS', 4000)
        )
        self.bedrock_temperature = float(
            getattr(settings, 'BEDROCK_TEMPERATURE', 0.7)  # Increased from 0.5
        )
        self.top_p = float(
            getattr(settings, 'BEDROCK_TOP_P', 0.9)
        )

        endpoint_url = f"https://bedrock-runtime.{self.region}.amazonaws.com"
        config = Config(signature_version='v4')

        # Initialize boto3 client
        client_kwargs = dict(
            service_name='bedrock-runtime',
            region_name=self.region,
            endpoint_url=endpoint_url,
            config=config
        )
        if self.aws_access_key and self.aws_secret_access_key:
            client_kwargs.update(
                aws_access_key_id=self.aws_access_key,
                aws_secret_access_key=self.aws_secret_access_key
            )

        self.bedrock_runtime = boto3.client(**client_kwargs)

    def generate_system_prompt(self, profile="default", compliance_framework=None, context=None, conversation_context=None):
        """
        Build a system prompt from JSON templates and optional context.
        Now includes conversation awareness to prevent repetitive responses.
        """
        prompt_parts = []
        profile_data = INITIAL_PROMPT.get(profile, INITIAL_PROMPT.get("default", {}))

        # Base description
        desc = profile_data.get('description') if isinstance(profile_data, dict) else profile_data
        prompt_parts.append(desc or "You are a helpful assistant.")

        # Topics
        topics = profile_data.get('topics') if isinstance(profile_data, dict) else None
        if topics:
            prompt_parts.append("Topics you can discuss:")
            for idx, topic in enumerate(topics, start=1):
                prompt_parts.append(f"• {topic}")

        # Guidelines with conversation awareness
        guidelines = profile_data.get('guidelines') if isinstance(profile_data, dict) else None
        if guidelines:
            prompt_parts.append(f"Guidelines: {guidelines}")
        
        # Add conversation context awareness
        prompt_parts.append("""
            CONVERSATION RULES:
            - Pay attention to the conversation history
            - If this is a follow-up question, build on previous responses naturally
            - Don't repeat information you've already provided unless asked to clarify
            - If the user asks a specific question, focus on answering that question directly
            - Vary your response style and approach based on what you've already discussed
            - Keep responses concise unless the user asks for detailed information
            - Be conversational and engaging, not robotic or repetitive
                    """.strip())

        # Default context - format as readable text
        custom_context = profile_data.get('context') if isinstance(profile_data, dict) else None
        if custom_context:
            prompt_parts.append("COMPANY INFORMATION:")
            
            if isinstance(custom_context, dict):
                if 'about' in custom_context:
                    prompt_parts.append(f"About: {custom_context['about']}")
                
                if 'mission_and_vision' in custom_context:
                    prompt_parts.append(f"Mission: {custom_context['mission_and_vision']}")
                
                if 'meet_the_team' in custom_context:
                    prompt_parts.append("Team Members:")
                    for member in custom_context['meet_the_team']:
                        prompt_parts.append(f"• {member.get('handle', 'Unknown')} - {member.get('role', 'Unknown Role')}")
            else:
                prompt_parts.append(str(custom_context))

        # Conversation state context
        if conversation_context:
            prompt_parts.append(f"CONVERSATION CONTEXT: {conversation_context}")

        # Compliance or additional context
        if compliance_framework:
            prompt_parts.append(f"COMPLIANCE FOCUS: Current discussion focuses on the {compliance_framework} framework.")
        
        if context:
            prompt_parts.append(f"ADDITIONAL CONTEXT: {context}")

        return "\n\n".join(prompt_parts)

    def format_chat_history(self, interactions):
        """
        Convert stored interactions into a list of message dicts.
        Only include successful interactions to maintain proper conversation flow.
        """
        messages = []
        for interaction in interactions:
            # Skip interactions that resulted in errors
            if (hasattr(interaction, 'response') and 
                interaction.response and 
                not any(error_phrase in str(interaction.response) for error_phrase in [
                    "There was an issue with your request format",
                    "Ops something went wrong",
                    "I encountered a technical issue",
                    "I don't have permission to access",
                    "The AI service is temporarily unavailable",
                    "Rate limit reached"
                ])):
                
                # Ensure text content is not empty and is a string
                user_text = str(interaction.prompt).strip() if interaction.prompt else ""
                assistant_text = str(interaction.response).strip() if interaction.response else ""
                
                if user_text and assistant_text:
                    messages.append({"role": "user", "content": [{"text": user_text}]})
                    messages.append({"role": "assistant", "content": [{"text": assistant_text}]})
        return messages

    def analyze_conversation_context(self, previous_interactions, current_prompt):
        """
        Analyze the conversation to provide context about what's been discussed.
        """
        if not previous_interactions:
            return "This is the start of a new conversation. Engage naturally with the user's question."
        
        context_parts = []
        
        # Convert to list if it's a QuerySet and get recent interactions safely
        interactions_list = list(previous_interactions) if hasattr(previous_interactions, 'model') else previous_interactions
        
        # Get recent responses safely
        recent_responses = []
        if len(interactions_list) > 0:
            # Get last 3 interactions safely
            start_idx = max(0, len(interactions_list) - 3)
            recent_interactions = interactions_list[start_idx:]
            recent_responses = [interaction.response for interaction in recent_interactions]
        
        # Check if we've already given company intro
        has_full_intro = any(
            "Buzzerboy" in response and 
            "mission" in response.lower() and 
            len(response) > 500  # Long response suggesting full intro
            for response in recent_responses
        )
        
        if has_full_intro:
            context_parts.append("You've already provided a company introduction.")
        
        # Check for team introductions
        has_team_intro = any(
            "team" in response.lower() and 
            any(name in response for name in ["Fahad", "Jiu", "Khent", "Mohammed", "Vince", "Edgar", "Jenerose"])
            for response in recent_responses
        )
        
        if has_team_intro:
            context_parts.append("You've already introduced team members.")
        
        # Analyze recent topics safely
        recent_topics = []
        if len(interactions_list) > 0:
            # Get last 2 interactions safely
            start_idx = max(0, len(interactions_list) - 2)
            recent_topic_interactions = interactions_list[start_idx:]
            
            for interaction in recent_topic_interactions:
                prompt_lower = interaction.prompt.lower()
                if "team" in prompt_lower:
                    recent_topics.append("team")
                elif "mission" in prompt_lower or "vision" in prompt_lower:
                    recent_topics.append("mission/vision")
                elif "service" in prompt_lower or "what do you do" in prompt_lower:
                    recent_topics.append("services")
                elif "how" in prompt_lower:
                    recent_topics.append("process/methodology")
        
        if recent_topics:
            context_parts.append(f"Recently discussed: {', '.join(set(recent_topics))}")
        
        # Analyze current prompt intent
        current_lower = current_prompt.lower().strip()
        
        # Check for greeting patterns
        greetings = ["hi", "hello", "hey", "good morning", "good afternoon", "good evening"]
        if any(greeting in current_lower for greeting in greetings) and len(current_lower) < 20:
            context_parts.append("User is greeting - respond warmly and briefly.")
        
        # Check for question patterns
        elif any(word in current_lower for word in ["what", "how", "why", "when", "where", "who"]):
            context_parts.append("User is asking a specific question - answer directly and concisely.")
        
        # Check for elaboration requests
        elif any(phrase in current_lower for phrase in ["tell me more", "explain", "elaborate", "details"]):
            context_parts.append("User wants more details - provide focused elaboration.")
        
        # Check for short responses
        elif len(current_prompt.strip()) < 10:
            context_parts.append("User gave a brief response - engage conversationally and ask a follow-up question.")
        
        # Check for multiple questions
        elif current_prompt.count('?') > 1:
            context_parts.append("User asked multiple questions - address each one clearly.")
        
        return " ".join(context_parts) if context_parts else "Continue the conversation naturally based on the user's input."

    def should_vary_parameters(self, prompt, previous_interactions):
        """
        Determine if we should adjust parameters to encourage variety.
        """
        if not previous_interactions:
            return False
        
        # Convert to list if it's a QuerySet
        interactions_list = list(previous_interactions) if hasattr(previous_interactions, 'model') else previous_interactions
        
        # Check if recent responses were very similar or long
        if len(interactions_list) >= 2:
            # Get last 2 interactions safely
            start_idx = max(0, len(interactions_list) - 2)
            recent_interactions = interactions_list[start_idx:]
            recent_responses = [i.response for i in recent_interactions]
            
            # Check response length similarity
            lengths = [len(r) for r in recent_responses]
            avg_length = sum(lengths) / len(lengths)
            
            # If responses are consistently very long, encourage variety
            if avg_length > 800:
                return True
            
            # Check for similar openings
            openings = [r[:100].lower() for r in recent_responses]
            similar_openings = len(set(openings)) < len(openings)
            
            if similar_openings:
                return True
        
        return False

    def _call_bedrock(self, conversation, system_content, use_varied_params=False):
        """
        Low-level call to Bedrock Runtime.
        """
        try:
            # Adjust parameters for variety if needed
            temperature = self.bedrock_temperature
            top_p = self.top_p
            
            if use_varied_params:
                temperature = min(1.0, self.bedrock_temperature + 0.15)  # Increase creativity
                top_p = min(1.0, self.top_p + 0.05)  # Slight increase in randomness
            
            # Debug: Print conversation structure
            print(f"Conversation length: {len(conversation)}")
            for i, msg in enumerate(conversation):
                print(f"Message {i}: role={msg['role']}, content_length={len(msg['content'][0]['text'])}")
            
            # Prepare the request parameters
            request_params = {
                "modelId": self.model_id,
                "messages": conversation,
                "inferenceConfig": {
                    "maxTokens": self.bedrock_max_tokens,
                    "temperature": temperature,
                    "topP": top_p
                }
            }
            
            # Add system message if provided
            if system_content and system_content.strip():
                request_params["system"] = [{"text": system_content.strip()}]
            
            return self.bedrock_runtime.converse(**request_params)
            
        except Exception as e:
            print(f"Error in _call_bedrock: {str(e)}")
            print(f"Model ID: {self.model_id}")
            print(f"Region: {self.region}")
            raise

    def invoke_model(self, prompt, ai_chat, previous_interactions=None):
        """
        High-level API: assemble system/user messages, call Bedrock, handle errors.
        """
        # Analyze conversation context
        conversation_context = self.analyze_conversation_context(previous_interactions, prompt)
        
        # Generate system instructions with conversation awareness
        system_content = self.generate_system_prompt(
            profile=getattr(settings, 'AI_CHAT_PROFILE', 'conversational'),  # Changed default to conversational
            compliance_framework=(
                ai_chat.compliance_framework.name if ai_chat.compliance_framework else None
            ),
            context=getattr(ai_chat, 'context', None),
            conversation_context=conversation_context
        )

        # Build conversation (without system message in messages array)
        conversation = []

        # Add history (limit to recent interactions to avoid context bloat)
        # Only include successful interactions to maintain proper conversation flow
        if previous_interactions:
            # Convert to list if it's a QuerySet and limit to recent interactions
            interactions_list = list(previous_interactions) if hasattr(previous_interactions, 'model') else previous_interactions
            
            # Only include last 3 successful interactions to keep context manageable
            if len(interactions_list) > 3:
                recent_interactions = interactions_list[-3:]
            else:
                recent_interactions = interactions_list
                
            history_messages = self.format_chat_history(recent_interactions)
            conversation.extend(history_messages)

        # Add the new user prompt with validation
        user_prompt_clean = str(prompt).strip() if prompt else ""
        if not user_prompt_clean:
            return "I didn't receive a message. Please try again.", None
            
        conversation.append({
            "role": "user",
            "content": [{"text": user_prompt_clean}]
        })
        
        # Final validation: ensure proper conversation structure
        # Must have alternating user/assistant messages, ending with user
        if len(conversation) == 0:
            return "Invalid conversation structure. Please try again.", None
            
        # Check that we end with a user message (required by Bedrock)
        if conversation[-1]["role"] != "user":
            return "Conversation must end with a user message. Please try again.", None
            
        # Validate no consecutive same-role messages
        for i in range(len(conversation) - 1):
            if conversation[i]["role"] == conversation[i + 1]["role"]:
                # Remove duplicate consecutive messages of same role
                conversation = [msg for j, msg in enumerate(conversation) 
                             if j == 0 or msg["role"] != conversation[j-1]["role"]]
                break

        try:
            # Determine if we should use varied parameters
            use_variation = self.should_vary_parameters(prompt, previous_interactions)
            
            # Call Bedrock with separate system content
            response = self._call_bedrock(conversation, system_content, use_varied_params=use_variation)
            ai_response = response['output']['message']['content'][0]['text']

            # Extract any control references
            controls = self.extract_control_references(ai_response)
            return ai_response, controls

        except ClientError as e:
            error_info = e.response.get('Error', {})
            code = error_info.get('Code')
            message = error_info.get('Message', '')
            
            # Log the actual error for debugging
            print(f"Bedrock ClientError - Code: {code}, Message: {message}")
            
            if code == 'AccessDeniedException':
                msg = 'I don\'t have permission to access the AI service right now. Please contact support.'
            elif code == 'ValidationException':
                msg = f'There was a validation issue with the request. Error: {message}'
            elif code == 'ServiceUnavailableException':
                msg = 'The AI service is temporarily unavailable. Please try again in a few minutes.'
            elif code == 'ModelNotReadyException':
                msg = 'The AI model is starting up. Please wait a moment and try again.'
            elif code == 'ThrottlingException':
                msg = 'I\'m experiencing high demand right now. Please try again in a moment.'
            else:
                msg = f'I encountered a technical issue ({code}): {message}. Please try again or contact support if this persists.'
            return msg, None
        except Exception as e:
            print(f"Unexpected error in invoke_model: {str(e)}")
            return f'I encountered an unexpected error. Please try again or contact support if this continues.', None

    def extract_control_references(self, text):
        """
        Find compliance control IDs (e.g., NIST, FedRAMP, CMMC) in the model's output.
        """
        patterns = [
            r"\b([A-Z]{2}-\d+(?:\(\d+\))?)\b",           # NIST 800-53
            r"\b(FedRAMP [A-Z]{2}-\d+(?:\(\d+\))?)\b",    # FedRAMP
            r"\b([A-Z]{2}\.\d+\.\d{3})\b"                # CMMC
        ]
        regex = re.compile('|'.join(patterns))
        found = set(match for match in regex.findall(text) if any(match))
        
        # Flatten the tuple results and filter out empty strings
        flattened = []
        for match in found:
            if isinstance(match, tuple):
                flattened.extend([m for m in match if m])
            elif match:
                flattened.append(match)
        
        return ", ".join(set(flattened)) if flattened else None