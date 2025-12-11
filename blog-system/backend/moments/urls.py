from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import MomentViewSet

router = DefaultRouter()
router.register(r'moments', MomentViewSet, basename='moment')

urlpatterns = [
    path('api/', include(router.urls)),
]

