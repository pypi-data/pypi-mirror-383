# core/email_service.py
from django.core.mail import send_mail
from buzzerboy_saas_tenants.core.jinja2_env import jinja_env  # Import the Jinja2 environment
from django.utils.html import strip_tags
#from buzzerboy_saas_tenants.core.shortcuts import send_email as CORE_SHORTCUTS_send_email

class EmailService:
    @staticmethod
    def send_template_email(template_content, context, subject, from_email, recipient_list):


        # Load the template from the string
        template = jinja_env.from_string(template_content)

        # Render the template with the context data
        rendered_content = template.render(context)

        plain_message = strip_tags(rendered_content)

        # Send the email using the rendered content
#        CORE_SHORTCUTS.send_email(subject=subject, message=rendered_content, recipient_list=recipient_list)
        
        send_mail(
            subject=subject,
            message=plain_message,  # Fallback message if HTML is not supported
            html_message=rendered_content,
            from_email=from_email,
            recipient_list=recipient_list,
            fail_silently=False,
        )
