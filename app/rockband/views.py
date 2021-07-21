from rest_framework import viewsets, mixins
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from core.models import Tag, Member

from rockband import serializers


class BaseRockbandAttrViewSet(viewsets.GenericViewSet,
                              mixins.ListModelMixin,
                              mixins.CreateModelMixin):
    """
    Base viewset for user owned rockband attributes
    """
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        """Return objects for the current authenticated user only"""
        return self.queryset.filter(user=self.request.user).order_by('-name')

    def perform_create(self, serializer):
        """
        Create a new object
        :param serializer:
        :return: None
        """
        serializer.save(user=self.request.user)


class TagViewSet(BaseRockbandAttrViewSet):
    """Manage tags in the database"""
    queryset = Tag.objects.all()
    serializer_class = serializers.TagSerializer


class MemberViewSet(BaseRockbandAttrViewSet):
    """
    Manage members in the database
    """

    queryset = Member.objects.all()
    serializer_class = serializers.MemberSerializer
