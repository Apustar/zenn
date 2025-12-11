from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import LinkCategoryViewSet, LinkViewSet

router = DefaultRouter()
router.register(r'link-categories', LinkCategoryViewSet, basename='link-category')
router.register(r'links', LinkViewSet, basename='link')

urlpatterns = [
    path('api/', include(router.urls)),
]

