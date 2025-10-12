import os
from django.db import models


from buzzerboy_saas_tenants.saas_tenants.models.accounts import UserProfile
from buzzerboy_saas_tenants.saas_tenants.models.localization import Country, StateProvince
from buzzerboy_saas_tenants.saas_tenants.models.tenant import Tenant



from buzzerboy_saas_tenants.core.models import AuditableBaseModel

class BillingDetails(models.Model):
    tenant = models.OneToOneField(Tenant, related_name='tenant_billing', blank=True, null=True, on_delete=models.DO_NOTHING)
    billing_contact_name = models.CharField(max_length=50, null=True)
    billing_contact_address = models.CharField(max_length=50, null=True)
    billing_contact_city = models.CharField(max_length=50, null=True)
    billing_contact_postalcode = models.CharField(max_length=50, null=True)
    billing_contact_country = models.ForeignKey(Country, on_delete=models.SET_NULL, null=True, related_name="tenant_billing_country")
    billing_contact_state_province = models.ForeignKey(StateProvince, on_delete=models.SET_NULL, null=True, related_name="tenant_billing_state")
    billing_contact_email = models.EmailField(max_length=255, null=True)
    billing_contact_telephone = models.CharField(max_length=20, null=True)
    
class AuditLog(models.Model):
    tenant = models.ForeignKey(Tenant, related_name='tenant_audit_logs', on_delete=models.DO_NOTHING)
    activity = models.CharField(max_length=255, null=True)
    module = models.CharField(max_length=255, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    performed_by = models.ForeignKey(UserProfile, related_name='tenant_activity_performed_by', null=True, blank=True, on_delete=models.DO_NOTHING)
    details = models.JSONField(null=True, blank=True)

class SupportCase(AuditableBaseModel):
    class SupportCaseStatus(models.TextChoices):
        PENDING = 'pending', 'Pending'
        RESOLVED = 'resolved', 'Resolved'
        IN_PROGRESS = 'in_progress', 'In Progress'

    REQUEST_TYPE_CHOICES = [
        ('bug', 'Bug Report'),
        ('feature', 'Feature Request'),
        ('support', 'Support Inquiry'),
        # Add more options as needed
    ]

    id = models.AutoField(primary_key=True)
    request_type = models.CharField(max_length=20, choices=REQUEST_TYPE_CHOICES)
    summary = models.CharField(max_length=255)
    detailed_description = models.TextField()
    status = models.CharField(
        max_length=20,
        choices=SupportCaseStatus.choices,
        default=SupportCaseStatus.PENDING
    )


    def __str__(self):
        return self.summary

class SupportCaseResponse(AuditableBaseModel):

    def upload_support_case_attachments(instance, filename):
        fname, fextension = os.path.splitext(filename)
        s = "u_" + instance.id.__str__() + fextension
        return os.path.join('support_case_attachments', instance.id.__str__(), "user", s)
    
    
    case = models.ForeignKey(SupportCase, on_delete=models.DO_NOTHING)
    message = models.TextField()
    attachment = models.FileField(upload_to=upload_support_case_attachments, blank=True, null=True)

    def __str__(self):
        return f"Response to case {self.case.id}"


