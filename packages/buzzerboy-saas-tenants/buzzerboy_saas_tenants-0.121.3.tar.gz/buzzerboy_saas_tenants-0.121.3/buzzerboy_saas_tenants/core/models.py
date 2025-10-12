from django.db import models
from django.utils.crypto import get_random_string
from django.contrib.auth.models import User
import uuid
import re

class AuditableBaseModel(models.Model):
    """
    Abstract base model that includes audit fields for tracking creation and updates.
    """

    @staticmethod
    def random_related_name():
        """Generate a random string for related_name."""
        return get_random_string(10)

    created = models.DateTimeField(auto_now_add=True, null=True, blank=True,)
    last_updated = models.DateTimeField(auto_now=True, null=True, blank=True,)

    added_by = models.ForeignKey(
        User, 
        on_delete=models.DO_NOTHING, 
        null=True, 
        blank=True,
        related_name='created_%(class)ss'
    )

    last_updated_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='updated_%(class)ss'
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    class Meta:
        abstract = True
    
    
    @staticmethod
    def slugify(string,  prefix=None):
        """
        Converts a string into a URL-friendly slug.
        
        Args:
            string (str): The string to be slugified.
            unique_identifier (str, optional): A unique identifier to append to the slug. Defaults to None.
            unique (bool, optional): Whether to append a unique identifier to the slug. Defaults to True.
        
        Returns:
            str: The slugified string.
        """
        string = string.lower().strip()
        string = re.sub(r'[^\w\s-]', '', string)
        string = re.sub(r'[\s_-]+', '-', string)
        string = re.sub(r'^-+|-+$', '', string)
        return string
