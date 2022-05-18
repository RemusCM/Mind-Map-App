"""
URL mappings for the MindMap app.
"""
from django.urls import (
    path,
    include,
)

from rest_framework.routers import DefaultRouter

from mindmap import views

router = DefaultRouter()
router.register('mindmaps', views.MindMapViewSet)
router.register('leafs', views.LeafViewSet)

app_name = 'mindmap'

urlpatterns = [
    path('', include(router.urls))
]