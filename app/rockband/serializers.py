from rest_framework import serializers

from core.models import Tag, Member, Band


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


class BandSerializer(serializers.ModelSerializer):
    """
    Serialize a band
    """
    members = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Member.objects.all()
    )
    tags = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Tag.objects.all()
    )

    class Meta:
        model = Band
        fields = ('id', 'title', 'members', 'tags', 'band_members',
                  'tickets', 'link'
                  )
        read_only_fields = ('id',)


class BandDetailSerializer(BandSerializer):
    """
    Serialize a band detail
    """
    members = MemberSerializer(many=True, read_only=True)
    tags = TagSerializer(many=True, read_only=True)


class BandImageSerializer(serializers.ModelSerializer):
    """
    Serializer for uploading images
    """

    class Meta:
        model = Band
        fields = ('id', 'image')
        read_only_fields = ('id',)
