"""
URL Configuration for Django project.

This module defines the URL patterns for the project. It includes the following routes:
- Admin route: '/admin/' for accessing the Django admin site.
- Authentication routes: Routes for login and registration.
- Home routes: Routes for UI Kits HTML files.
- CKEditor route: '/ckeditor/' for CKEditor file uploads.

If the project is in DEBUG mode, it also includes the media URL pattern for serving media files.

Note: This module is located at '/Users/ralphvincent/Desktop/buzzerboy_inc/DuraluxDjango/core/urls.py'.
"""

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from django.conf.urls.i18n import i18n_patterns
from buzzerboy_saas_tenants.core.views import change_language
urlpatterns = [
    path('admin/', admin.site.urls),
    path('ckeditor/', include('ckeditor_uploader.urls')),
    path('change-language/', change_language, name='change_language'),  
   path('accounts/', include('allauth.urls')),
    path('i18n/', include('django.conf.urls.i18n')),  
]

urlpatterns += i18n_patterns(
    path("", include("buzzerboy_saas_tenants.saas_tenants.urls")),  
           
)


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)