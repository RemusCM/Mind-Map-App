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
# from anytree import AbstractStyle, Node, RenderTree

from core.models import (
    MindMap,
    Leaf
)
from mindmap import serializers


def pretty_print(node, tab_counter=0, result=None) -> str:
    """Pretty print tree from node"""
    if result is None:
        result = ""

    if node.children == []:
        tabs = ""
        for i in range(0, tab_counter):
            tabs += "\t"

        result += tabs + node.data + "\n"
        return str(result)

    else:
        tabs = ""
        for i in range(0, tab_counter):
            tabs += "\t"
        result += tabs + node.data + "/\n"
        tab_counter += 1
        for child_node in node.children:
            result += pretty_print(child_node, tab_counter, result)
        return result


class Node(object):
    def __init__(self, data):
        self.data = data
        self.children = []

    def add_child(self, obj):
        self.children.append(obj)

    def __str__(self) -> str:
        return pretty_print(self, tab_counter=0, result=None)


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
        serializer = self.get_serializer(instance)
        root = Node(data=str(serializer.data['title']))

        # Tree Creation
        node = root
        for path in serializer.data['leafs']:
            subpaths = path.split(sep='/')
            for index, value, in enumerate(subpaths):
                # Navigate to end of known tree
                for i in range(index):
                    for j in node.children:
                        if j.data == subpaths[i]:
                            node = j

                exists_flag = False
                for child_node in node.children:
                    if child_node.data == value:
                        exists_flag = True
                        break
                if exists_flag:
                    exists_flag = False
                    if index == len(subpaths) - 1:
                        node = root
                else:

                    node.add_child(Node(data=value))
                    exists_flag = False
                    node = root

        return HttpResponse(
            str(node)[str(node).rfind(serializer.data['title']):].rstrip(),
            content_type="text/plain"
            )


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
