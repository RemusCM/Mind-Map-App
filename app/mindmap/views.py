"""
Views for MindMap APIs
"""
from rest_framework import (
    viewsets,
    mixins,
)
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from core.models import (
    MindMap,
    Leaf
)
from mindmap import serializers


class MindMapViewSet(viewsets.ModelViewSet):
    """View for managing the mindmap APIs."""
    serializer_class = serializers.MindMapSerializer
    queryset = MindMap.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Retrieve mindmaps for authenticated user."""
        return self.queryset.filter(user=self.request.user).order_by('-id')

    def perform_create(self, serializer):
        """Create a new mindmap."""
        serializer.save(user=self.request.user)


class LeafViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    """Manage Leafs in the database."""
    serializer_class = serializers.LeafSerializer
    queryset = Leaf.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_query(self):
        """Filter queryset to an authenticated user."""
        return self.queryset.filter(user=self.request.user).order_by('-path')
