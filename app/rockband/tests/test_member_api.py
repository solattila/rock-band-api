from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Member, Band

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

    def test_create_member_successful(self):
        """
        Test create a new ingredient
        :return:
        """
        payload = {'name': 'Petrucci'}
        self.client.post(MEMBERS_URL, payload)

        exists = Member.objects.filter(
            user=self.user,
            name=payload['name'],
        ).exists()
        self.assertTrue(exists)

    def test_create_member_invalid(self):
        """
        Test creating invalid member fails
        :return:
        """
        payload = {'name': ''}
        res = self.client.post(MEMBERS_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_retrieve_members_assigned_to_bands(self):
        """
        Test filtering members by those assigned to bands
        :return:
        """
        member1 = Member.objects.create(
            user=self.user, name='Joakim'
        )
        member2 = Member.objects.create(
            user=self.user, name='Tony'
        )
        band = Band.objects.create(
            title='Sabaton',
            band_members=5,
            tickets=55.5,
            user=self.user
        )
        band.members.add(member1)

        res = self.client.get(MEMBERS_URL, {'assigned_only': 1})

        serializer1 = MemberSerializer(member1)
        serializer2 = MemberSerializer(member2)
        self.assertIn(serializer1.data, res.data)
        self.assertNotIn(serializer2.data, res.data)

    def Test_retrieve_members_assigned_unique(self):
        """
        Test filtering members by assigned returns unique items
        :return:
        """
        member = Member.objects.create(
            user=self.user, name='Joakim'
        )
        Member.objects.create(
            user=self.user, name='Tony'
        )
        band1 = Band.objects.create(
            title='Sabaton',
            band_members=5,
            tickets=55.5,
            user=self.user
        )
        band1.members.add(member)
        band2 = Band.objects.create(
            title='Sonata',
            band_members=5,
            tickets=45.5,
            user=self.user
        )
        band2.members.add(member)

        res = self.client.get(MEMBERS_URL, {'assigned_only': 1})

        self.assertEqual(len(res.data), 1)
