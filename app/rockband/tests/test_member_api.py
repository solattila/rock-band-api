from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Member

from rockband.serializers import MemberSerializer


MEMBERS_URL = reverse('rockband:member-list')


class PublicMembersApiTests(TestCase):
    """
    Test the publicly available ingredients API
    """

    def setUp(self):
        self.client = APIClient()

    def test_login_required(self):
        """
        Test that login is required to access the endpoint
        :return:
        """
        res = self.client.get(MEMBERS_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateMemberApiTests(TestCase):
    """
    Test the private member API
    """

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            'test@rockbanddev.com',
            'testpass'
        )
        self.client.force_authenticate(self.user)

    def test_retrieve_member_list(self):
        """
        Test retrieving a list of members
        :return:
        """
        Member.objects.create(user=self.user, name='Hendrix')
        Member.objects.create(user=self.user, name='Satriani')

        res = self.client.get(MEMBERS_URL)

        members = Member.objects.all().order_by('-name')
        serializer = MemberSerializer(members, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_members_limited_to_user(self):
        """
        Test that members for the authenticated user are returned
        :return:
        """
        user2 = get_user_model().objects.create_user(
            'other@rockbanddev.com',
            'testpass'
        )
        Member.objects.create(user=user2, name='Lemmy')
        member = Member.objects.create(user=self.user, name='Elvis')

        res = self.client.get(MEMBERS_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['name'], member.name)
