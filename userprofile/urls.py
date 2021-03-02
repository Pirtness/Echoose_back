from django.urls import path
from userprofile import views
from rest_framework.routers import DefaultRouter
from django.conf import settings
from django.conf.urls.static import static

router = DefaultRouter()

router.register(r'profile', views.ProfileViewSet, basename='profile')
urlpatterns = router.urls

router.register(r'service', views.ServiceViewSet, basename='service')
urlpatterns += router.urls

router.register(r'address', views.AddressViewSet)
urlpatterns += router.urls

urlpatterns += [
    path('hello/', views.HelloView.as_view(), name='hello')
]

urlpatterns += static(settings.IMAGES_URL, document_root=settings.IMAGES_ROOT)
