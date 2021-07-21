from rest_framework import serializers

from core.models import Tag, Member


class TagSerializer(serializers.ModelSerializer):
    """Serializer for tag objects"""

    class Meta:
        model = Tag
        fields = ('id', 'name')
        read_only_fields = ('id',)


class MemberSerializer(serializers.ModelSerializer):
    """
    Serializer for member objects
    """

    class Meta:
        model = Member
        fields = ('id', 'name')
        read_only_fields = ('id',)
