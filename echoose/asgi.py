"""
ASGI config for echoose project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.1/howto/deployment/asgi/
"""

import os

from django.core.asgi import get_asgi_application



os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'echoose.settings')

from djangochannelsrestframework.consumers import view_as_consumer
from userprofile import views
from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from django.conf.urls import url
from django.urls import path

websockets = URLRouter([
    path(
        "ws/dialog", views.DialogViewSet.as_asgi(),
        name="dialog",
    ),
])

application = ProtocolTypeRouter({
    "websocket": websockets,
})


#application = get_asgi_application()
