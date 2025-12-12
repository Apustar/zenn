from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import SiteSettingsViewSet, NavigationItemViewSet

router = DefaultRouter()
router.register(r'settings', SiteSettingsViewSet, basename='settings')
router.register(r'navigation', NavigationItemViewSet, basename='navigation')

urlpatterns = [
    path('api/', include(router.urls)),
]
