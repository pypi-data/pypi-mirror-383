
import  uuid
import os
from ckeditor.fields import RichTextField
from urllib.parse import urlparse

from django.contrib.auth.models import User
from django.db import models
from django.utils.translation import gettext_lazy as _  # Make sure to use gettext_lazy for model choices


from buzzerboy_saas_tenants.core.models import AuditableBaseModel
from buzzerboy_saas_tenants.saas_tenants.models.localization import Country, StateProvince, SupportedLanguage

class SubscriptionPlan(models.Model):
    class PlanNames(models.TextChoices):
        BASIC = 'BASIC', 'Basic Plan'
        PRO = 'TEAM', 'Team Plan'
        ENTERPRISE = 'ENTERPRISE', 'Enterprise Plan'

    
    name = models.CharField(
        default=PlanNames.BASIC,
        max_length=10,
        choices=PlanNames.choices,
        unique=True,
        help_text="The subscription plan these features apply to."
    )

    price = models.DecimalField(max_digits=6, decimal_places=2, default=0.00, help_text="Price of the plan")
    description = models.TextField(blank=True, help_text="Description of the subscription plan")

    user_limit = models.IntegerField(default=5, help_text="Number of users allowed")
    department_limit = models.IntegerField(default=5, help_text="Number of departments allowed")
    vulnerability_limit = models.IntegerField(default=5, help_text="Number of vulnerabilities allowed")
    storage_limit = models.IntegerField(default=5, help_text="Storage limit in GB")
    dashboard_access = models.BooleanField(default=False, help_text="Access to dashboard")
    api_access = models.BooleanField(default=False, help_text="Access to API")
    advanced_support = models.BooleanField(default=False, help_text="Access to advanced support")
    # Add any other features here...

    def __str__(self):
        return f"{self.get_name_display()}"

    def get_name_display(self):
        return self.PlanNames(self.name).label

class ContractStatus (models.Model):
    description = models.CharField(max_length=255)  
    desc_prefix = models.CharField(max_length=255, default='<i class="bg-dark"></i>')

    def __str__(self):
        return self.description

class Tenant(AuditableBaseModel):
    

    def upload_company_logo(instance, filename):
       fname, fextension = os.path.splitext(filename)
       s = "t_" + instance.id.__str__() + "__u_".__str__() + instance.uuid.__str__() + fextension
       return os.path.join('uploads', instance.uuid.__str__(), "tenant", s)


    uuid = models.UUIDField(default=uuid.uuid4, unique=True)
    company_name = models.CharField(max_length=255, unique=True, null=True, blank=True, default="*** TENANT NOT SETUP ***")
    subdomain = models.CharField(max_length=25, null=True, blank=True)
    support_email_address = models.CharField(max_length=255, blank=True, null=True)

    company_slogan = models.TextField(default="", blank=True, null=True)
    website = models.CharField(null=True, blank=True, max_length=255, unique=True)
    
    address = models.CharField(null=True, max_length=255)
    city = models.CharField(null=True, max_length=20)
    postalcode = models.CharField(null=True, max_length=10)
    state_province = models.ForeignKey(StateProvince, null=True, blank=True, on_delete=models.SET_NULL, related_name="tenants")
    country = models.ForeignKey(Country, on_delete=models.SET_NULL, null=True, blank=True, related_name="tenants")
    
    telephone = models.CharField(max_length=20, blank=True)
    fax = models.CharField(max_length=20, blank=True)
    contract_status = models.ForeignKey(ContractStatus, on_delete=models.SET_NULL, null=True, blank=True)
    primary_account_email = models.EmailField(max_length=255,  unique=True, null=True, blank=True)
    primary_account_name = models.CharField(max_length=255,  unique=True, null=True, blank=True)
    
    company_logo = models.ImageField(null=True, blank=True, default="", upload_to=upload_company_logo)
    beta_features_csv = models.TextField(null=True, blank=True)

    user_invite_subject = models.CharField(null=True, blank=True, max_length=100)
    user_invite_template = RichTextField(null=True, blank=True, default="Please join our team. Click on the link below to create your account. <br><br><a href='{{invite_url}}'>{{invite_url}}</a>")

    subscription_plan = models.ForeignKey(
        SubscriptionPlan,
        default=1,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='tenants'
    )
    
    @staticmethod
    def get_tenant_by_subdomain(absolute_url):

        url = urlparse(absolute_url)
        url_subdomain = url.hostname.split('.')[0]  

        try:
            obj = Tenant.objects.get(subdomain=url_subdomain)
        except:
            return

        return obj

    def __str__(self):
        return self.company_name   

    def get_tenant_template(self):
        return self.user_invite_template   

    def supported_languages(self):
        list = self.tenant_languages.all()
        if list:
            res = {}
            count = 0
            for x in list:
                res.update({
                    x.language: 'item' + count.__str__()})
                count += 1
            return res
        
        else:
            return {SupportedLanguage.objects.first()}     

    def tenant_administrators_html_list(self):
        s = "<ul>"
        for k in self.team.all():
            if k.user_type.has_full_access:
                s += "<li>" + k.user_object.email + "</li>"

        s += "</ul>"
        return s

    def has_betafeature(self, feature_string):
        if self.beta_features_csv:
            return self.beta_features_csv.find(feature_string) >= 0 
        else:   
            return False

    @property
    def company_logo_url(self):
        if self.company_logo and hasattr(self.company_logo, 'url'):
            return self.company_logo.url 

class TenantLanguages(models.Model):
    tenant = models.ForeignKey(Tenant, null=True, blank=True, on_delete=models.SET_NULL, related_name="tenant_languages")
    language = models.ForeignKey(SupportedLanguage, null=True, blank=True, on_delete=models.SET_NULL, related_name="tenants")

    company_name = models.CharField(max_length=255, default="")
    company_slogan = models.TextField(default="") 

    def default_company_name(self):
        return self.tenant.company_name

    def __str__(self):
        return self.language.__str__()

