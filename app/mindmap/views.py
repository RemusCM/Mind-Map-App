"""
Views for MindMap APIs
"""
from rest_framework import (
    viewsets,
    mixins,
)
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from django.http import HttpResponse

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

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        print(instance)
        serializer = self.get_serializer(instance)
        print(serializer)
        print(serializer.data['title'])
        print(serializer.data['title'])

        paths = "\n"

        for path in serializer.data['leafs']:
            tabCounter = 1
            subpaths = path.split(sep='/')
            for subpath in subpaths:

                for tab in range(0, tabCounter):
                    paths += "\t"
                tabCounter += 1
                paths += subpath + "/\n"
        paths.rstrip()

        return HttpResponse(str(serializer.data['title'])+"/"+paths,
                            content_type="text/plain")


class LeafViewSet(mixins.UpdateModelMixin,
                  mixins.CreateModelMixin,
                  mixins.RetrieveModelMixin,
                  mixins.DestroyModelMixin,
                  mixins.ListModelMixin,
                  viewsets.GenericViewSet):
    """Manage Leafs in the database."""
    serializer_class = serializers.LeafSerializer
    queryset = Leaf.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Filter queryset to an authenticated user."""
        return self.queryset.filter(user=self.request.user).order_by('-path')

    def perform_create(self, serializer):
        """Create a new Leaf."""
        serializer.save(user=self.request.user)

    def get_serializer_class(self):
        """Return the serializer class depending on the request."""
        if self.action == 'retrieve':
            return serializers.LeafRetrieveSerializer
        return self.serializer_class

    # def retrieve(self, request, *args, **kwargs):
    #     instance = self.get_object()
    #     print(instance)
    #     serializer = self.get_serializer(instance)
    #     print(serializer)
    #     print(serializer.data)
    #     return Response(serializer.data)
