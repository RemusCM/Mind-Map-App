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
        fields = ['id', 'mindmap', 'path', 'text']
        read_only_fields = ['id']

    def to_representation(self, instance):
        self.fields['mindmap'] = MindMapSerializer(read_only=True)
        return super(LeafSerializer, self).to_representation(instance)


class LeafRetrieveSerializer(serializers.ModelSerializer):
    """Serializer to use when retrieving a specific leaf."""
    class Meta:
        model = Leaf
        fields = ['id', 'path', 'text']
        read_only_fields = ['id']


class MindMapSerializer(serializers.ModelSerializer):
    """Serializer for MindMaps"""
    leafs = serializers.StringRelatedField(read_only=True, many=True)

    class Meta:
        model = MindMap
        fields = ['id', 'title', 'leafs', ]
