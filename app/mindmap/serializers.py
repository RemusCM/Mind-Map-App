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
    leafs = LeafSerializer(many=True, required=False)

    class Meta:
        model = MindMap
        fields = ['id', 'title', 'leafs', ]
        read_only_fields = ['id']

    def _get_or_create_leafs(self, leafs, mindmap):
        """Handle getting or creating leafs for MindMaps"""
        auth_user = self.context['request'].user
        for leaf in leafs:
            leaf_obj, create = Leaf.objects.get_or_create(
                user=auth_user,
                **leaf,
            )
            mindmap.leafs.add(leaf_obj)

    def create(self, validated_data):
        """Create a MindMap"""
        leafs = validated_data.pop('leafs', [])
        mindmap = MindMap.objects.create(**validated_data)
        self._get_or_create_leafs(leafs, mindmap)
        return mindmap

    def update(self, instance, validated_data):
        """Update a MindMap"""
        leafs = validated_data.pop('leafs', None)
        if leafs is not None:
            instance.leafs.clear()
            self._get_or_create_leafs(leafs, instance)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance



# class MindMapDetailSerializer(MindMapSerializer):
#     """Serializer for mindmap detail view."""

#     class Meta(MindMapSerializer.Meta):
#         fields = MindMapSerializer.Meta.fields + ['description']
