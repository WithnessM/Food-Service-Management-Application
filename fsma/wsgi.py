"""
WSGI config for fsma project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/wsgi/
"""

import os
from django.core.wsgi import get_wsgi_application
from whitenoise import WhiteNoise

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fsma.settings')

# Get the Django WSGI application
application = get_wsgi_application()

# Wrap it with WhiteNoise to serve static files
application = WhiteNoise(application, root='/home/ec2-user/Food-Service-Management-Application/staticfiles')
