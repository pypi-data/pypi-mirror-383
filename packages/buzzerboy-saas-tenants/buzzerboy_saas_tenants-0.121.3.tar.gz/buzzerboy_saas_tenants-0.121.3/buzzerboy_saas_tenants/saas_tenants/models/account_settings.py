
from django.db import models
from django.contrib.auth.models import User




# Create your models here.
class NotificationPreferences(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='notification_preferences')
    
    email_notifications = models.BooleanField(default=True)
    sms_notifications = models.BooleanField(default=True)
    push_notifications = models.BooleanField(default=True)

    class Meta:
        verbose_name_plural = "Notification Preferences"

    def __str__(self):
        return f"{self.user.username}'s Notification Preferences"
    
class NotificationChannel(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notification_channels')
    
    email_address = models.EmailField(null=True, blank=True)
    phone_number = models.CharField(max_length=15, null=True, blank=True)
    device_token = models.CharField(max_length=255, null=True, blank=True)  # For push notifications

    def __str__(self):
        return f"Channels for {self.user.username}"
    
class NotificationSettings(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='notification_settings')
    
    frequency = models.CharField(max_length=50, choices=[('immediately', 'Immediately'), ('daily', 'Daily'), ('weekly', 'Weekly')], default='immediately')
    enabled = models.BooleanField(default=True)
    
    quiet_hours_start = models.TimeField(null=True, blank=True)
    quiet_hours_end = models.TimeField(null=True, blank=True)
    
    preferred_language = models.CharField(max_length=50, default='en')

    def __str__(self):
        return f"Settings for {self.user.username}"
    
class NotificationType(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notification_types')
    
    system_alerts = models.BooleanField(default=True)
    promotional_messages = models.BooleanField(default=False)
    user_activity = models.BooleanField(default=True)

    def __str__(self):
        return f"Notification Types for {self.user.username}"

class CustomTemplate(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='custom_templates')
    
    template_name = models.CharField(max_length=100)
    subject = models.CharField(max_length=255)
    body = models.TextField()

    def __str__(self):
        return f"{self.template_name} - {self.user.username}"

class NotificationHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notification_history')
    
    notification_type = models.CharField(max_length=100)
    sent_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Notification sent to {self.user.username} at {self.sent_at}"
class NotificationLog(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='notification_log')
    
    last_notified = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Last notified: {self.last_notified} for {self.user.username}"