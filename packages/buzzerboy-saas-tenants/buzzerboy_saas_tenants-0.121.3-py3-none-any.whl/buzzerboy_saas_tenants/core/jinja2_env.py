# jinja2_env.py

from jinja2 import Environment, FileSystemLoader
import os
from django.conf import settings

# Set up Jinja2 environment
template_dir = os.path.join(settings.BASE_DIR, 'templates')
jinja_env = Environment(loader=FileSystemLoader(template_dir))
