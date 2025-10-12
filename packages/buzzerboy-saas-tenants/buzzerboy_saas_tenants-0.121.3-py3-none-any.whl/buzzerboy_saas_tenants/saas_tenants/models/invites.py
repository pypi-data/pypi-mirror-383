
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _  # Make sure to use gettext_lazy for model choices


from buzzerboy_saas_tenants.core.models import AuditableBaseModel
from buzzerboy_saas_tenants.saas_tenants.models.accounts import UserType
from buzzerboy_saas_tenants.saas_tenants.models.tenant import Tenant

# Create your models here.
class Invites(AuditableBaseModel):
    
    access_role = models.ForeignKey(UserType, on_delete=models.DO_NOTHING, blank=True, null=True)
    email = models.EmailField(max_length=254, blank=False, null=False)
    first_name = models.CharField(max_length=50, blank=False, null=False)
    last_name = models.CharField(max_length=50, blank=False, null=False)
    notes = models.TextField(blank=True, null=True)
    tenant = models.ForeignKey(Tenant, on_delete=models.DO_NOTHING, blank=True, null=True, related_name='invites')

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('expired', 'Expired'),
        ('cancelled', 'Cancelled'),
    ]
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    expired_at = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.email}) - {self.get_status_display()}"
    
    def save(self, *args, **kwargs):
        if self.status == 'expired' and not self.expired_at:
            self.expired_at = timezone.now()
        super().save(*args, **kwargs)
