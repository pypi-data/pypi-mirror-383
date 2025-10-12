from django.db import models



class IdentityProvider(models.Model):
    domain = models.CharField(max_length=255, unique=True)  # E.g., "companyA.com"
    idp_metadata_url = models.URLField()  # URL to the IdP metadata (e.g., Federation Metadata XML)
    idp_name = models.CharField(max_length=255, blank=True, null=True)  # Optional name for the IdP

    def __str__(self):
        return self.domain
