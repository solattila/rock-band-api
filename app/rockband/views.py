from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import viewsets, mixins, status
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from core.models import Tag, Member, Band

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
        assigned_only = bool(
            int(self.request.query_params.get('assigned_only', 0))
        )
        queryset = self.queryset
        if assigned_only:
            queryset = queryset.filter(band__isnull=False)

        return queryset.filter(user=self.request.user).order_by('-name')\
            .distinct()

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


class BandViewSet(viewsets.ModelViewSet):
    """
    Manage Bands in the database
    """
    serializer_class = serializers.BandSerializer
    queryset = Band.objects.all()
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def _params_to_ints(self, qs):
        """Convert a list of string IDs to a list of integers"""
        return [int(str_id) for str_id in qs.split(',')]

    def get_queryset(self):
        """
        Retrieve the receepies for the authenticated user
        :return:
        """
        tags = self.request.query_params.get('tags')
        members = self.request.query_params.get('members')
        queryset = self.queryset
        if tags:
            tag_ids = self._params_to_ints(tags)
            queryset = queryset.filter(tags__id__in=tag_ids)
        if members:
            members_ids = self._params_to_ints(members)
            queryset = queryset.filter(members__id__in=members_ids)

        return queryset.filter(user=self.request.user)

    def get_serializer_class(self):
        """
        Return appropriate serializer class
        :return:
        """
        if self.action == 'retrieve':
            return serializers.BandDetailSerializer
        elif self.action == 'upload_image':
            return serializers.BandImageSerializer

        return self.serializer_class

    def perform_create(self, serializer):
        """
        Create a new band
        :param serializer:
        :return:
        """
        serializer.save(user=self.request.user)

    @action(methods=['POST'], detail=True, url_path='upload-image')
    def upload_image(self, request, pk=None):
        """

        Upload an image to a band
        :param request:
        :param pk:
        :return:
        """
        band = self.get_object()
        serializer = self.get_serializer(
            band,
            data=request.data
        )

        if serializer.is_valid():
            serializer.save()
            return Response(
                serializer.data,
                status=status.HTTP_200_OK
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )
