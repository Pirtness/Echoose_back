from django.urls import path
from userprofile import views
from rest_framework.routers import DefaultRouter
from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls import url

from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter



router = DefaultRouter()

router.register(r'profile', views.ProfileViewSet, basename='profile')
urlpatterns = router.urls

router.register(r'service', views.ServiceViewSet, basename='service')
urlpatterns += router.urls

router.register(r'address', views.AddressViewSet)
urlpatterns += router.urls

router.register(r'offers', views.OfferViewSet, basename='offers')
urlpatterns += router.urls

router.register(r'dialog', views.DialogViewSet, basename='dialog')
urlpatterns += router.urls




#urlpatterns += application.websocket.urls
urlpatterns += static(settings.IMAGES_URL, document_root=settings.IMAGES_ROOT)
