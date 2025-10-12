from django.db import models

# Create your models here.
class Timezone(models.Model):
    timezone = models.CharField(max_length=63, unique=True)
    offset = models.CharField(max_length=10, blank=True, null=True)

    def __str__(self):
        return self.timezone

class Country(models.Model):
    name = models.CharField(max_length=255)
    flag_url = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return self.name

class StateProvince (models.Model):
    location_name = models.CharField(max_length=255)
    country = models.ForeignKey(Country, blank=True, null=True, on_delete=models.SET_NULL)

    def __str__(self):
        return self.location_name

class SupportedLanguage(models.Model):
    language_key = models.CharField(max_length=4)
    description = models.CharField(max_length=255)
    flag_url = models.TextField
    flag_pic = models.ImageField(null=True, blank=True, default="", upload_to="settings/flags")

    def __str__(self):
        return self.description + " (" + self.language_key + ")"

    @staticmethod
    def get_languages():
        sl = SupportedLanguage.objects.all()
        return sl

    def flag_img(self):
        return "<img src='" + self.flag_url + "'/>"

    @property
    def flag_url(self):
        if self.flag_pic and hasattr(self.flag_pic, 'url'):
            return self.flag_pic.url
