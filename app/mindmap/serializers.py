"""
Serializers for MindMap API
"""
from rest_framework import serializers

from core.models import (
    MindMap,
    Leaf,
    )


class LeafSerializer(serializers.ModelSerializer):
    """Serializer for leafs."""

    class Meta:
        model = Leaf
        fields = ['id', 'path', 'text']
        read_only_fields = ['id']


class MindMapSerializer(serializers.ModelSerializer):
    """Serializer for MindMaps"""

    class Meta:
        model = MindMap
        fields = ['id', 'title']
        read_only_fields = ['id']


# class MindMapDetailSerializer(MindMapSerializer):
#     """Serializer for mindmap detail view."""

#     class Meta(MindMapSerializer.Meta):
#         fields = MindMapSerializer.Meta.fields + ['description']
